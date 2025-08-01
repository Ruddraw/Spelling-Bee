from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', next_page='home'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('practice/', views.practice, name='practice'),
    path('spelling-practice/', views.spelling_practice, name='spelling_practice'),
    path('profile/', views.profile, name='profile'),
    path('start-session/', views.start_session, name='start_session'),
    path('end-session/', views.end_session, name='end_session'),
]