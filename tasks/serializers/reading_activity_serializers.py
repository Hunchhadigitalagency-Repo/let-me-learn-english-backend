# tasks/serializers/reading_serializers.py
from rest_framework import serializers
from tasks.models import ReadingActivity

class ReadingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingActivity
        fields = [
            'id',
            'title',
            'duration',
            'passage',
            'task'
        ]
