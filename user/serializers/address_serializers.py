from rest_framework import serializers
from user.models import Country, Province, District

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']

class ProvinceSerializer(serializers.ModelSerializer):
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source='country',  
        write_only=True
    )
    country = serializers.SerializerMethodField()  # to show country name instead of ID

    class Meta:
        model = Province
        fields = ['id', 'name', 'country','country_id']

    def get_country(self, obj):
        return obj.country.name if obj.country else None

class DistrictSerializer(serializers.ModelSerializer):
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(),
        source='province',  
        write_only=True
    )
    province = serializers.SerializerMethodField()  # to show province name instead of ID

    class Meta:
        model = District
        fields = ['id', 'name', 'province','province_id']

    def get_province(self, obj):
        return obj.province.name if obj.province else None
