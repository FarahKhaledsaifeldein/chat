
# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Project, Message, ChatSession
from django.contrib import messages
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']

@login_required
# chat/views.py


def project_list(request):
    if request.user.is_authenticated:
        return redirect('chat')
    
    return render(request, '../templates/project_list.html', {'projects': projects, 'form': form})

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('chat')
            else:
                messages.error(request, "Signup failed. Please try again.")
    else:
        form = SignupForm()
    return render(request, '../templates/signup.html', {'form': form})

@login_required
def chat_view(request):
    project = Project.objects.filter(user=request.user).order_by('-id').first()
    if not project:
        project = Project.objects.create(user=request.user, name="Default Project")
        ChatSession.objects.get_or_create(project=project, status='active')
    if 'project_id' in request.GET:
        project = get_object_or_404(Project, id=request.GET['project_id'], user=request.user)
    messages = Message.objects.filter(chat_session__project=project).order_by('timestamp')
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            ChatSession.objects.get_or_create(project=project, status='active')
            messages.success(request, f"Project '{project.name}' created!")
            return redirect('chat')
    else:
        form = ProjectForm()
    return render(request, '../templates/chat.html', {'project': project, 'messages': messages, 'projects': Project.models.Project.objects.filter(user=request.user), 'form': form})
