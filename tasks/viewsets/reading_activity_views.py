# tasks/viewsets/reading_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import ReadingActivity
from tasks.serializers.reading_activity_serializers import ReadingActivitySerializer

class ReadingActivityViewSet(viewsets.ViewSet):
    
    # List all reading activities
    def list(self, request):
        activities = ReadingActivity.objects.all()
        serializer = ReadingActivitySerializer(activities, many=True, context={'request': request})
        return Response(serializer.data)

    # Retrieve a single reading activity
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(ReadingActivity, pk=pk)
        serializer = ReadingActivitySerializer(activity, context={'request': request})
        return Response(serializer.data)

    # Create a new reading activity
    def create(self, request):
        serializer = ReadingActivitySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a reading activity completely (PUT)
    def update(self, request, pk=None):
        activity = get_object_or_404(ReadingActivity, pk=pk)
        serializer = ReadingActivitySerializer(activity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(ReadingActivity, pk=pk)
        serializer = ReadingActivitySerializer(activity, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a reading activity
    def destroy(self, request, pk=None):
        activity = get_object_or_404(ReadingActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
