from django.db import models
from django.utils import timezone

# Create your models here.
GRADE_CHOICES = [(str(i), str(i)) for i in range(1, 11)]
class Task(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField()
    grade=models.CharField(max_length=255,choices=GRADE_CHOICES)
    status=models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.name
    
    
class SpeakingActivity(models.Model):
    task=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    title=models.CharField(max_length=255)
    duration=models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)

    instructions=models.TextField()
    use_default_instruction=models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
SPEAKING_CHOICES = [
    ('part1', 'Part 1'),
    ('extended_question', 'Extended Question')
]
class speakingActivitySample(models.Model):
    speaking_activity=models.ForeignKey(SpeakingActivity,on_delete=models.CASCADE,null=True,blank=True)
    type=models.CharField(max_length=255,choices=SPEAKING_CHOICES)
    sample_question=models.FileField(upload_to='samplequestion/',null=True,blank=True)
    sample_answer=models.FileField(upload_to='sampleanswer/',null=True,blank=True)
    sample_text_question=models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return f"{self.speaking_activity}"
    
    
class SpeakingActivityQuestion(models.Model):
    speaking_activity=models.ForeignKey(SpeakingActivity,on_delete=models.CASCADE,null=True,blank=True)
    type=models.CharField(max_length=255,choices=SPEAKING_CHOICES)
    attachment=models.FileField(upload_to='question_attachment/',null=True,blank=True)
    durations=models.DecimalField(max_digits=5, decimal_places=2)   
    text_question=models.CharField(max_length=255,null=True,blank=True) 
    
    def __str__(self):
        return f"{self.speaking_activity}"
    
    
class ReadingActivity(models.Model):
    title=models.CharField(max_length=255)
    duration=models.DecimalField(max_digits=5,decimal_places=2)
    passage=models.TextField()
    task=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    
    def __str__(self):
        return self.title
    
READ_TYPE=[
    ('true_false','True_False'),
    ('mcq','MCQ'),
    ('note_completion','NoteCompletion'),
    ('sentence_Completion','SentenceCompletion'),
    ('summary_completion','SummaryCompletion')
]

class ReadingAcitivityQuestion(models.Model):
    reading_activity=models.ForeignKey(ReadingActivity,on_delete=models.CASCADE,null=True,blank=True)
    question=models.CharField(max_length=255)
    answer_1=models.CharField(max_length=255)
    answer_2=models.CharField(max_length=255)
    answer_3=models.CharField(max_length=255)
    answer_4=models.CharField(max_length=255)
    is_correct_answer=models.CharField(max_length=255)
    type=models.CharField(max_length=255,choices=READ_TYPE)
    
    
    
class ListeningActivity(models.Model):
    task=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    title=models.CharField(max_length=255)
    duration=models.DecimalField(max_digits=5, decimal_places=2)
    instruction=models.TextField()
    audio_file=models.FileField(upload_to='listening_file/',null=True,blank=True)
    
    
    def __str__(self):
        return self.title
    
LISTENING_CHOICES=[
    ('part1','part1'),
    ('form_question','form_question')
]   
    
class ListeningActivityQuestion(models.Model):
    listening_activity=models.ForeignKey(ListeningActivity,on_delete=models.CASCADE,null=True,blank=True)
    type=models.CharField(max_length=255,choices=LISTENING_CHOICES)
    question=models.CharField(max_length=255)
    answer_1=models.CharField(max_length=255)
    answer_2=models.CharField(max_length=255)
    answer_3=models.CharField(max_length=255)
    answer_4=models.CharField(max_length=255)
    is_correct_answer=models.CharField(max_length=255)
    
    
    def __str__(self):
        return self.question
    
    
    
class WritingActivity(models.Model):
    task=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    title=models.CharField(max_length=255)
    duration=models.DecimalField(max_digits=5, decimal_places=2)
    instruction=models.TextField()
    writing_sample=models.CharField(max_length=255)
    
    
    def __str__(self):
        return self.title
    
    
    
    
