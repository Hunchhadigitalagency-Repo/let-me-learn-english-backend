from django.db import models

# Create your models here.
GRADE_CHOICES = [(str(i), str(i)) for i in range(1, 11)]
class Task(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField()
    grade=models.CharField(max_length=255,choices=GRADE_CHOICES)
    
    def __str__(self):
        return self.name
    
    
    
class SpeakingActivity(models.Model):
    task=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    title=models.CharField(max_length=255)
    duration=models.DateTimeField()
    instructions=models.TextField()
    use_default_instruction=models.BooleanField(default=True)
    
    def __str__(self):
        return self.title