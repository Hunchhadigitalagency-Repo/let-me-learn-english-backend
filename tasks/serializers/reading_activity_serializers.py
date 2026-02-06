# tasks/serializers/reading_serializers.py
from rest_framework import serializers
from tasks.models import ReadingActivity
from utils.urlsfixer import build_https_url  # if needed for any URLs
from tasks.serializers.reading_activity_question_serializers import ReadingActivityQuestionListSerializer
# --------------------------
# Serializer for Create/Update ReadingActivity
# --------------------------
class ReadingActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingActivity
        fields = '__all__'


# --------------------------
# Serializer for List/Retrieve ReadingActivity
# --------------------------
class ReadingActivityListSerializer(serializers.ModelSerializer):
    # show task as {id, name}
    task = serializers.SerializerMethodField()

    class Meta:
        model = ReadingActivity
        fields = '__all__'

    def get_task(self, obj):
        if obj.task:
            return {
                'id': obj.task.id,
                'name': obj.task.name
            }
        return None
    
    
    
class ReadingActivityDropdownSerializer(serializers.ModelSerializer):
    questions = ReadingActivityQuestionListSerializer(
        source='readingacitivityquestion_set',  
        many=True,
        read_only=True
    )
    
    class Meta:
        model = ReadingActivity
        fields = '__all__'
