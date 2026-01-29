from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from master_settings.models import ExamPause
from master_settings.serializers.exampause_serializers import (
    ExamPauseListSerializer,
    ExamPauseCreateSerializer,
)
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ExamPauseViewSet(ModelViewSet):
   
    queryset = ExamPause.objects.all().order_by('-start_date')
    permission_classes = [IsAuthenticated]

    # Pagination
    pagination_class = CustomPageNumberPagination

    # Filters, search, ordering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['school', 'grade', 'mark_all_grade']
    search_fields = ['grade', 'school__name']

    ordering_fields = ['start_date', 'end_date', 'grade']

    def get_serializer_class(self):
        """Switch serializer based on action"""
        if self.action in ['list', 'retrieve']:
            return ExamPauseListSerializer
        return ExamPauseCreateSerializer
    
    @swagger_auto_schema(
        tags=['admin.exampause'],
        operation_summary="List Exam Pauses",
        operation_description=(
            "Paginated list of ExamPause entries.\n\n"
            "Filters:\n"
            "- school: Filter by school ID\n"
            "- grade: Filter by grade\n"
            "- mark_all_grade: Filter by boolean\n\n"
            "Search:\n"
            "- grade and school name\n\n"
            "Ordering:\n"
            "- start_date, end_date, grade"
        ),
        responses={200: ExamPauseListSerializer(many=True)}
    )

   
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer_class()(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @swagger_auto_schema(
        tags=['admin.exampause'],
        operation_summary="Retrieve Exam Pause",
        operation_description="Fetch a single ExamPause entry by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ExamPause ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: ExamPauseListSerializer(), 404: "Not Found"}
    )
    
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer_class()(instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=['admin.exampause'],
        operation_summary="Create Exam Pause",
        operation_description="Create a new ExamPause entry",
        request_body=ExamPauseCreateSerializer,
        responses={201: ExamPauseCreateSerializer(), 400: "Bad Request"}
    )


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        tags=['admin.exampause'],
        operation_summary="Partial Update Exam Pause",
        operation_description="Partially update an existing ExamPause entry by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ExamPause ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=ExamPauseCreateSerializer,
        responses={200: ExamPauseCreateSerializer(), 400: "Bad Request", 404: "Not Found"}
    )

    def partial_update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer_class()(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @swagger_auto_schema(
        tags=['admin.exampause'],
        operation_summary="Delete Exam Pause",
        operation_description="Delete an ExamPause entry by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ExamPause ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={204: "Deleted successfully", 404: "Not Found"}
    )

    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"detail": "Exam pause deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
