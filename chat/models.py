# chat/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    input_sheet_link = models.URLField()
    price_list_json = models.JSONField()  # CHANGED: Use models.JSONField instead
    output_sheet_link = models.URLField(blank=True)
    # chat/models.py (inside Project class)
    status_choices = (('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'))
    status = models.CharField(max_length=20, choices=status_choices, default='pending')

class ChatSession(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='active')

class Message(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    sender = models.CharField(max_length=50)  # 'user' or 'bot'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class AnalysisStep(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    step_type = models.CharField(max_length=50)  # 'ai' or 'code'
    input_data = models.TextField()
    output_data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=Project)
def create_chat_session(sender, instance, created, **kwargs):
    if created:
        ChatSession.objects.get_or_create(project=instance, status='active')