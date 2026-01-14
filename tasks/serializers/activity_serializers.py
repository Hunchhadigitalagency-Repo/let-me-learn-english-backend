from rest_framework import serializers
from tasks.models import SpeakingActivity, speakingActivitySample
from utils.urlsfixer import build_https_url  # assuming you already have this utility

class SpeakingActivitySerializer(serializers.ModelSerializer):
    samples = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()  # override task to show name

    class Meta:
        model = SpeakingActivity
        fields = ['id', 'task', 'title', 'duration', 'instructions', 'use_default_instruction', 'samples']

    def get_task(self, obj):
        # Return task name instead of id
        return obj.task.name if obj.task else None

    def get_samples(self, obj):
        request = self.context.get('request')  # get request from context
        samples = speakingActivitySample.objects.filter(speaking_activity=obj)
        return [
            {
                'id': sample.id,
                'type': sample.type,
                'sample_question': build_https_url(request, sample.sample_question.url) if sample.sample_question and request else None,
                'sample_answer': build_https_url(request, sample.sample_answer.url) if sample.sample_answer and request else None,
                'sample_text_question': sample.sample_text_question
            }
            for sample in samples
        ]
