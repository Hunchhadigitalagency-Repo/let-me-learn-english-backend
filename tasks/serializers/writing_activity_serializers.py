# tasks/serializers/writing_activity_serializers.py
from rest_framework import serializers
from tasks.models import WritingActivity

# --------------------------
# Serializer for Create/Update
# --------------------------
class WritingActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingActivity
        fields = ['id', 'task', 'title', 'duration', 'instruction', 'writing_sample']


# --------------------------
# Serializer for List/Retrieve
# --------------------------
class WritingActivityListSerializer(serializers.ModelSerializer):
    # Show task name instead of id
    task = serializers.SerializerMethodField()

    class Meta:
        model = WritingActivity
        fields = ['id', 'task', 'title', 'duration', 'instruction', 'writing_sample']
        
    def get_task(self, obj):
        if obj.task:
            return {
                'id': obj.task.id,
                'name': obj.task.name
            }
        return None
