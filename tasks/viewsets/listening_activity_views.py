# tasks/viewsets/listening_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import ListeningActivity
from tasks.serializers.listening_activity_serializers import (
    ListeningActivityCreateSerializer,
    ListeningActivityListSerializer
)
from utils.paginator import CustomPageNumberPagination
class ListeningActivityViewSet(viewsets.ViewSet):
    
    # Helper to choose serializer depending on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return ListeningActivityListSerializer
        return ListeningActivityCreateSerializer

    # List all listening activities
    # List all listening activities with pagination
    # List all listening activities with pagination
    def list(self, request):
        activities = ListeningActivity.objects.all().order_by('-id')
        
        # Apply custom pagination
        paginator = CustomPageNumberPagination()
        paginated_activities = paginator.paginate_queryset(activities, request)
        
        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_activities, many=True, context={'request': request})
        
        # Return paginated response using your CustomPageNumberPagination
        return paginator.get_paginated_response(serializer.data)



    # Retrieve a single listening activity
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(ListeningActivity, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(activity, context={'request': request})
        return Response(serializer.data)

    # Create a new listening activity
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a listening activity completely (PUT)
    def update(self, request, pk=None):
        activity = get_object_or_404(ListeningActivity, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(activity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(ListeningActivity, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(activity, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a listening activity
    def destroy(self, request, pk=None):
        activity = get_object_or_404(ListeningActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
