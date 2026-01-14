from rest_framework import serializers




from user.models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
import random
from django.contrib.auth.hashers import make_password 
import string
from PIL import Image
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from utils.urlsfixer import build_https_url
from django.contrib.auth import get_user_model


User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]
        extra_kwargs = {
            "email": {"write_only": True, "required": True},
            "username": {"write_only": True, "required": True},
            "password": {"write_only": True, "required": True},
            "date_joined": {"write_only": True, "required": False},
        }
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with UserProfile data.
    """
    profile = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'profile', 'date_joined'
        )
        read_only_fields = ('id', 'date_joined')

    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            # First check if there's a profile picture
            if profile.profile_picture:
                avatar_url = self.context['request'].build_absolute_uri(profile.profile_picture.url)
            # If no profile picture, use google avatar if available
            elif profile.google_avatar:
                avatar_url = profile.google_avatar
            # If neither exists, use default avatar
            else:
                avatar_url = "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-icon-of-social-media-user-vector.jpg"
            return {
                "bio": profile.bio,
                "profile_picture": avatar_url,
                "user_type": profile.user_type,
                "address": profile.address
            }
        except UserProfile.DoesNotExist:
            return None
        
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    
    email = serializers.SerializerMethodField(read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = UserProfile
        fields = [
             'bio', 'email', 'profile_picture', 'phone_number',
            'first_name', 'last_name', 'address', 'is_verified', 'display_name',
            'google_id', 'google_avatar','password','student_parent_name','student_parent_email','student_parent_phone_number','section','grade'
        ]
        read_only_fields = [ 'is_verified']

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    def validate_profile_picture(self, value):
        if not value:
            return value

        max_size_mb = 10
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Profile picture size should not exceed {max_size_mb} MB.")

        return value

    

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            # Use your utility to build HTTPS URL
            return build_https_url(request, obj.profile_picture.url)
        return None




    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Update User fields if present
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        if 'password' in validated_data:
            user.password = make_password(validated_data.pop('password'))
        user.save()

        # Update only incoming UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance



class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
             'user_id','username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture','google_avatar' ,'phone_number',
            'address', 'user_type', 'display_name'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "New passwords must match."})
        return data




class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        email = validated_data['email']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        password = validated_data['password']

        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.password = make_password(password)
        user.save()

        
        UserProfile.objects.create(user=user,user_type="admin")

       
        serializer = UserSerializer(user,context=self.context)

        return serializer.data
    
class AdminRegisterSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    # Optional UserProfile fields
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    google_id = serializers.CharField(required=False, allow_blank=True)
    google_avatar = serializers.URLField(required=False, allow_blank=True)
    display_name = serializers.CharField(required=False, allow_blank=True)
    user_type = serializers.ChoiceField(
        choices=[('superadmin','SuperAdmin'),('admin', 'Admin'), ('user', 'User')],
        required=False
    )
    address = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    is_verified = serializers.BooleanField(required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        # Extract user fields
        email = validated_data.pop('email')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        password = validated_data.pop('password')

        # Create User
        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.password = make_password(password)
        user.save()

        # Only take the UserProfile fields that are present in validated_data
        profile_fields = [
            'bio', 'profile_picture', 'google_id', 'google_avatar',
            'display_name', 'user_type', 'address', 'phone_number', 'is_verified'
        ]
        profile_data = {key: validated_data[key] for key in profile_fields if key in validated_data}

        # If user_type not sent, default to 'admin'
        profile_data.setdefault('user_type', 'admin')

        UserProfile.objects.create(user=user, **profile_data)

        # Return serialized user
        serializer = UserSerializer(user, context=self.context)
        return serializer.data


