from django.db import models

# Create your models here.
from django.utils import timezone
from django.conf import settings
from tasks.models import Task
# Choices for activity_type field
ACTIVITY_CHOICES = [
    ('speaking_activity', 'Speaking Activity'),
    
    ('listening_activity', 'Listening Activity'),
    ('writing_activity', 'Writing Activity'),
    ('reading_activity', 'Reading Activity'),
]

class StudentAttempts(models.Model):
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    activity_type = models.CharField(choices=ACTIVITY_CHOICES,max_length=255)
    score = models.PositiveIntegerField()
    status = models.CharField(max_length=255)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    
    
    
