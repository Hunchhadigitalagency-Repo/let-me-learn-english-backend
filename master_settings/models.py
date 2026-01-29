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
    
    
    created_at = models.DateTimeField(auto_now_add=True,null=True)  # Add this
    
    updated_at = models.DateTimeField(auto_now=True,null=True)   
    
    
    def __str__(self):
        return self.topic

