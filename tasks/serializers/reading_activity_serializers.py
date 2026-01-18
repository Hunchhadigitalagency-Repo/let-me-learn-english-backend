# tasks/serializers/reading_serializers.py
from rest_framework import serializers
from tasks.models import ReadingActivity
from utils.urlsfixer import build_https_url  # if needed for any URLs

# --------------------------
# Serializer for Create/Update ReadingActivity
# --------------------------
class ReadingActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingActivity
        fields = [
            'id',
            'task',       # pass task as ID
            'title',
            'duration',
            'passage'
        ]


# --------------------------
# Serializer for List/Retrieve ReadingActivity
# --------------------------
class ReadingActivityListSerializer(serializers.ModelSerializer):
    # show task as {id, name}
    task = serializers.SerializerMethodField()

    class Meta:
        model = ReadingActivity
        fields = [
            'id',
            'task',
            'title',
            'duration',
            'passage'
        ]

    def get_task(self, obj):
        if obj.task:
            return {
                'id': obj.task.id,
                'name': obj.task.name
            }
        return None
