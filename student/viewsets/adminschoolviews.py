from rest_framework import viewsets, status
from rest_framework.response import Response
from utils.permissions.admins.admin_perms_mixins import IsAdminUserType
from user.models import School
from user.serializers.school_serializers import SchoolBasicSerializer
from django.db.models import Q  
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
class SchoolBasicViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserType]
    search_param = openapi.Parameter(
        'search', openapi.IN_QUERY,
        description="Search by school name, district, province, country, city, or address",
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(
        manual_parameters=[search_param],
        responses={200: SchoolBasicSerializer(many=True)}
    )

    def list(self, request):
        search_query = request.query_params.get('search', '').strip()

        if search_query:
            schools = School.objects.filter(
                Q(name__icontains=search_query) |
                Q(district__name__icontains=search_query) |
                Q(country__name__icontains=search_query) |
                Q(province__name__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(city__icontains=search_query)
            )
        else:
            schools = School.objects.all()

        serializer = SchoolBasicSerializer(schools, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
