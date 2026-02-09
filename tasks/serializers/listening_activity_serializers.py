from rest_framework import serializers
from tasks.models import (
    ListeningActivity,
    ListeningActivityPart,
    ListeningActivityQuestion
)
from utils.urlsfixer import build_https_url


# ---------------------------------------
# Listening Activity Question Serializer
# ---------------------------------------
class ListeningActivityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningActivityQuestion
        fields = [
            'id',
            'question_type',   # ✅ corrected
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer'
        ]


# ---------------------------------------
# Listening Activity Part Serializer
# ---------------------------------------
class ListeningActivityPartSerializer(serializers.ModelSerializer):
    questions = ListeningActivityQuestionSerializer(
        source='listeningactivityquestion_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = ListeningActivityPart
        fields = [
            'id',
            'part',
            'instruction',
            'audio_file',
            'duration',
            'questions'
        ]


# ---------------------------------------
# ListeningActivity Create/Update
# ---------------------------------------
class ListeningActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningActivity
        fields = [
            'id',
            'task',
            'title',
            'duration',
            'instruction',
            'audio_file'
        ]


# ---------------------------------------
# ListeningActivity List/Retrieve
# ---------------------------------------
class ListeningActivityListSerializer(serializers.ModelSerializer):

    # Nested Parts (instead of questions directly)
    parts = ListeningActivityPartSerializer(
        source='listeningactivitypart_set',
        many=True,
        read_only=True
    )

    # Task as {id, name}
    task = serializers.SerializerMethodField()

    # Full audio file URL
    audio_file = serializers.SerializerMethodField()

    class Meta:
        model = ListeningActivity
        fields = [
            'id',
            'task',
            'title',
            'duration',
            'instruction',
            'audio_file',
            'parts'
        ]

    def get_task(self, obj):
        if obj.task:
            return {
                'id': obj.task.id,
                'name': obj.task.name
            }
        return None

    def get_audio_file(self, obj):
        request = self.context.get('request')
        if obj.audio_file and request:
            return build_https_url(request, obj.audio_file.url)
        elif obj.audio_file:
            return obj.audio_file.url
        return None


# ---------------------------------------
# Dropdown Version (lighter version)
# ---------------------------------------
class ListeningActivityDropdownSerializer(serializers.ModelSerializer):

    parts = ListeningActivityPartSerializer(
        source='listeningactivitypart_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = ListeningActivity
        fields = [
            'id',
            'task',
            'title',
            'duration',
            'instruction',
            'audio_file',
            'parts'
        ]