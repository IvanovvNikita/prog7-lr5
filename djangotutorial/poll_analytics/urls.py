from django.urls import path
from . import views

app_name = 'poll_analytics'

urlpatterns = [
    # Маршруты для статистики
    path("statistics/", views.StatisticsView.as_view(), name="statistics"),
    path("statistics-question-list", views.QuestionView.as_view(), name="statistics-question-list"),
    path('statistics/question-stats/<int:pk>/', views.QuestionStatsAPIView.as_view(), name='statistics-question-stats'),
    path('export/', views.ExportDataView.as_view(), name='export_data'),
]