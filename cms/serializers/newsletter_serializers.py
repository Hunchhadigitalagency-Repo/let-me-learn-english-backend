from rest_framework import serializers
from cms.models import Newsletters
from user.models import User  # assuming your custom user model is here
from user.models import User

# Nested user serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']  # Include any other fields you need
class NewsletterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletters
        fields = [
            'subject_header',
            'message',
            'users',
            'is_active'
        ]
        extra_kwargs = {
            'users': {'required': False}
        }


class NewsletterListSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True)  # shows usernames/emails

    class Meta:
        model = Newsletters
        fields = [
            'id',
            'subject_header',
            'message',
            'users',
            'is_active'
        ]
        read_only_fields = ['id']
