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
    def list(self, request):
        activities = WritingActivity.objects.all().order_by('-id')
        paginator = CustomPageNumberPagination()
        paginated_activities = paginator.paginate_queryset(activities, request)

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_activities, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    # Retrieve a single writing activity
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(activity, context={'request': request})
        return Response(serializer.data)

    # Create a new writing activity
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a writing activity completely (PUT)
    def update(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(activity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(activity, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a writing activity
    def destroy(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
