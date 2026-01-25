from rest_framework import serializers
from cms.models import Videos
from utils.urlsfixer import build_https_url
class VideoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = [
            'video',
            'is_active',
        ]
        
class VideoListSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = Videos
        fields = [
            'id',
            'video',
            'is_active',
            'created_at',
        ]

    def get_video(self, obj):
        request = self.context.get('request')
        if obj.video and request:
            return build_https_url(request, obj.video.url)
        return None