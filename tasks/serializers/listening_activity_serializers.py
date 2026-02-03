# serializers.py
from rest_framework import serializers
from tasks.models import ListeningActivity, ListeningActivityQuestion
from tasks.models import Task  # To get task name
from utils.urlsfixer import build_https_url
from tasks.serializers.listening_activity_question_serializers import ListeningActivityQuestionListSerializer
# --------------------------
# ListeningActivityQuestion Serializer
# --------------------------
class ListeningActivityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningActivityQuestion
        fields = ['id', 'type', 'question', 'answer_1', 'answer_2', 'answer_3', 'answer_4', 'is_correct_answer']


# --------------------------
# ListeningActivity Serializer for Create/Update
# --------------------------
class ListeningActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningActivity
        fields = ['id', 'task', 'title', 'duration', 'instruction', 'audio_file']


# --------------------------
# ListeningActivity Serializer for Retrieve/List
# --------------------------
# --------------------------
# ListeningActivity Serializer for Retrieve/List
# --------------------------
class ListeningActivityListSerializer(serializers.ModelSerializer):
    # nested questions
    questions = ListeningActivityQuestionSerializer(many=True, read_only=True, source='listeningactivityquestion_set')

    # task as {id, name}
    task = serializers.SerializerMethodField()

    # full URL for audio_file
    audio_file = serializers.SerializerMethodField()

    class Meta:
        model = ListeningActivity
        fields = ['id', 'task', 'title', 'duration', 'instruction', 'audio_file', 'questions']

    # Return task as {id, name}
    def get_task(self, obj):
        if obj.task:
            return {
                'id': obj.task.id,
                'name': obj.task.name
            }
        return None

    # Return full URL for audio file
    def get_audio_file(self, obj):
        request = self.context.get('request')
        if obj.audio_file and request:
            return build_https_url(request, obj.audio_file.url)
        elif obj.audio_file:
            return obj.audio_file.url
        return None



class ListeningActivityDropdownSerializer(serializers.ModelSerializer):
    questions = ListeningActivityQuestionListSerializer(
        source='listeningactivityquestion_set',  # NO space here
        many=True,
        read_only=True
    )
    
    class Meta:
        model = ListeningActivity
        fields = ['id', 'task', 'title', 'duration', 'instruction', 'audio_file', 'questions']