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


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'description']  


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  

# List serializer with nested fields
class StudentAttemptsListSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    task = TaskSerializer(read_only=True)

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
