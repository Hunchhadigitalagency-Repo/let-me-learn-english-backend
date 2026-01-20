# tasks/viewsets/writing_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import WritingActivity
from tasks.serializers.writing_activity_serializers import (
    WritingActivityCreateSerializer,
    WritingActivityListSerializer
)
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
class WritingActivityViewSet(viewsets.ViewSet):
    """
    CRUD ViewSet for WritingActivity with dynamic serializers and pagination.
    """

    # Helper to select serializer based on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return WritingActivityListSerializer
        return WritingActivityCreateSerializer

    # List all writing activities with pagination
    @swagger_auto_schema(
        operation_description="List all writing activities with pagination",
        responses={200: WritingActivityListSerializer(many=True)}
    )
    def list(self, request):
        activities = WritingActivity.objects.all().order_by('-id')
        paginator = CustomPageNumberPagination()
        paginated_activities = paginator.paginate_queryset(activities, request)

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_activities, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    # Retrieve a single writing activity
    @swagger_auto_schema(
        operation_description="Retrieve a single writing activity by ID",
        responses={200: WritingActivityListSerializer()}
    )
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(activity, context={'request': request})
        return Response(serializer.data)

    # Create a new writing activity
    @swagger_auto_schema(
        operation_description="Create a new writing activity",
        request_body=WritingActivityCreateSerializer,
        responses={201: WritingActivityListSerializer(), 400: "Bad Request"}
    )
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a writing activity completely (PUT)
    @swagger_auto_schema(
        operation_description="Update a writing activity completely (PUT)",
        request_body=WritingActivityCreateSerializer,
        responses={200: WritingActivityListSerializer(), 400: "Bad Request", 404: "Not Found"}
    )
    def update(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(activity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    @swagger_auto_schema(
        operation_description="Partially update a writing activity (PATCH)",
        request_body=WritingActivityCreateSerializer,
        responses={200: WritingActivityListSerializer(), 400: "Bad Request", 404: "Not Found"}
    )
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(activity, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a writing activity
    @swagger_auto_schema(
        operation_description="Delete a writing activity",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )
    def destroy(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
