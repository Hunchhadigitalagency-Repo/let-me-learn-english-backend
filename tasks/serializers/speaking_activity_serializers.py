# tasks/serializers/speaking_activity_serializers.py
from rest_framework import serializers
from tasks.models import SpeakingActivity, speakingActivitySample
from utils.urlsfixer import build_https_url
from tasks.serializers.speaking_activity_question_serializers import SpeakingActivityQuestionListSerializer
# --------------------------
# Serializer for Create/Update SpeakingActivity
# --------------------------
class SpeakingActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingActivity
        fields = [
            'id',
            'task',  
            'title',
            'duration',
            'instructions',
            'use_default_instruction'
        ]


# --------------------------
# Serializer for List/Retrieve SpeakingActivity
# --------------------------
class SpeakingActivityListSerializer(serializers.ModelSerializer):
    samples = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()  # show task name
    duration = serializers.SerializerMethodField()

    class Meta:
        model = SpeakingActivity
        fields = [
            'id',
            'task',
            'title',
            'duration',
            'instructions',
            'use_default_instruction',
            'samples'
        ]

    def get_task(self, obj):
        if obj.task:
            return {
                'id': obj.task.id,
                'name': obj.task.name
            }
        return None
    def get_duration(self, obj):
        return float(obj.duration) if obj.duration is not None else None

    def get_samples(self, obj):
        request = self.context.get('request')
        samples = speakingActivitySample.objects.filter(speaking_activity=obj)
        return [
            {
                'id': sample.id,
                'type': sample.type,
                'sample_question': build_https_url(request, sample.sample_question.url) if sample.sample_question else None,
                'sample_answer': build_https_url(request, sample.sample_answer.url) if sample.sample_answer else None,
                'sample_text_question': sample.sample_text_question
            }
            for sample in samples
        ]



class SpeakingActivityDropdownSerializer(serializers.ModelSerializer):
    questions = SpeakingActivityQuestionListSerializer(
        source='speakingactivityquestion_set',  
        many=True,
        read_only=True
    )
    
    class Meta:
        model = SpeakingActivity
        fields = ['id', 'title', 'duration', 'instructions', 'use_default_instruction', 'questions']
