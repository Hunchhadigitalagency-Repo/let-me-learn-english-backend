# tasks/viewsets/reading_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import ReadingActivity
from tasks.serializers.reading_activity_serializers import (
    ReadingActivityCreateSerializer,
    ReadingActivityListSerializer
)
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.decorators import has_permission
class ReadingActivityViewSet(viewsets.ViewSet):
    
    # Helper to choose serializer depending on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return ReadingActivityListSerializer
        return ReadingActivityCreateSerializer

    # List all reading activities with pagination
    @has_permission("can_read_readingactivity")
    @swagger_auto_schema(
        operation_description="List all reading activities with pagination",
        responses={200: ReadingActivityListSerializer(many=True)}
    )
    def list(self, request):
        activities = ReadingActivity.objects.all().order_by('-id')
        
        # Apply pagination
        paginator = CustomPageNumberPagination()
        paginated_activities = paginator.paginate_queryset(activities, request)
        
        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_activities, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

    # Retrieve a single reading activity
    @has_permission("can_read_readingactivity")
    @swagger_auto_schema(
        operation_description="Retrieve a single reading activity by ID",
        responses={200: ReadingActivityListSerializer()}
    )
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(ReadingActivity, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(activity, context={'request': request})
        return Response(serializer.data)

    # Create a new reading activity
    @has_permission("can_write_readingactivity")
    @swagger_auto_schema(
        operation_description="Create a new reading activity",
        request_body=ReadingActivityCreateSerializer,
        responses={
            201: ReadingActivityListSerializer(),
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

    # Update a reading activity completely (PUT)
    @has_permission("can_update_readingactivity")
    @swagger_auto_schema(
        operation_description="Update a reading activity completely",
        request_body=ReadingActivityCreateSerializer,
        responses={
            200: ReadingActivityListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        activity = get_object_or_404(ReadingActivity, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(activity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    @has_permission("can_update_readingactivity")
    @swagger_auto_schema(
        operation_description="Partially update a reading activity",
        request_body=ReadingActivityCreateSerializer,
        responses={
            200: ReadingActivityListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(ReadingActivity, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(activity, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a reading activity
    @has_permission("can_delete_readingactivity")
    @swagger_auto_schema(
        operation_description="Delete a reading activity",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )
    def destroy(self, request, pk=None):
        activity = get_object_or_404(ReadingActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
