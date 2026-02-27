from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

import random
import string
from PIL import Image

from user.serializers.school_serializers import SchoolBasicSerializer
from utils.urlsfixer import build_https_url
from user.models import UserProfile, School
from school.models import Subscription                                          # updated
from school.serializers.subscriptions_serializers import SubscriptionHistoryListSerializer

User = get_user_model()


# ─────────────────────────────────────────
# Basic
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# User (used in login / token responses)
# ─────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    school_subscription = serializers.SerializerMethodField()   # single object — was school_subscriptions list
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "is_active", "profile", "date_joined", "school_subscription",
        )
        read_only_fields = ("id", "date_joined")

    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)

            if profile.profile_picture:
                avatar_url = self.context["request"].build_absolute_uri(profile.profile_picture.url)
            elif profile.google_avatar:
                avatar_url = profile.google_avatar
            else:
                avatar_url = "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-icon-of-social-media-user-vector.jpg"

            return {
                "bio": profile.bio,
                "profile_picture": avatar_url,
                "display_name": profile.display_name,
                "phone_number": profile.phone_number,
                "address": profile.address,
                "user_type": profile.user_type,
                "is_verified": profile.is_verified,
                "is_disabled": profile.is_disabled,
                "is_deleted": profile.is_deleted,
                "google_id": profile.google_id,
                "google_avatar": profile.google_avatar,
            }

        except UserProfile.DoesNotExist:
            return None

    def get_school_subscription(self, obj):
        """
        Returns the single active subscription for the user's school.
        None if the school has no subscription yet.
        """
        school = School.objects.filter(user=obj).first()
        if not school:
            return None

        try:
            subscription = Subscription.objects.prefetch_related("logs").get(school=school)
        except Subscription.DoesNotExist:
            return None

        return SubscriptionHistoryListSerializer(subscription, context=self.context).data


# ─────────────────────────────────────────
# Profile Update
# ─────────────────────────────────────────

class UserProfileGetSerializer(serializers.ModelSerializer):
    school = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'bio', 'profile_picture', 'display_name', 'phone_number',
            'address', 'user_type', 'is_verified', 'is_disabled', 'is_deleted',
            'google_id', 'google_avatar', 'is_active', 'grade', 'section',
            'dateofbirth', 'student_parent_name', 'student_parent_email',
            'student_parent_phone_number',
            'school'
        ]

    def get_school(self, obj):
        if obj.user_type == 'school':
            try:
                # assuming a OneToOneField from School to User
                school = obj.user.school
                return SchoolBasicSerializer(school).data
            except School.DoesNotExist:
                return None
        return None
    

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = UserProfile
        fields = [
            "bio", "email", "profile_picture", "phone_number",
            "first_name", "last_name", "address", "is_verified", "display_name",
            "google_id", "google_avatar", "password",
            "student_parent_name", "student_parent_email", "student_parent_phone_number",
            "section", "grade",
        ]
        read_only_fields = ["is_verified"]

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
        request = self.context.get("request")
        if obj.profile_picture:
            return build_https_url(request, obj.profile_picture.url)
        return None

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        user = instance.user

        if "first_name" in user_data:
            user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            user.last_name = user_data["last_name"]
        if "password" in validated_data:
            user.password = make_password(validated_data.pop("password"))
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


# ─────────────────────────────────────────
# Profile Read
# ─────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user_id", "username", "email", "first_name", "last_name",
            "bio", "profile_picture", "google_avatar", "phone_number",
            "address", "user_type", "display_name",
        ]


# ─────────────────────────────────────────
# Change Password
# ─────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True, write_only=True,
        style={"input_type": "password"},
        help_text="Current password of the user"
    )
    new_password = serializers.CharField(
        required=True, write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
        help_text="New password following password policy"
    )
    confirm_new_password = serializers.CharField(
        required=True, write_only=True,
        style={"input_type": "password"},
        help_text="Must match the new password"
    )

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "New passwords must match."})
        return data


# ─────────────────────────────────────────
# Register (school self-registration)
# ─────────────────────────────────────────

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
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        user = User(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.password = make_password(validated_data["password"])
        user.save()

        UserProfile.objects.create(user=user, user_type="school")

        return user


# ─────────────────────────────────────────
# Admin Register
# ─────────────────────────────────────────

class AdminRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    bio = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    google_id = serializers.CharField(required=False, allow_blank=True)
    google_avatar = serializers.URLField(required=False, allow_blank=True)
    display_name = serializers.CharField(required=False, allow_blank=True)
    user_type = serializers.ChoiceField(
        choices=[("superadmin", "SuperAdmin"), ("admin", "Admin"), ("user", "User")],
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
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        email = validated_data.pop("email")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        password = validated_data.pop("password")

        user = User(username=email, email=email, first_name=first_name, last_name=last_name)
        user.password = make_password(password)
        user.save()

        profile_fields = [
            "bio", "profile_picture", "google_id", "google_avatar",
            "display_name", "user_type", "address", "phone_number", "is_verified",
        ]
        profile_data = {k: validated_data[k] for k in profile_fields if k in validated_data}
        profile_data.setdefault("user_type", "admin")

        UserProfile.objects.create(user=user, **profile_data)

        return UserSerializer(user, context=self.context).data


# ─────────────────────────────────────────
# User Upsert (admin bulk create/update)
# ─────────────────────────────────────────

class UserUpsertSerializer(serializers.ModelSerializer):
    # ---- User fields ----
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    login_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    # ---- Profile fields ----
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    display_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user_type = serializers.ChoiceField(
        choices=[("superadmin", "superadmin"), ("admin", "admin"), ("parent", "parent"), ("student", "student"), ("school", "school")],
        required=False, allow_null=True
    )
    is_verified = serializers.BooleanField(required=False)
    is_disabled = serializers.BooleanField(required=False)
    is_deleted = serializers.BooleanField(required=False)
    google_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    google_avatar = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dateofbirth = serializers.DateTimeField(required=False, allow_null=True)
    student_parent_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    student_parent_email = serializers.EmailField(required=False, allow_null=True)
    student_parent_phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name", "is_active", "login_code", "name", "password",
            "bio", "profile_picture", "display_name", "phone_number", "address", "user_type",
            "is_verified", "is_disabled", "is_deleted",
            "google_id", "google_avatar",
            "grade", "section", "dateofbirth",
            "student_parent_name", "student_parent_email", "student_parent_phone_number",
        ]
        read_only_fields = ["id"]

    _PROFILE_FIELDS = {
        "bio", "profile_picture", "display_name", "phone_number", "address", "user_type",
        "is_verified", "is_disabled", "is_deleted",
        "google_id", "google_avatar",
        "grade", "section", "dateofbirth",
        "student_parent_name", "student_parent_email", "student_parent_phone_number",
    }

    def validate(self, attrs):
        if self.instance is None and not attrs.get("email"):
            raise serializers.ValidationError({"email": "email is required"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        profile_fields = {k: validated_data.pop(k) for k in list(validated_data) if k in self._PROFILE_FIELDS}

        email = validated_data.get("email")
        if not validated_data.get("username"):
            validated_data["username"] = email

        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])

        UserProfile.objects.create(user=user, **profile_fields)
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        profile_data = {k: validated_data.pop(k) for k in list(validated_data) if k in self._PROFILE_FIELDS}

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()

        profile, _ = UserProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance