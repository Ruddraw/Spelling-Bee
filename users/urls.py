from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # Updated to use custom_logout
    path('practice/', views.practice, name='practice'),
    path('spelling-practice/', views.spelling_practice, name='spelling_practice'),
    path('profile/', views.profile, name='profile'),
    path('practice-history/', views.practice_history, name='practice_history'),
]