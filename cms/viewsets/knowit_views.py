from rest_framework import viewsets, status
from rest_framework.response import Response
from cms.models import NowKnowIt
from cms.serializers.knowit_serializers import NowKnowItSerializer
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from django.utils.dateparse import parse_date  
from utils.decorators import has_permission
class NowKnowItViewSet(viewsets.ModelViewSet):
    
    queryset = NowKnowIt.objects.all().order_by("-created_at")
    serializer_class = NowKnowItSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    
    search_fields = ['common_nepali_english', 'natural_english', 'reason']

    
    filterset_fields = ['is_active', 'used_status', 'forced_publish', 'created_at', 'updated_at']

   
    ordering_fields = ['created_at', 'updated_at']

    # ---------------- LIST ----------------
    @has_permission("can_read_knowit")
    @swagger_auto_schema(
        operation_description="List all NowKnowIt items with pagination",
        responses={200: NowKnowItSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # ---------------- RETRIEVE ----------------
    @has_permission("can_read_knowit")
    @swagger_auto_schema(
        operation_description="Retrieve a single NowKnowIt item by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="NowKnowIt ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: NowKnowItSerializer(),
            404: "Not Found"
        }
    )
    def retrieve(self, request, pk=None):
        try:
            instance = NowKnowIt.objects.get(pk=pk)
        except NowKnowIt.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NowKnowItSerializer(instance)
        return Response(serializer.data)

    # ---------------- CREATE ----------------
    @has_permission("can_write_knowit")
    @swagger_auto_schema(
        operation_description="Create a new NowKnowIt item",
        request_body=NowKnowItSerializer,
        responses={
            201: NowKnowItSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer = NowKnowItSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # ---------------- UPDATE (PUT) ----------------
    @has_permission("can_update_knowit")
    @swagger_auto_schema(
        operation_description="Update a NowKnowIt item completely by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="NowKnowIt ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=NowKnowItSerializer,
        responses={
            200: NowKnowItSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        try:
            instance = NowKnowIt.objects.get(pk=pk)
        except NowKnowIt.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NowKnowItSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # ---------------- PARTIAL UPDATE (PATCH) ----------------
    @has_permission("can_update_knowit")
    @swagger_auto_schema(
        operation_description="Partially update a NowKnowIt item by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="NowKnowIt ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=NowKnowItSerializer,
        responses={
            200: NowKnowItSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        try:
            instance = NowKnowIt.objects.get(pk=pk)
        except NowKnowIt.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NowKnowItSerializer(
            instance,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # ---------------- DELETE ----------------
    @has_permission("can_delete_knowit")
    @swagger_auto_schema(
        operation_description="Delete a NowKnowIt item by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="NowKnowIt ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Deleted successfully",
            404: "Not Found"
        }
    )
    def destroy(self, request, pk=None):
        try:
            instance = NowKnowIt.objects.get(pk=pk)
        except NowKnowIt.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        instance.delete()
        return Response(
            {"detail": "Deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
        
        
    


from rest_framework.permissions import IsAuthenticated


from cms.models import NowKnowIt
from cms.serializers.knowit_serializers import NowKnowItSerializer

class NowKnowItDropdownViewSet(viewsets.ViewSet):
   
    permission_classes = [IsAuthenticated]  

    @swagger_auto_schema(
        operation_description="Dropdown list of NowKnowIt filtered by date range",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Filter items with created_at >= start_date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="Filter items with created_at <= end_date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            ),
        ],
        responses={200: NowKnowItSerializer(many=True)}
    )
    def list(self, request):
       
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

      
        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

      
        qs = NowKnowIt.objects.filter(is_active=True)

       
        if start_date and end_date:
            qs = qs.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )

        qs = qs.order_by("-created_at")
        serializer = NowKnowItSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)