from rest_framework import serializers
from tasks.models import SpeakingActivityQuestion, SpeakingActivity
from utils.urlsfixer import build_https_url
class SpeakingActivityQuestionSerializer(serializers.ModelSerializer):
    
    speaking_activity = serializers.CharField(read_only=True)
    speaking_activity_id = serializers.PrimaryKeyRelatedField(
        queryset=SpeakingActivity.objects.all(),
        source='speaking_activity',  
        write_only=True  
    )
    

    attachment = serializers.FileField(write_only=True, required=False)
    attachment_url = serializers.SerializerMethodField()  # read-only URL

    class Meta:
        model = SpeakingActivityQuestion
        fields = [
            'id',
            'speaking_activity',
            'type',
            'attachment',        
            'attachment_url',    
            'durations',
            'text_question',
            'speaking_activity_id'
        ]
        
    def get_speaking_activity(self, obj):
        return obj.speaking_activity.name if obj.speaking_activity else None
       

    def get_attachment_url(self, obj):
        request = self.context.get('request')
        if obj.attachment and request:
            return build_https_url(request,obj.attachment.url)
        return None
