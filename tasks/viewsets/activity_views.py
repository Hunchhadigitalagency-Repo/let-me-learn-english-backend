from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import SpeakingActivity
from tasks.serializers.activity_serializers import SpeakingActivitySerializer

class SpeakingActivityViewSet(viewsets.ViewSet):
    """
    A full ViewSet for SpeakingActivity with all CRUD operations.
    """

    # List all speaking activities
    def list(self, request):
        activities = SpeakingActivity.objects.all()
        serializer = SpeakingActivitySerializer(activities, many=True,context={'request': request})
        return Response(serializer.data)

    # Retrieve a single speaking activity
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(SpeakingActivity, pk=pk)
        serializer = SpeakingActivitySerializer(activity,context={'request': request})
        return Response(serializer.data)

    # Create a new speaking activity
    def create(self, request):
        serializer = SpeakingActivitySerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  

    # Partial update (PATCH)
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(SpeakingActivity, pk=pk)
        serializer = SpeakingActivitySerializer(activity, data=request.data, partial=True,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete speaking activity
    def destroy(self, request, pk=None):
        activity = get_object_or_404(SpeakingActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
