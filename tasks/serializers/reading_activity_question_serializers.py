# tasks/serializers/reading_question_serializers.py
from rest_framework import serializers
from tasks.models import ReadingAcitivityQuestion, ReadingActivity

# --------------------------
# Serializer for Create/Update ReadingActivityQuestion
# --------------------------
class ReadingActivityQuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingAcitivityQuestion
        fields = [
            'id',
            'reading_activity',  
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer',
            'type',
        ]


# --------------------------
# Serializer for List/Retrieve ReadingActivityQuestion
# --------------------------
class ReadingActivityQuestionListSerializer(serializers.ModelSerializer):
    # Show reading activity info as {id, title}
    reading_activity = serializers.SerializerMethodField()

    class Meta:
        model = ReadingAcitivityQuestion
        fields = [
            'id',
            'reading_activity',  # full info
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer',
            'type',
        ]

    def get_reading_activity(self, obj):
        if obj.reading_activity:
            return {
                'id': obj.reading_activity.id,
                'title': obj.reading_activity.title
            }
        return None
