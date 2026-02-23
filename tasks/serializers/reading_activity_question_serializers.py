# tasks/serializers/reading_question_serializers.py
from rest_framework import serializers
from tasks.models import ReadingAcitivityQuestion, ReadingActivity

# --------------------------
# Serializer for Create/Update ReadingActivityQuestion
# --------------------------
class ReadingActivityQuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingAcitivityQuestion
        fields = '__all__'


# --------------------------
# Serializer for List/Retrieve ReadingActivityQuestion
# --------------------------
class ReadingActivityQuestionListSerializer(serializers.ModelSerializer):
    # Show reading activity info as {id, title}
    reading_activity = serializers.SerializerMethodField()

    class Meta:
        model = ReadingAcitivityQuestion
        fields = '__all__'

    def get_reading_activity(self, obj):
        if obj.reading_activity:
            return {
                'id': obj.reading_activity.id,
                'title': obj.reading_activity.title
            }
        return None


class ReadingActivityQuestionStudentSerializer(serializers.ModelSerializer):
    # Show reading activity info as {id, title}
    reading_activity = serializers.SerializerMethodField()

    class Meta:
        model = ReadingAcitivityQuestion
        exclude = ['is_correct_answer']

    def get_reading_activity(self, obj):
        if obj.reading_activity:
            return {
                'id': obj.reading_activity.id,
                'title': obj.reading_activity.title
            }
        return None
