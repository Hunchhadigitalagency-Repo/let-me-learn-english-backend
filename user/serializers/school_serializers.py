# user/serializers/school_serializers.py

from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from user.models import User, UserProfile, School, Country, Province, District, FocalPerson, SchoolStudentParent
from school.models import Subscription  # updated import
from utils.urlsfixer import build_https_url
from user.serializers.address_serializers import ProvinceSerializer, CountrySerializer, DistrictSerializer


# ─────────────────────────────────────────
# Registration
# ─────────────────────────────────────────

class SchoolRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    school_name = serializers.CharField(source='name', required=False)

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


# ─────────────────────────────────────────
# Create
# ─────────────────────────────────────────

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
            'id', 'name', 'establish_date', 'landline', 'email',
            'city', 'address', 'logo', 'logo_url',
            'country_id', 'province_id', 'district_id',
            'country', 'province', 'district', 'code',
            'focal_name', 'focal_email', 'focal_phone', 'focal_designation',
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
            'designation': validated_data.pop('focal_designation'),
        }

        with transaction.atomic():
            country = Country.objects.get(id=validated_data.pop('country_id')) if validated_data.get('country_id') else None
            province = Province.objects.get(id=validated_data.pop('province_id')) if validated_data.get('province_id') else None
            district = District.objects.get(id=validated_data.pop('district_id')) if validated_data.get('district_id') else None

            school = School.objects.create(
                user=user, country=country, province=province, district=district,
                **validated_data
            )
            FocalPerson.objects.create(school=school, **focal_data)

        return school

    def get_logo_url(self, obj):
        request = self.context.get('request')
        return build_https_url(request, obj.logo.url) if obj.logo else None

    def get_country(self, obj):
        return obj.country.name if obj.country else None

    def get_province(self, obj):
        return obj.province.name if obj.province else None

    def get_district(self, obj):
        return obj.district.name if obj.district else None

    def get_focal_person(self, obj):
        focal = FocalPerson.objects.filter(school=obj).first()
        if focal:
            return {'name': focal.name, 'email': focal.email, 'phone': focal.phone, 'designation': focal.designation}
        return None


# ─────────────────────────────────────────
# Update
# ─────────────────────────────────────────

class SchoolUpdateSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()

    focal_name = serializers.CharField(write_only=True, required=False)
    focal_email = serializers.EmailField(write_only=True, required=False)
    focal_phone = serializers.CharField(write_only=True, required=False)
    focal_designation = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = School
        fields = [
            'name', 'establish_date', 'landline', 'email',
            'country', 'province', 'district', 'city', 'address',
            'logo', 'logo_url',
            'focal_name', 'focal_email', 'focal_phone', 'focal_designation',
        ]
        extra_kwargs = {'logo': {'write_only': True}}

    def update(self, instance, validated_data):
        focal_fields = {'focal_name', 'focal_email', 'focal_phone', 'focal_designation'}
        for attr, value in validated_data.items():
            if attr not in focal_fields:
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
        return build_https_url(request, obj.logo.url) if obj.logo else None

    def get_country(self, obj):
        return obj.country.name if obj.country else None

    def get_province(self, obj):
        return obj.province.name if obj.province else None

    def get_district(self, obj):
        return obj.district.name if obj.district else None


# ─────────────────────────────────────────
# Basic / Dropdown
# ─────────────────────────────────────────

class SchoolBasicSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    country = CountrySerializer()
    province = ProvinceSerializer()
    district = DistrictSerializer()

    class Meta:
        model = School
        fields = ['id', 'name', 'email', 'city', 'address', 'logo', 'country', 'district', 'province']

    def get_logo(self, obj):
        request = self.context.get('request')
        return build_https_url(request, obj.logo.url) if obj.logo else None


class SchoolDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ("id", "name")


class FocalPersonGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocalPerson
        fields = ("id", "name", "email", "phone", "designation")


# ─────────────────────────────────────────
# Shared helper — subscription status
# Reused in both SchoolGetSerializer and SchoolListSerializer
# ─────────────────────────────────────────

def resolve_subscription_status(subscription):
    """
    Given a Subscription instance (or None), return a human-readable status string.
    on_trial is now a field on the Subscription model itself.
    """
    if not subscription:
        return "new"

    now = timezone.now().date()  # Subscription uses DateField

    if subscription.status == "deactivated":
        return "deactivated"

    if subscription.status == "inactive":
        return "inactive"

    if subscription.on_trial:
        return "on_trial"

    if subscription.end_date and subscription.end_date < now:
        return "expired"

    if subscription.end_date and now <= subscription.end_date <= now + timedelta(days=7):
        return "expiring_soon"

    if subscription.status == "pending":
        return "pending"

    if subscription.status == "paid":
        return "active"

    return "inactive"


# ─────────────────────────────────────────
# Get (detail view)
# ─────────────────────────────────────────

class SchoolGetSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    focal_person = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()      # single object, not a list
    subscription_status = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    parent_count = serializers.SerializerMethodField()
    relation_count = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = (
            "id", "name", "code", "establish_date", "landline", "email",
            "country", "province", "district", "city", "address",
            "logo_url", "created_at", "updated_at",
            "focal_person",
            "student_count", "parent_count", "relation_count",
            "subscription_status",
            "subscription",          # replaces "subscriptions" list
        )

    def _get_subscription(self, obj):
        """Cache subscription on the object to avoid repeated DB hits."""
        if not hasattr(obj, '_cached_subscription'):
            obj._cached_subscription = (
                Subscription.objects
                .filter(school=obj)
                .prefetch_related("logs")
                .first()
            )
        return obj._cached_subscription

    def get_logo_url(self, obj):
        request = self.context.get("request")
        return build_https_url(request, obj.logo.url) if obj.logo else None

    def get_country(self, obj):
        return obj.country.name if obj.country else None

    def get_province(self, obj):
        return obj.province.name if obj.province else None

    def get_district(self, obj):
        return obj.district.name if obj.district else None

    def get_subscription_status(self, obj):
        return resolve_subscription_status(self._get_subscription(obj))

    def get_focal_person(self, obj):
        focal = getattr(obj, "prefetched_focal_person", None)
        if focal is None:
            focal = FocalPerson.objects.filter(school=obj).first()
        if not focal:
            return None
        return FocalPersonGetSerializer(focal, context=self.context).data

    def get_subscription(self, obj):
        from school.serializers.subscriptions_serializers import SubscriptionHistoryListSerializer
        sub = self._get_subscription(obj)
        if not sub:
            return None
        return SubscriptionHistoryListSerializer(sub, context=self.context).data

    def get_student_count(self, obj):
        return SchoolStudentParent.objects.filter(school=obj).values("student").distinct().count()

    def get_parent_count(self, obj):
        return SchoolStudentParent.objects.filter(school=obj).values("parent").distinct().count()

    def get_relation_count(self, obj):
        return SchoolStudentParent.objects.filter(school=obj).count()


# ─────────────────────────────────────────
# List (table/card view)
# ─────────────────────────────────────────

class SchoolListSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    focal_person = serializers.SerializerMethodField()
    subscription_expiry_date = serializers.SerializerMethodField()
    subscription_status = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = (
            "id", "name", "email", "city", "address", "code",
            "logo_url", "focal_person",
            "subscription_expiry_date", "subscription_status",
        )

    def _get_subscription(self, obj):
        if not hasattr(obj, '_cached_subscription'):
            obj._cached_subscription = (
                Subscription.objects
                .filter(school=obj)
                .only("end_date", "status", "on_trial")
                .first()
            )
        return obj._cached_subscription

    def get_logo_url(self, obj):
        request = self.context.get("request")
        return build_https_url(request, obj.logo.url) if obj.logo else None

    def get_focal_person(self, obj):
        focal = FocalPerson.objects.filter(school=obj).first()
        if not focal:
            return None
        return {'name': focal.name, 'email': focal.email, 'phone': focal.phone, 'designation': focal.designation}

    def get_subscription_expiry_date(self, obj):
        sub = self._get_subscription(obj)
        return sub.end_date if sub else None

    def get_subscription_status(self, obj):
        return resolve_subscription_status(self._get_subscription(obj))