from django.contrib import admin
from django.urls import include, path
from polls import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("polls/", include("polls.urls")),
    path('', views.home, name='home'),
    path("admin/", admin.site.urls),
    path('login/', views.login_view, name='login'),  # Используем стандартное представление для входа
    path('logout/', views.logout_view, name='logout'),  # Стандартное представление для выхода
    path('register/', views.register, name='register'),
    path("", include("allauth.urls")),  # Подключаем маршруты allauth для OAuth
    path('poll-analytics/', include('poll_analytics.urls')),
]