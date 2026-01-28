from django.db import models

# Create your models here.
class InstructionTemplate(models.Model):
    speaking_instruction=models.TextField(blank=False, null=False)
    listening_instruction=models.TextField(blank=False, null=False)
    writing_instruction=models.TextField(blank=False, null=False)
    reading_instruction=models.TextField(blank=False, null=False)
       
    def __str__(self):
        return self.speaking_instruction