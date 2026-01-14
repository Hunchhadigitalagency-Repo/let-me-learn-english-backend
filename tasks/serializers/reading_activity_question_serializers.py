# tasks/serializers/reading_question_serializers.py
from rest_framework import serializers
from tasks.models import ReadingAcitivityQuestion, ReadingActivity

class ReadingActivityQuestionSerializer(serializers.ModelSerializer):
    # Show the reading activity title in the response
    reading_activity = serializers.CharField(source='reading_activity.title', read_only=True)
    
    # Allow sending reading_activity_id for create/update
    reading_activity_id = serializers.PrimaryKeyRelatedField(
        queryset=ReadingActivity.objects.all(),
        source='reading_activity',
        write_only=True
    )

    class Meta:
        model = ReadingAcitivityQuestion
        fields = [
            'id',
            'reading_activity',      # read-only title
            'reading_activity_id',   # write-only ID for POST/PATCH
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer',
            'type',
        ]
