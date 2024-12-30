from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Question, Choice

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput, required=True)
    email = forms.EmailField(label="Электронная почта", widget=forms.EmailInput)

    class Meta:
        model = User
        fields = ['username', 'email']  # Поля: имя пользователя и email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже зарегистрирован.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))

class QuestionForm(forms.ModelForm):
    choices = forms.CharField(
        label='Варианты ответа',
        widget=forms.Textarea(attrs={'rows': 7}),
        help_text='Введите варианты ответов, разделяя каждый вариант новой строкой.'
    )

    class Meta:
        model = Question
        fields = ['question_text', 'choices']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            choices = '\n'.join(self.instance.choice_set.values_list('choice_text', flat=True))
            self.initial['choices'] = choices

    def clean_choices(self):
        choices = self.cleaned_data.get('choices')
        if choices:
            # Разбить строки по переносу строки и удалить пустые элементы
            choices_list = [choice.strip() for choice in choices.split('\n') if choice.strip()]
            
            # Проверить, чтобы было хотя бы два варианта ответа
            if len(choices_list) < 2:
                raise forms.ValidationError('Введите хотя бы два варианта ответа.')
            
            return choices_list

        return []
    
    def save(self, commit=True):
        question_instance = super().save(commit=False)
        if not question_instance.pub_date:
            question_instance.pub_date = timezone.now()
        question_instance.save()

        # Удалить старые варианты ответов и добавить новые
        Choice.objects.filter(question=question_instance).delete()

        choices = self.cleaned_data.get('choices')
        if choices:
            for choice_text in choices:
                Choice.objects.create(question=question_instance, choice_text=choice_text)

        return question_instance