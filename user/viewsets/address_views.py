# user/viewsets/location_views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from user.models import Country, Province, District
from user.serializers.address_serializers import CountrySerializer, ProvinceSerializer, DistrictSerializer

# ----------------- COUNTRY -----------------
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]  # you can change as needed

# ----------------- PROVINCE -----------------
class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [AllowAny]

# ----------------- DISTRICT -----------------
class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]
