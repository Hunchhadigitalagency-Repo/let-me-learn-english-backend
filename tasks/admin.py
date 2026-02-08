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
    WritingActivity,
    StudentSpeakingAttempt,
    StudentSpeakingAnswer,
    StudentReadingAttempt,
    StudentReadingAnswer,
    StudentListeningAttempt,
    StudentListeningAnswer,
    StudentWritingAttempt,
    StudentWritingAnswer,
    UserTaskProgress
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
    search_fields = ['text_question', 'instruction']
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

# ----------------------
# Student Speaking Attempt Admin
# ----------------------
@admin.register(StudentSpeakingAttempt)
class StudentSpeakingAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'speaking_activity', 'is_completed', 'started_at', 'completed_at']
    search_fields = ['student__username', 'speaking_activity__title']
    list_filter = ['is_completed', 'speaking_activity']

# ----------------------
# Student Speaking Answer Admin
# ----------------------
@admin.register(StudentSpeakingAnswer)
class StudentSpeakingAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'attempt', 'question', 'created_at']
    search_fields = ['attempt__student__username', 'question__text_question']
    list_filter = ['question']

# ----------------------
# Student Reading Attempt Admin
# ----------------------
@admin.register(StudentReadingAttempt)
class StudentReadingAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'reading_activity', 'is_completed', 'started_at', 'completed_at', 'score']
    search_fields = ['student__username', 'reading_activity__title']
    list_filter = ['is_completed', 'reading_activity']

# ----------------------
# Student Reading Answer Admin
# ----------------------
@admin.register(StudentReadingAnswer)
class StudentReadingAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'attempt', 'question', 'selected_answer', 'is_correct']
    search_fields = ['attempt__student__username', 'question__question']
    list_filter = ['is_correct', 'question']

# ----------------------
# Student Listening Attempt Admin
# ----------------------
@admin.register(StudentListeningAttempt)
class StudentListeningAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'listening_activity', 'is_completed', 'started_at', 'completed_at', 'score']
    search_fields = ['student__username', 'listening_activity__title']
    list_filter = ['is_completed', 'listening_activity']

# ----------------------
# Student Listening Answer Admin
# ----------------------
@admin.register(StudentListeningAnswer)
class StudentListeningAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'attempt', 'question', 'selected_answer', 'is_correct']
    search_fields = ['attempt__student__username', 'question__question']
    list_filter = ['is_correct', 'question']

# ----------------------
# Student Writing Attempt Admin
# ----------------------
@admin.register(StudentWritingAttempt)
class StudentWritingAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'writing_activity', 'is_completed', 'started_at', 'completed_at', 'score']
    search_fields = ['student__username', 'writing_activity__title']
    list_filter = ['is_completed', 'writing_activity']

# ----------------------
# Student Writing Answer Admin
# ----------------------
@admin.register(StudentWritingAnswer)
class StudentWritingAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'attempt', 'created_at']
    search_fields = ['attempt__student__username', 'submission_text']
    list_filter = ['attempt']

# ----------------------
# User Task Progress Admin
# ----------------------
@admin.register(UserTaskProgress)
class UserTaskProgressAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_id', 'task', 
        'did_completed_speaking_activity',
        'did_completed_reading_activity',
        'did_completed_listening_activity',
        'did_completed_writing_activity',
        'last_updated'
    ]
    list_filter = [
        'did_completed_speaking_activity',
        'did_completed_reading_activity',
        'did_completed_listening_activity',
        'did_completed_writing_activity',
        'task'
    ]
    search_fields = ['user_id', 'task__name']