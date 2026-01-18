# serializers/listening_question_serializers.py
from rest_framework import serializers
from tasks.models import ListeningActivityQuestion, ListeningActivity
from utils.urlsfixer import build_https_url

# --------------------------
# Serializer for creating/updating a ListeningActivityQuestion
# --------------------------
class ListeningActivityQuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningActivityQuestion
        fields = [
            'id', 
            'listening_activity',  
            'type', 
            'question', 
            'answer_1', 
            'answer_2', 
            'answer_3', 
            'answer_4', 
            'is_correct_answer'
        ]


# --------------------------
# Serializer for listing/retrieving a ListeningActivityQuestion
# --------------------------
class ListeningActivityQuestionListSerializer(serializers.ModelSerializer):
   
    listening_activity = serializers.SerializerMethodField()

    class Meta:
        model = ListeningActivityQuestion
        fields = [
            'id', 
            'listening_activity',  
            'type', 
            'question', 
            'answer_1', 
            'answer_2', 
            'answer_3', 
            'answer_4', 
            'is_correct_answer'
        ]

    
    def get_listening_activity(self, obj):
        if obj.listening_activity:
            return {
                'id': obj.listening_activity.id,
                'title': obj.listening_activity.title,
                # 'audio_file': build_https_url(self.context.get('request'), obj.listening_activity.audio_file.url) 
                #               if obj.listening_activity.audio_file else None
            }
        return None
