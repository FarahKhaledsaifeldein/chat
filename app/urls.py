# app/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from chat.views import chat_view, signup_view

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='chat/login.html', redirect_authenticated_user=True, next_page='/chat/'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', signup_view, name='signup'),
    path('chat/', chat_view, name='chat'),
]