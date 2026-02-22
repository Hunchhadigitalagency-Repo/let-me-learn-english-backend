from rest_framework import serializers
from student.models import StudentAttempts
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentAttemptsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttempts
        fields = ['task', 'student', 'activity_type', 'score', 'status', 'started_at', 'submitted_at']
        read_only_fields = ['started_at']  # these are auto-managed

    # Optional: validate score
    def validate_score(self, value):
        if value < 0:
            raise serializers.ValidationError("Score cannot be negative.")
        return value


from rest_framework import serializers
from student.models import StudentAttempts
from django.contrib.auth import get_user_model
from tasks.models import Task  
User = get_user_model()


class StudentAttemptTaskSerializer(serializers.ModelSerializer):
    speaking_activity_ids = serializers.SerializerMethodField()
    reading_activity_ids = serializers.SerializerMethodField()
    listening_activity_ids = serializers.SerializerMethodField()
    writing_activity_ids = serializers.SerializerMethodField()
    from tasks.models import SpeakingActivity, ReadingActivity, ListeningActivity, WritingActivity

    class Meta:
        model = Task
        fields = [
            'id',
            'name',
            'description',
            'grade',
            'speaking_activity_ids',
            'reading_activity_ids',
            'listening_activity_ids',
            'writing_activity_ids'
        ]

    def get_speaking_activity_ids(self, obj):
        return list(
            SpeakingActivity.objects.filter(task=obj).values_list('id', flat=True)
        )

    def get_reading_activity_ids(self, obj):
        return list(
            ReadingActivity.objects.filter(task=obj).values_list('id', flat=True)
        )

    def get_listening_activity_ids(self, obj):
        return list(
            ListeningActivity.objects.filter(task=obj).values_list('id', flat=True)
        )

    def get_writing_activity_ids(self, obj):
        return list(
            WritingActivity.objects.filter(task=obj).values_list('id', flat=True)
        )


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  

# List serializer with nested fields
class StudentAttemptsListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    task = StudentAttemptTaskSerializer(read_only=True)

    class Meta:
        model = StudentAttempts
        fields = [
            'id',
            'task',
            'student',
            'activity_type',
            'score',
            'status',
            'started_at',
            'submitted_at'
        ]
