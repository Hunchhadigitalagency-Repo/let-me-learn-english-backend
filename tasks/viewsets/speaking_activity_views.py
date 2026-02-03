# tasks/viewsets/activity_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import SpeakingActivity
from tasks.serializers.speaking_activity_serializers import (
    SpeakingActivityCreateSerializer,
    SpeakingActivityListSerializer
)
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.decorators import has_permission
class SpeakingActivityViewSet(viewsets.ViewSet):
    """
    Full CRUD ViewSet for SpeakingActivity with dynamic serializers and pagination.
    """

    # Helper to choose serializer based on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return SpeakingActivityListSerializer
        return SpeakingActivityCreateSerializer

    # List all speaking activities with pagination
    @has_permission("can_read_speakingactivity")
    @swagger_auto_schema(
        operation_description="List all speaking activities with pagination",
        responses={200: SpeakingActivityListSerializer(many=True)}
    )
    def list(self, request):
        activities = SpeakingActivity.objects.all().order_by('-id')
        paginator = CustomPageNumberPagination()
        paginated_activities = paginator.paginate_queryset(activities, request)

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_activities, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    # Retrieve a single speaking activity
    @has_permission("can_read_speakingactivity")
    @swagger_auto_schema(
        operation_description="Retrieve a single speaking activity by ID",
        responses={200: SpeakingActivityListSerializer()}
    )
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(SpeakingActivity, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(activity, context={'request': request})
        return Response(serializer.data)

    # Create a new speaking activity
    @has_permission("can_write_speakingactivity")
    @swagger_auto_schema(
        operation_description="Create a new speaking activity",
        request_body=SpeakingActivityCreateSerializer,
        responses={
            201: SpeakingActivityListSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a speaking activity completely (PUT)
    @has_permission("can_update_speakingactivity")
    @swagger_auto_schema(
        operation_description="Update a speaking activity completely",
        request_body=SpeakingActivityCreateSerializer,
        responses={
            200: SpeakingActivityListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        activity = get_object_or_404(SpeakingActivity, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(activity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    @has_permission("can_update_speakingactivity")
    @swagger_auto_schema(
        operation_description="Partially update a speaking activity",
        request_body=SpeakingActivityCreateSerializer,
        responses={
            200: SpeakingActivityListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(SpeakingActivity, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(activity, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete speaking 
    @has_permission("can_delete_speakingactivity")
    @swagger_auto_schema(
        operation_description="Delete a speaking activity",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )
    def destroy(self, request, pk=None):
        activity = get_object_or_404(SpeakingActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





from rest_framework import viewsets
from rest_framework.response import Response
from tasks.models import SpeakingActivity
from tasks.serializers.speaking_activity_serializers import SpeakingActivityDropdownSerializer
from utils.decorators import has_permission
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
class SpeakingActivityDropdownViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
  

    
    @swagger_auto_schema(
        operation_description="List all speaking activities for dropdown with nested questions, filterable by question type",
        manual_parameters=[
            openapi.Parameter(
                'type', 
                openapi.IN_QUERY,
                description="Filter questions by type (e.g., reading, writing)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: SpeakingActivityDropdownSerializer(many=True)}
    )
    def list(self, request):
        question_type = request.query_params.get('type', None)

        if question_type:
           
            activities = SpeakingActivity.objects.filter(
                speakingactivityquestion__type=question_type
            ).distinct().order_by('title')
        else:
            activities = SpeakingActivity.objects.all().order_by('title')

        serializer = SpeakingActivityDropdownSerializer(
            activities,
            many=True,
            context={'request': request, 'question_type': question_type}
        )
        return Response(serializer.data)
