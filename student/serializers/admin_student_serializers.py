from rest_framework import serializers
from user.models import User, UserProfile
from utils.urlsfixer import build_https_url
class StudentSerializer(serializers.ModelSerializer):
    name = serializers.CharField( read_only=True)  # User's name
    grade = serializers.CharField(source='userprofile.grade', read_only=True)
    section = serializers.CharField(source='userprofile.section', read_only=True)
    address = serializers.CharField(source='userprofile.address', read_only=True)
    profile_picture = serializers.SerializerMethodField()
    is_active = serializers.BooleanField( read_only=True)
    is_published=serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'grade', 'section', 'address', 'profile_picture', 'is_active','is_published']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'userprofile') and obj.userprofile.profile_picture:
            if request:
                return build_https_url(request,obj.userprofile.profile_picture.url)
            return obj.userprofile.profile_picture.url
        return None
