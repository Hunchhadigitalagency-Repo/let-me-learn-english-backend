from django.db import models

# Create your models here.
class InstructionTemplate(models.Model):
    speaking_instruction=models.TextField(blank=False, null=False)
    listening_instruction=models.TextField(blank=False, null=False)
    writing_instruction=models.TextField(blank=False, null=False)
    reading_instruction=models.TextField(blank=False, null=False)
       
    def __str__(self):
        return self.speaking_instruction
    
    
    
class PrivacyPolicy(models.Model):
    topic = models.CharField(max_length=255)
    effective_date = models.DateTimeField()
    description = models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
   

    def __str__(self):
        return self.topic
    
    
class TermsandConditions(models.Model):
    topic=models.CharField(max_length=255)
    description= models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    effective_date=models.DateTimeField(null=True,blank=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True,null=True)  # Add this
    
    updated_at = models.DateTimeField(auto_now=True,null=True)   
    
    
    def __str__(self):
        return self.topic
from user.models import School
class ExamPause(models.Model):
    school = models.ForeignKey(
        School,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    grade = models.CharField(max_length=50,null=True,blank=True)
    mark_all_grade = models.BooleanField(default=True)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return f"Exam Pause ({self.grade})"