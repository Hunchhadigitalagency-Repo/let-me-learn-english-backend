from django.db import models
from django.utils import timezone

from user.models import User
import uuid

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
    instruction=models.CharField(max_length=255, blank=True, null=True)
    title=models.CharField(max_length=255)
    duration=models.CharField(max_length=255,null=True,blank=True)
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
    instruction=models.CharField(max_length=255, blank=True, null=True)
    type=models.CharField(max_length=255,choices=SPEAKING_CHOICES)
    attachment=models.FileField(upload_to='question_attachment/',null=True,blank=True)
    durations=models.CharField(max_length=255,null=True,blank=True)   
    text_question=models.CharField(max_length=255,null=True,blank=True) 
    instructions=models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return f"{self.speaking_activity}"
    
class StudentSpeakingAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    speaking_activity = models.ForeignKey(SpeakingActivity, on_delete=models.CASCADE)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.speaking_activity}"

class StudentSpeakingAnswer(models.Model):
    attempt = models.ForeignKey(
        StudentSpeakingAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        SpeakingActivityQuestion,
        on_delete=models.CASCADE
    )

    audio_file = models.FileField(upload_to="student_speaking/")
    transcript = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('attempt', 'question')
    
    
class ReadingActivity(models.Model):
    title=models.CharField(max_length=255)
    duration=models.CharField(max_length=255,null=True,blank=True)
    passage=models.TextField()
    instruction=models.TextField(blank=True,null=True)
    task=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    file = models.FileField(upload_to='reading_passage/', null=True, blank=True)
    
    def __str__(self):
        return self.title
    
READ_TYPE=[
    ('true_false','True_False'),
    ('mcq','MCQ'),
    ('note_completion','NoteCompletion'),
    ('sentence_completion','SentenceCompletion'),
    ('summary_completion','SummaryCompletion')
]

class ReadingAcitivityQuestion(models.Model):
    reading_activity=models.ForeignKey(ReadingActivity,on_delete=models.CASCADE,null=True,blank=True)
    instruction=models.CharField(max_length=255, blank=True, null=True)
    bundle_id = models.UUIDField(default=uuid.uuid4, editable=False)
    question=models.CharField(max_length=255)
    answer_1=models.CharField(max_length=255, blank=True, null=True)
    answer_2=models.CharField(max_length=255, blank=True, null=True)
    answer_3=models.CharField(max_length=255, blank=True, null=True)
    answer_4=models.CharField(max_length=255, blank=True, null=True)
    is_correct_answer=models.CharField(max_length=255)
    type=models.CharField(max_length=255,choices=READ_TYPE)
    
class StudentReadingAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    reading_activity = models.ForeignKey(ReadingActivity, on_delete=models.CASCADE)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    score = models.FloatField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.reading_activity}"
    
class StudentReadingAnswer(models.Model):
    attempt = models.ForeignKey(
        StudentReadingAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        ReadingAcitivityQuestion,
        on_delete=models.CASCADE
    )

    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')
    
class ListeningActivity(models.Model):
    task=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    title=models.CharField(max_length=255)
    duration=models.CharField(max_length=255, null=True, blank=True)
    instruction=models.TextField()
    audio_file=models.FileField(upload_to='listening_file/',null=True,blank=True)
    
    
    def __str__(self):
        return self.title
    

LISTENING_PART_CHOICES=[
    ('Part1-Conversation ','Part1-Conversation'),
    ('Part2-Talk ','Part2-Talk'),
    ('Part3-Lecture ','Part3-Lecture '),
] 
LISTENING_QUESTION_TYPE_CHOICES=[
    ('matching_info','Matching_info'),
    ('mcq','Mcq'),
    ('note_completion','Note_completion'),
]
class ListeningActivityPart(models.Model):
    listening_activity=models.ForeignKey(ListeningActivity,on_delete=models.CASCADE,null=True,blank=True)
    part=models.CharField(max_length=255,choices=LISTENING_PART_CHOICES)
    audio_file=models.FileField(upload_to='listening_part_file/',null=True,blank=True)
    instruction=models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.listening_activity} - {self.part}"
    
class ListeningActivityQuestion(models.Model):
    listening_activity_part=models.ForeignKey(ListeningActivityPart,on_delete=models.CASCADE,null=True,blank=True)
    question_type = models.CharField(max_length=255,choices=LISTENING_QUESTION_TYPE_CHOICES, blank=True, null=True)
    bundle_id = models.UUIDField(default=uuid.uuid4, editable=False)
    question=models.CharField(max_length=255)
    answer_1=models.CharField(max_length=255)
    answer_2=models.CharField(max_length=255)
    answer_3=models.CharField(max_length=255)
    answer_4=models.CharField(max_length=255)
    is_correct_answer=models.CharField(max_length=255)
    
    
    def __str__(self):
        return self.question
    
class StudentListeningAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    listening_activity = models.ForeignKey(ListeningActivity, on_delete=models.CASCADE)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    score = models.FloatField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.listening_activity}"

class StudentListeningAnswer(models.Model):
    attempt = models.ForeignKey(
        StudentListeningAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(
        ListeningActivityQuestion,
        on_delete=models.CASCADE
    )

    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')
    
class WritingActivity(models.Model):
    task=models.ForeignKey(Task,on_delete=models.CASCADE,null=True,blank=True)
    title=models.TextField(null=True,blank=True)
    duration=models.CharField(max_length=255,null=True,blank=True)
    instruction=models.TextField()
    writing_sample=models.TextField(null=True,blank=True)
    issue=models.TextField(null=True,blank=True)
    
    
    def __str__(self):
        return self.title

class StudentWritingAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    writing_activity = models.ForeignKey(WritingActivity, on_delete=models.CASCADE)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.writing_activity}"

class StudentWritingAnswer(models.Model):
    attempt = models.ForeignKey(
        StudentWritingAttempt,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    submission_text = models.TextField()
    file = models.FileField(upload_to="student_writing/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
class UserTaskProgress(models.Model):
    user_id = models.IntegerField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    did_completed_speaking_activity = models.BooleanField(default=False)
    did_completed_reading_activity = models.BooleanField(default=False)
    did_completed_listening_activity = models.BooleanField(default=False)
    did_completed_writing_activity = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user_id} - Task {self.task.name} - Progress {self.progress}%"
