# tasks/serializers/activity_sample_serializers.py
from rest_framework import serializers
from tasks.models import speakingActivitySample, SpeakingActivity
from utils.urlsfixer import build_https_url
class SpeakingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingActivity
        fields = ['id', 'title', 'instructions', 'use_default_instruction', 'duration', 'task']

class SpeakingActivitySampleSerializer(serializers.ModelSerializer):
    speaking_activity = SpeakingActivitySerializer(read_only=True)
    speaking_activity_id = serializers.PrimaryKeyRelatedField(
        queryset=SpeakingActivity.objects.all(),
        source='speaking_activity',  
        write_only=True  
    )

    sample_question = serializers.SerializerMethodField()
    sample_answer = serializers.SerializerMethodField()

    class Meta:
        model = speakingActivitySample
        fields = ['id', 'speaking_activity', 'type', 'sample_question', 'sample_answer', 'sample_text_question','speaking_activity_id']

    # This will convert file paths to full URLs
    def get_sample_question(self, obj):
        request = self.context.get('request')
        if obj.sample_question and request:
            return build_https_url(request,obj.sample_question.url)
        return None

    def get_sample_answer(self, obj):
        request = self.context.get('request')
        if obj.sample_answer and request:
            return build_https_url(request,obj.sample_answer.url)
        return None
