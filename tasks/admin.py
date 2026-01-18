from django.contrib import admin

# Register your models here.
# tasks/admin.py
from django.contrib import admin
from .models import (
    Task,
    SpeakingActivity,
    speakingActivitySample,
    SpeakingActivityQuestion,
    ReadingActivity,
    ReadingAcitivityQuestion,
    ListeningActivity,
    ListeningActivityQuestion,
    WritingActivity
)

# ----------------------
# Task Admin
# ----------------------
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'grade']
    search_fields = ['name', 'description']
    list_filter = ['grade']

# ----------------------
# Speaking Activity Admin
# ----------------------
@admin.register(SpeakingActivity)
class SpeakingActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'task', 'duration', 'use_default_instruction']
    search_fields = ['title', 'instructions']
    list_filter = ['task', 'use_default_instruction']

# ----------------------
# Speaking Activity Sample Admin
# ----------------------
@admin.register(speakingActivitySample)
class SpeakingActivitySampleAdmin(admin.ModelAdmin):
    list_display = ['id', 'speaking_activity', 'type', 'sample_text_question']
    search_fields = ['sample_text_question']
    list_filter = ['type', 'speaking_activity']

# ----------------------
# Speaking Activity Question Admin
# ----------------------
@admin.register(SpeakingActivityQuestion)
class SpeakingActivityQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'speaking_activity', 'type', 'durations']
    search_fields = ['text_question']
    list_filter = ['type', 'speaking_activity']

# ----------------------
# Reading Activity Admin
# ----------------------
@admin.register(ReadingActivity)
class ReadingActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'task', 'duration']
    search_fields = ['title', 'passage']
    list_filter = ['task']

# ----------------------
# Reading Activity Question Admin
# ----------------------
@admin.register(ReadingAcitivityQuestion)
class ReadingAcitivityQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'reading_activity', 'type', 'question']
    search_fields = ['question']
    list_filter = ['type', 'reading_activity']

# ----------------------
# Listening Activity Admin
# ----------------------
@admin.register(ListeningActivity)
class ListeningActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'task', 'duration']
    search_fields = ['title', 'instruction']
    list_filter = ['task']

# ----------------------
# Listening Activity Question Admin
# ----------------------
@admin.register(ListeningActivityQuestion)
class ListeningActivityQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'listening_activity', 'type', 'question']
    search_fields = ['question']
    list_filter = ['type', 'listening_activity']

# ----------------------
# Writing Activity Admin
# ----------------------
@admin.register(WritingActivity)
class WritingActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'task', 'duration']
    search_fields = ['title', 'instruction', 'writing_sample']
    list_filter = ['task']
