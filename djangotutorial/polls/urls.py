from django.urls import path
from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('register/', views.register, name='register'),
    path('create/', views.create_question, name='create_question'),  # Проверка прав доступа в представлении
    path('<int:pk>/edit/', views.edit_question, name='edit_question'),  # Проверка прав доступа в представлении
]