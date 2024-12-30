from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .forms import CustomUserCreationForm, CustomAuthenticationForm, QuestionForm
from .models import Choice, Question

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    
def home(request):
    context = {
        'user': request.user, 
        'is_authenticated': request.user.is_authenticated  # Проверяем, авторизован ли пользователь
    }
    return render(request, 'polls/home.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя
            user = form.save()
            # Логиним пользователя сразу после регистрации
            login(request, user)
            # Сообщение об успешной регистрации
            messages.success(request, 'Вы успешно зарегистрированы и вошли в систему!')
            return redirect('home')  # Перенаправляем на главную страницу
        else:
            messages.error(request, 'Произошла ошибка при регистрации. Проверьте введенные данные.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'polls/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Получаем данные из формы
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Авторизуем пользователя
                login(request, user)
                # Сообщение об успешной авторизации
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('home')  # Перенаправление на главную страницу после успешного входа
            else:
                messages.error(request, 'Неверные учетные данные')  # Ошибка авторизации
        else:
            messages.error(request, 'Ошибка при авторизации')

    else:
        form = CustomAuthenticationForm()

    return render(request, 'polls/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')

# Декоратор для проверки прав администратора
def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Опрос успешно создан!')
            return redirect('polls:index')
        else:
            messages.error(request, 'Произошла ошибка при создании опроса.')
    else:
        form = QuestionForm()

    return render(request, 'polls/create_question.html', {'form': form})

@user_passes_test(is_staff)
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Опрос успешно обновлен!')
            return redirect('polls:index')
        else:
            messages.error(request, 'Произошла ошибка при редактировании опроса.')
    else:
        form = QuestionForm(instance=question)

    return render(request, 'polls/edit_question.html', {'form': form, 'question': question})