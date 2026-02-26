from rest_framework import serializers
from user.models import School
from rest_framework import serializers
from django.db import transaction
from user.models import User,UserProfile,School
from utils.urlsfixer import build_https_url

from django.utils import timezone

class SchoolRegistrationSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
   
    school_name = serializers.CharField(source='name',required=False)

    class Meta:
        model = School
        fields = ['email', 'password', 'school_name', 'establish_date']

    def create(self, validated_data):
        with transaction.atomic():
          
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                username=validated_data['email'] 
            )
            
            UserProfile.objects.create(user=user, user_type='school')
            
          
            
                
            
            return user
        
        
from rest_framework import serializers
from django.db import transaction
from user.models import School, User, UserProfile, Country, Province, District, FocalPerson


class FocalPersonSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    designation = serializers.CharField(required=True)

class SchoolCreateSerializer(serializers.ModelSerializer):
   
    country_id = serializers.IntegerField(write_only=True, required=False)
    province_id = serializers.IntegerField(write_only=True, required=False)
    district_id = serializers.IntegerField(write_only=True, required=False)

   
    focal_name = serializers.CharField(write_only=True, required=True)
    focal_email = serializers.EmailField(write_only=True, required=True)
    focal_phone = serializers.CharField(write_only=True, required=True)
    focal_designation = serializers.CharField(write_only=True, required=True)

   
    logo_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    focal_person = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'establish_date',
            'landline',
            'email',
            'city',
            'address',
            'logo',
            'logo_url',
            'country_id',
            'province_id',
            'district_id',
            'country',
            'province',
            'district',
            "code",
            'focal_name',
            'focal_email',
            'focal_phone',
            'focal_designation',
            'focal_person',
        ]
        extra_kwargs = {'logo': {'write_only': True}}

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user

        focal_data = {
            'name': validated_data.pop('focal_name'),
            'email': validated_data.pop('focal_email'),
            'phone': validated_data.pop('focal_phone'),
            'designation': validated_data.pop('focal_designation')
        }

        with transaction.atomic():
            
            country = Country.objects.get(id=validated_data.pop('country_id')) if validated_data.get('country_id') else None
            province = Province.objects.get(id=validated_data.pop('province_id')) if validated_data.get('province_id') else None
            district = District.objects.get(id=validated_data.pop('district_id')) if validated_data.get('district_id') else None

            
            school = School.objects.create(
                user=user,
                country=country,
                province=province,
                district=district,
                **validated_data
            )

            # Create focal person
            FocalPerson.objects.create(
                school=school,
                **focal_data
            )

        return school

    # ------------------ Output fields ------------------
    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo:
            return build_https_url(request, obj.logo.url)
        return None

    def get_country(self, obj):
        return obj.country.name if obj.country else None

    def get_province(self, obj):
        return obj.province.name if obj.province else None

    def get_district(self, obj):
        return obj.district.name if obj.district else None

    def get_focal_person(self, obj):
        focal = FocalPerson.objects.filter(school=obj).first()
        if focal:
            return {
                'name': focal.name,
                'email': focal.email,
                'phone': focal.phone,
                'designation': focal.designation
            }
        return None
class SchoolUpdateSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()

    # Focal person fields (write-only for updates)
    focal_name = serializers.CharField(write_only=True, required=False)
    focal_email = serializers.EmailField(write_only=True, required=False)
    focal_phone = serializers.CharField(write_only=True, required=False)
    focal_designation = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = School
        fields = [
            'name',
            'establish_date',
            'landline',
            'email',
            'country',
            'province',
            'district',
            'city',
            'address',
            'logo',
            'logo_url',
            'focal_name',
            'focal_email',
            'focal_phone',
            'focal_designation'
        ]
        extra_kwargs = {
            'logo': {'write_only': True}  
        }

    def update(self, instance, validated_data):
       
        for attr, value in validated_data.items():
            if attr not in ['focal_name', 'focal_email', 'focal_phone', 'focal_designation']:
                setattr(instance, attr, value)
        instance.save()

      
        focal = FocalPerson.objects.filter(school=instance).first()
        if focal:
            focal.name = validated_data.get('focal_name', focal.name)
            focal.email = validated_data.get('focal_email', focal.email)
            focal.phone = validated_data.get('focal_phone', focal.phone)
            focal.designation = validated_data.get('focal_designation', focal.designation)
            focal.save()

        return instance

   
    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo:
            return build_https_url(request, obj.logo.url)  
        return None

    def get_country(self, obj):
        return obj.country.name if obj.country else None

    def get_province(self, obj):
        return obj.province.name if obj.province else None

    def get_district(self, obj):
        return obj.district.name if obj.district else None



from rest_framework import serializers
from user.models import School
from user.serializers.address_serializers import ProvinceSerializer,CountrySerializer,DistrictSerializer
class SchoolBasicSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    country=CountrySerializer()
    province=ProvinceSerializer()
    district=DistrictSerializer()

    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'email',
            'city',
            'address',
            'logo',
            'country',
            'district',
            'province',
        ]
    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo:
            return build_https_url(request, obj.logo.url)  
        return None


class FocalPersonGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocalPerson
        fields = ("id", "name", "email", "phone", "designation")


from rest_framework import serializers
from django.db.models import Count
from utils.urlsfixer import build_https_url

from user.models import School, FocalPerson, SchoolStudentParent
from school.models import SubscriptionHistory

# ^ adjust import path to your actual file
# It already nests `logs = SubscriptionLogSerializer(many=True)` in your code.

from user.serializers.school_serializers import FocalPersonGetSerializer  # if you place it there


class SchoolGetSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    country = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()

    focal_person = serializers.SerializerMethodField()

    # subscription histories (each includes nested logs via SubscriptionHistoryListSerializer)
    subscriptions = serializers.SerializerMethodField()

    # counts
    student_count = serializers.SerializerMethodField()
    parent_count = serializers.SerializerMethodField()
    relation_count = serializers.SerializerMethodField()
    subscription_status = serializers.SerializerMethodField()


    class Meta:
        model = School
        fields = (
            "id",
            "name",
            "code",
            "establish_date",
            "landline",
            "email",
            "country",
            "province",
            "district",
            "city",
            "address",
            "logo_url",
            "created_at",
            "updated_at",

            "focal_person",

            "student_count",
            "parent_count",
            "relation_count",
            "subscription_status",


            "subscriptions",
        )

    # ---------- base computed fields ----------
    def get_logo_url(self, obj):
        request = self.context.get("request")
        if obj.logo:
            return build_https_url(request, obj.logo.url)
        return None

    def get_country(self, obj):
        return obj.country.name if obj.country else None

    def get_province(self, obj):
        return obj.province.name if obj.province else None

    def get_district(self, obj):
        return obj.district.name if obj.district else None

    def get_subscription_status(self, obj):
        sub = (
            SubscriptionHistory.objects
            .filter(school=obj)
            .order_by("-start_date")
            .only("end_date", "status")
            .first()
        )

        # No subscription → pending
        if not sub:
            return "pending"

        now = timezone.now()

        # Not paid → pending
        if sub.status != "paid":
            return "pending"

        # Paid but expired
        if sub.end_date and sub.end_date < now:
            return "expired"

        # Paid and active
        return "active"


    # ---------- focal person ----------
    def get_focal_person(self, obj):
        focal = getattr(obj, "prefetched_focal_person", None)
        if focal is None:
            focal = FocalPerson.objects.filter(school=obj).first()
        if not focal:
            return None
        return FocalPersonGetSerializer(focal, context=self.context).data

    # ---------- subscriptions ----------
    def get_subscriptions(self, obj):
        from school.serializers.subscriptions_serializers import SubscriptionHistoryListSerializer
        qs = getattr(obj, "prefetched_subscriptions", None)
        if qs is None:
            qs = (
                SubscriptionHistory.objects
                .filter(school=obj)
                .prefetch_related("logs")
                .order_by("-start_date")
            )
        return SubscriptionHistoryListSerializer(qs, many=True, context=self.context).data

    # ---------- counts ----------
    def get_student_count(self, obj):
        # uses distinct to avoid duplicates
        return (
            SchoolStudentParent.objects
            .filter(school=obj)
            .values("student")
            .distinct()
            .count()
        )

    def get_parent_count(self, obj):
        return (
            SchoolStudentParent.objects
            .filter(school=obj)
            .values("parent")
            .distinct()
            .count()
        )

    def get_relation_count(self, obj):
        return SchoolStudentParent.objects.filter(school=obj).count()


from rest_framework import serializers
from user.models import School
from utils.urlsfixer import build_https_url

class SchoolListSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    focal_person = serializers.SerializerMethodField()
    subscription_expiry_date = serializers.SerializerMethodField()
    subscription_status = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = (
            "id",
            "name",
            "email",
            "city",
            "address",
            "code",
            "logo_url",
            "focal_person",
            "subscription_expiry_date",
            "subscription_status",
        )

    # ---------- logo ----------
    def get_logo_url(self, obj):
        request = self.context.get("request")
        if obj.logo:
            return build_https_url(request, obj.logo.url)
        return None

    # ---------- focal person ----------
    def get_focal_person(self, obj):
        focal = FocalPerson.objects.filter(school=obj).first()
        if not focal:
            return None
        return {
            "name": focal.name,
            "email": focal.email,
            "phone": focal.phone,
            "designation": focal.designation,
        }

    # ---------- subscription ----------
    def _get_latest_subscription(self, obj):
        return (
            SubscriptionHistory.objects
            .filter(school=obj)
            .order_by("-start_date")
            .only("end_date", "status")
            .first()
        )

    def get_subscription_expiry_date(self, obj):
        sub = self._get_latest_subscription(obj)
        return sub.end_date if sub else None

    def get_subscription_status(self, obj):
        sub = self._get_latest_subscription(obj)

        # ✅ If no subscription → pending
        if not sub:
            return "pending"

        now = timezone.now()

        # ✅ If not paid yet → pending
        if sub.status != "paid":
            return "pending"

        # ✅ If paid but expired
        if sub.end_date and sub.end_date < now:
            return "expired"

        # ✅ Paid and active
        return "active"



from rest_framework import serializers
from user.models import School


class SchoolDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ("id", "name")
