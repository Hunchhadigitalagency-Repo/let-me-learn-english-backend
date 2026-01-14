from rest_framework import serializers
from tasks.models import Task, SpeakingActivity, speakingActivitySample
from utils.urlsfixer import build_https_url  # your utility to make full URLs

# Serializer for Sample
class SpeakingActivitySampleSerializer(serializers.ModelSerializer):
    sample_question = serializers.SerializerMethodField()
    sample_answer = serializers.SerializerMethodField()

    class Meta:
        model = speakingActivitySample
        fields = '__all__'

    def get_sample_question(self, obj):
        request = self.context.get('request')
        if obj.sample_question and request:
            return build_https_url(request, obj.sample_question.url)
        return None

    def get_sample_answer(self, obj):
        request = self.context.get('request')
        if obj.sample_answer and request:
            return build_https_url(request, obj.sample_answer.url)
        return None


# Serializer for Speaking Activity
class SpeakingActivitySerializer(serializers.ModelSerializer):
    samples = SpeakingActivitySampleSerializer(
        many=True,
        read_only=True,
        source='speakingactivitysample_set',
        # Pass context to nested serializer so URLs can be full
    )

    class Meta:
        model = SpeakingActivity
        fields = ['id', 'task', 'title', 'duration', 'instructions', 'use_default_instruction', 'samples']

    # Ensure nested serializer gets context
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['samples'] = SpeakingActivitySampleSerializer(
            instance.speakingactivitysample_set.all(),
            many=True,
            context=self.context
        ).data
        return rep


# Serializer for Task
class TaskSerializer(serializers.ModelSerializer):
    speaking_activities = SpeakingActivitySerializer(
        many=True,
        read_only=True,
        source='speakingactivity_set'
    )

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'grade', 'speaking_activities']

    # Ensure nested serializer gets context
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['speaking_activities'] = SpeakingActivitySerializer(
            instance.speakingactivity_set.all(),
            many=True,
            context=self.context
        ).data
        return rep
