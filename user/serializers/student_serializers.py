from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.models import UserProfile, Parent, SchoolStudentParent, School
from utils.urlsfixer import build_https_url
import random
import string

User = get_user_model()


# ===============================
# STUDENT REGISTER SERIALIZER
# ===============================

class StudentRegisterSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    grade = serializers.CharField(required=False)
    section = serializers.CharField(required=False)
    dateofbirth = serializers.DateField(required=False)

    # Parent fields (stored in Parent model)
    student_parent_name = serializers.CharField(required=False)
    student_parent_phone_number = serializers.CharField(required=False)
    student_parent_email = serializers.EmailField(required=False)

    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = [
            "name", "email",
            "profile_picture", "phone_number", "address",
            "grade", "section", "dateofbirth",
            "student_parent_name",
            "student_parent_phone_number",
            "student_parent_email"
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        school_user = request.user

        # Extract parent data
        parent_name = validated_data.pop("student_parent_name", None)
        parent_email = validated_data.pop("student_parent_email", None)
        parent_phone = validated_data.pop("student_parent_phone_number", None)

        # Generate login code
        login_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Auto-generate email if not provided
        email = validated_data.get("email")
        if not email:
            email = f"{validated_data['name'].replace(' ', '').lower()}{random.randint(1000,9999)}@students.local"

        # Create student user
        student_user = User.objects.create(
            name=validated_data["name"],
            email=email,
            login_code=login_code,
            username=validated_data["name"].replace(" ", "").lower() + str(random.randint(1000, 9999)),
        )

        # Create UserProfile
        UserProfile.objects.create(
            user=student_user,
            display_name=validated_data["name"],
            profile_picture=validated_data.get("profile_picture"),
            phone_number=validated_data.get("phone_number"),
            address=validated_data.get("address"),
            grade=validated_data.get("grade"),
            section=validated_data.get("section"),
            dateofbirth=validated_data.get("dateofbirth"),
            user_type="student",
        )

        # Create Parent record (Non-registered parent)
        if parent_name or parent_email:
            Parent.objects.create(
                student=student_user,
                name=parent_name,
                email=parent_email,
                phone_number=parent_phone,
                code=''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            )

        # Link student to school
        school_instance = School.objects.filter(user=school_user).first()
        if school_instance:
            SchoolStudentParent.objects.create(
                student=student_user,
                school=school_instance
            )

        return student_user


# ===============================
# STUDENT LOGIN SERIALIZER
# ===============================

class StudentLoginSerializer(serializers.Serializer):
    login_code = serializers.CharField(max_length=6)


# ===============================
# STUDENT RESPONSE SERIALIZER
# ===============================

class StudentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'login_code']


# ===============================
# STUDENT EDIT SERIALIZER
# ===============================

class StudentEditSerializer(serializers.ModelSerializer):

    profile_picture = serializers.ImageField(required=False)
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    grade = serializers.CharField(required=False)
    section = serializers.CharField(required=False)
    dateofbirth = serializers.DateField(required=False)

    student_parent_name = serializers.CharField(required=False)
    student_parent_phone_number = serializers.CharField(required=False)
    student_parent_email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = [
            "name", "email",
            "profile_picture", "phone_number", "address",
            "grade", "section", "dateofbirth",
            "student_parent_name",
            "student_parent_phone_number",
            "student_parent_email"
        ]
        extra_kwargs = {
            "email": {"required": False},
            "name": {"required": False}
        }

    def update(self, instance, validated_data):

        # Update User
        instance.name = validated_data.get("name", instance.name)
        instance.email = validated_data.get("email", instance.email)
        instance.save()

        # Update Profile
        profile = UserProfile.objects.filter(user=instance).first()
        if profile:
            profile.profile_picture = validated_data.get("profile_picture", profile.profile_picture)
            profile.phone_number = validated_data.get("phone_number", profile.phone_number)
            profile.address = validated_data.get("address", profile.address)
            profile.grade = validated_data.get("grade", profile.grade)
            profile.section = validated_data.get("section", profile.section)
            profile.dateofbirth = validated_data.get("dateofbirth", profile.dateofbirth)
            profile.save()

        # Update Parent
        parent = Parent.objects.filter(student=instance).first()
        if parent:
            parent.name = validated_data.get("student_parent_name", parent.name)
            parent.phone_number = validated_data.get("student_parent_phone_number", parent.phone_number)
            parent.email = validated_data.get("student_parent_email", parent.email)
            parent.save()

        return instance


# ===============================
# STUDENT READ SERIALIZER
# ===============================

class StudentReadSerializer(serializers.ModelSerializer):

    profile_picture = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='userprofile.phone_number', read_only=True)
    address = serializers.CharField(source='userprofile.address', read_only=True)
    grade = serializers.CharField(source='userprofile.grade', read_only=True)
    section = serializers.CharField(source='userprofile.section', read_only=True)
    dateofbirth = serializers.DateTimeField(source='userprofile.dateofbirth', read_only=True)

    student_parent_name = serializers.SerializerMethodField()
    student_parent_phone_number = serializers.SerializerMethodField()
    student_parent_email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'login_code',
            'profile_picture', 'phone_number', 'address',
            'grade', 'section', 'dateofbirth',
            'student_parent_name',
            'student_parent_phone_number',
            'student_parent_email'
        ]
        read_only_fields = ['login_code']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        profile = getattr(obj, 'userprofile', None)

        if profile and profile.profile_picture:
            if request:
                return build_https_url(request, profile.profile_picture.url)
            return profile.profile_picture.url
        return None

    def get_student_parent_name(self, obj):
        parent = Parent.objects.filter(student=obj).first()
        return parent.name if parent else None

    def get_student_parent_phone_number(self, obj):
        parent = Parent.objects.filter(student=obj).first()
        return parent.phone_number if parent else None

    def get_student_parent_email(self, obj):
        parent = Parent.objects.filter(student=obj).first()
        return parent.email if parent else None