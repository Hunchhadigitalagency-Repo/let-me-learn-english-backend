# tasks/serializers/activity_sample_serializers.py
from rest_framework import serializers
from tasks.models import speakingActivitySample, SpeakingActivity
from utils.urlsfixer import build_https_url

# --------------------------
# Serializer for Create/Update speakingActivitySample
# --------------------------
class SpeakingActivitySampleCreateSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = speakingActivitySample
        fields = [
            'id',
            'speaking_activity',
            'type',
            'sample_question',
            'sample_answer',
            'sample_text_question'
        ]


# --------------------------
# Serializer for List/Retrieve speakingActivitySample
# --------------------------
class SpeakingActivitySampleListSerializer(serializers.ModelSerializer):
    speaking_activity = serializers.SerializerMethodField()  # nested task info
    sample_question = serializers.SerializerMethodField()
    sample_answer = serializers.SerializerMethodField()

    class Meta:
        model = speakingActivitySample
        fields = [
            'id',
            'speaking_activity',
            'type',
            'sample_question',
            'sample_answer',
            'sample_text_question'
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

    def get_sample_question(self, obj):
        request = self.context.get('request')
        if obj.sample_question:
            return build_https_url(request, obj.sample_question.url) if request else obj.sample_question.url
        return None

    def get_sample_answer(self, obj):
        request = self.context.get('request')
        if obj.sample_answer:
            return build_https_url(request, obj.sample_answer.url) if request else obj.sample_answer.url
        return None
