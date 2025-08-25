from django.contrib import admin

# Register your models here.
# chat/admin.py
from django.contrib import admin
from .models import Project, ChatSession, Message, AnalysisStep
# chat/admin.py
from django.contrib.admin import ModelAdmin, register, TabularInline

class ChatSessionInline(TabularInline):
    model = ChatSession
    extra = 1
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    # chat/admin.py (inside ProjectAdmin class)
    list_display = ('id', 'name', 'user', 'input_sheet_link', 'output_sheet_link', 'status')
    list_filter = ('user', 'status')
    search_fields = ('name', 'input_sheet_link')
    inlines = [ChatSessionInline]

    # chat/admin.py (inside ProjectAdmin class)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['input_sheet_link'].widget.attrs['placeholder'] = 'Enter a valid Google Sheet URL'
        form.base_fields['price_list_json'].widget.attrs['placeholder'] = 'Enter JSON like {"item1": 10.0}'
        return form

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'created_at', 'status')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_session', 'sender', 'timestamp')
    list_filter = ('sender',)
    search_fields = ('content',)

@admin.register(AnalysisStep)
class AnalysisStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'step_type', 'timestamp')
    list_filter = ('step_type',)