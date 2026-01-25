from rest_framework import serializers
from user.models import  UserProfile

from rest_framework import serializers
from user.models import User
from rest_framework import serializers
from user.models import User, UserProfile
import random
from utils.urlsfixer import build_https_url
import string
from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.models import UserProfile
from django.core.mail import send_mail
import random, string
from django.conf import settings
from user.models import SchoolStudentParent,School
User = get_user_model()
class StudentProfileSerializer(serializers.Serializer):
    profile_picture = serializers.ImageField(required=False)
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    grade = serializers.CharField(required=False)
    section = serializers.CharField(required=False)
    dateofbirth = serializers.DateTimeField(required=False)
    student_parent_name = serializers.CharField(required=False)
    student_parent_phone_number = serializers.CharField(required=False)
    student_parent_email = serializers.EmailField(required=False)

class StudentRegisterSerializer(serializers.ModelSerializer):
    # Flatten all profile fields (works with multipart/form-data)
    profile_picture = serializers.ImageField(required=False)
    phone_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    grade = serializers.CharField(required=False)
    section = serializers.CharField(required=False)
    dateofbirth = serializers.DateField(required=False)
    student_parent_name = serializers.CharField(required=False)
    student_parent_phone_number = serializers.CharField(required=False)
    student_parent_email = serializers.EmailField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = [
            "name", "email", "profile_picture", "phone_number", "address", "grade", 
            "section", "dateofbirth", "student_parent_name", "student_parent_phone_number",
            "student_parent_email"
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        school_user = request.user 
        # Extract parent info
        parent_name = validated_data.pop("student_parent_name", None)
        parent_email = validated_data.pop("student_parent_email", None)
        parent_phone = validated_data.pop("student_parent_phone_number", None)

        # Generate student login code
        login_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Generate email if not provided
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

        # Create student profile
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
            student_parent_name=parent_name,
            student_parent_phone_number=parent_phone,
            student_parent_email=parent_email
        )

        # Create parent user & profile if info provided
        if parent_name and parent_email:
            parent_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            parent_user = User.objects.create(
                name=parent_name,
                email=parent_email,
                username=parent_email.split("@")[0] + str(random.randint(1000, 9999)),
            )
            parent_user.set_password(parent_password)
            parent_user.save()

            # Parent profile
            UserProfile.objects.create(
                user=parent_user,
                display_name=parent_name,
                phone_number=parent_phone,
                user_type="parent"
            )
            
            if parent_user:
           
            # The logged-in school creating the student

            # Later, get the School instance of this user
                school_instance = School.objects.filter(user=school_user).first()
                if school_instance:
                    SchoolStudentParent.objects.create(
                        student=student_user,
                        parent=parent_user,
                        school=school_instance
                    )

        return student_user

   

class StudentLoginSerializer(serializers.Serializer):
    login_code = serializers.CharField(max_length=6)

class StudentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'login_code']


from rest_framework import serializers
from user.models import User, UserProfile, SchoolStudentParent, School

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
            "name", "email", "profile_picture", "phone_number", "address", "grade",
            "section", "dateofbirth", "student_parent_name", "student_parent_phone_number",
            "student_parent_email"
        ]
        extra_kwargs = {
            "email": {"required": False},
            "name": {"required": False}
        }

    def update(self, instance, validated_data):
        
        instance.name = validated_data.get("name", instance.name)
        instance.email = validated_data.get("email", instance.email)
        instance.save()

       
        profile = UserProfile.objects.filter(user=instance).first()
        if profile:
            profile.profile_picture = validated_data.get("profile_picture", profile.profile_picture)
            profile.phone_number = validated_data.get("phone_number", profile.phone_number)
            profile.address = validated_data.get("address", profile.address)
            profile.grade = validated_data.get("grade", profile.grade)
            profile.section = validated_data.get("section", profile.section)
            profile.dateofbirth = validated_data.get("dateofbirth", profile.dateofbirth)
            profile.student_parent_name = validated_data.get("student_parent_name", profile.student_parent_name)
            profile.student_parent_phone_number = validated_data.get("student_parent_phone_number", profile.student_parent_phone_number)
            profile.student_parent_email = validated_data.get("student_parent_email", profile.student_parent_email)
            profile.save()

        return instance



class StudentReadSerializer(serializers.ModelSerializer):
    # Nested profile fields
    profile_picture = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='userprofile.phone_number', read_only=True)
    address = serializers.CharField(source='userprofile.address', read_only=True)
    grade = serializers.CharField(source='userprofile.grade', read_only=True)
    section = serializers.CharField(source='userprofile.section', read_only=True)
    dateofbirth = serializers.DateTimeField(source='userprofile.dateofbirth', read_only=True)

    student_parent_name = serializers.CharField(source='userprofile.student_parent_name', read_only=True)
    student_parent_phone_number = serializers.CharField(source='userprofile.student_parent_phone_number', read_only=True)
    student_parent_email = serializers.CharField(source='userprofile.student_parent_email', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'login_code', 
            'profile_picture', 'phone_number', 'address', 'grade', 'section',
            'dateofbirth', 'student_parent_name', 'student_parent_phone_number', 'student_parent_email'
        ]
        read_only_fields = ['login_code']
        
        
    def get_profile_picture(self, obj):
        request = self.context.get('request')
        profile = getattr(obj, 'userprofile', None)

        if profile and profile.profile_picture:
            if request:
                return build_https_url(request,profile.profile_picture.url)
            return profile.profile_picture.url

        return None