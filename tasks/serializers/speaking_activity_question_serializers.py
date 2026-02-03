# tasks/serializers/activity_question_serializers.py
from rest_framework import serializers
from tasks.models import SpeakingActivityQuestion, SpeakingActivity
from utils.urlsfixer import build_https_url

# --------------------------
# Create/Update Serializer
# --------------------------
class SpeakingActivityQuestionCreateSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = SpeakingActivityQuestion
        fields = [
            'id',
            'speaking_activity',
            'type',
            'attachment',
            'durations',
            'text_question',
            'instructions'
        ]


# --------------------------
# List/Retrieve Serializer
# --------------------------
class SpeakingActivityQuestionListSerializer(serializers.ModelSerializer):
    speaking_activity = serializers.SerializerMethodField()  # show name instead of id
    attachment_url = serializers.SerializerMethodField()      # full HTTPS URL for attachment

    class Meta:
        model = SpeakingActivityQuestion
        fields = [
            'id',
            'speaking_activity',
            'type',
            'attachment_url',
            'durations',
            'text_question',
            'instructions'
        ]

    def get_speaking_activity(self, obj):
        return {
            'id': obj.speaking_activity.id if obj.speaking_activity else None,
            'title': obj.speaking_activity.title if obj.speaking_activity else None,
            # 'duration': str(obj.speaking_activity.duration) if obj.speaking_activity else None,
            # 'instructions': obj.speaking_activity.instructions if obj.speaking_activity else None,
            # 'use_default_instruction': obj.speaking_activity.use_default_instruction if obj.speaking_activity else None,
            # 'task': obj.speaking_activity.task.name if obj.speaking_activity and obj.speaking_activity.task else None
        }

    def get_attachment_url(self, obj):
        request = self.context.get('request')
        if obj.attachment and request:
            return build_https_url(request, obj.attachment.url)
        elif obj.attachment:
            return obj.attachment.url
        return None
