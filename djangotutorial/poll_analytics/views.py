import plotly.graph_objects as go
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from polls.models import Question, Choice
from .serializers import QuestionSerializer, ChoiceSerializer
from django.db.models import Sum
import plotly.io as pio
from django.shortcuts import render
from django.views.generic import TemplateView

class StatisticsView(TemplateView):
    template_name = "poll_analytics/statistics.html"

# Представление для получения списка всех вопросов
class QuestionView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


# Представление для получения статистики по конкретному вопросу
class QuestionStatsAPIView(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        choices = question.choice_set.all()
        total_votes = choices.aggregate(Sum('votes'))['votes__sum'] or 0
        
        choices_data = []
        labels = []
        votes = []
        
        for choice in choices:
            labels.append(choice.choice_text)
            votes.append(choice.votes)
            if total_votes > 0:
                percentage = (choice.votes / total_votes) * 100
            else:
                percentage = 0

            choices_data.append({
                'choice_text': choice.choice_text,
                'votes': choice.votes,
                'percentage': round(percentage, 2)
            })

        # Создаем столбчатую диаграмму с помощью Plotly
        fig = go.Figure(data=[go.Bar(x=labels, y=votes)])
        fig.update_layout(
            title=f"Question: {question.question_text}",
            xaxis_title="Choices",
            yaxis_title="Votes",
            template="plotly_white"
        )

        # Генерация SVG
        svg_image = pio.to_image(fig, format='svg')

        # Выбор самого популярного и наименее популярного выбора
        most_popular_choice = max(choices_data, key=lambda c: c['votes'], default={'choice_text': 'N/A'})
        least_popular_choice = min(choices_data, key=lambda c: c['votes'], default={'choice_text': 'N/A'})

        response_data = {
            'question_text': question.question_text,
            'total_votes': total_votes,
            'choices': choices_data,
            'most_popular_choice': most_popular_choice['choice_text'],
            'least_popular_choice': least_popular_choice['choice_text'],
            'histogram_svg': svg_image.decode('utf-8')  # Возвращаем SVG как строку
        }
        
        return Response(response_data)

# Представление для голосования за выбранный вариант ответа
class VoteView(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            choice = Choice.objects.get(pk=pk)
        except Choice.DoesNotExist:
            return Response({"error": "Choice not found"}, status=status.HTTP_404_NOT_FOUND)

        choice.votes += 1
        choice.save()

        return Response({
            "message": "Vote registered successfully",
            "choice": choice.choice_text,
            "votes": choice.votes
        })

# Представление для фильтрации вопросов по дате публикации
class QuestionFilterByDateView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.get('publication-dates', {})
        from_date = data.get('from', None)
        to_date = data.get('to', None)

        if not from_date or not to_date:
            return Response({"error": "Both 'from' and 'to' dates must be provided"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            from_date_parsed = timezone.datetime.strptime(from_date, '%Y-%m-%d')
            to_date_parsed = timezone.datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid date format. Expected format: YYYY-MM-DD"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Фильтрация вопросов по дате публикации
        filtered_questions = Question.objects.filter(pub_date__range=[from_date_parsed, to_date_parsed])

        if not filtered_questions.exists():
            return Response({"message": "No questions found in the given date range"},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = QuestionSerializer(filtered_questions, many=True)
        return Response({"questions": serializer.data})
