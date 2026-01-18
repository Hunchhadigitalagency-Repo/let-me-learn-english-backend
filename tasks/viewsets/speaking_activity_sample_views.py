# tasks/viewsets/activity_sample_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import speakingActivitySample
from tasks.serializers.speaking_activity_sample_serializers import (
    SpeakingActivitySampleCreateSerializer,
    SpeakingActivitySampleListSerializer
)
from utils.paginator import CustomPageNumberPagination

class SpeakingActivitySampleViewSet(viewsets.ViewSet):
    """
    Full CRUD ViewSet for speakingActivitySample with dynamic serializers and pagination.
    """

    # Helper to choose serializer based on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return SpeakingActivitySampleListSerializer
        return SpeakingActivitySampleCreateSerializer

    # List all samples with pagination
    def list(self, request):
        samples = speakingActivitySample.objects.all().order_by('-id')
        paginator = CustomPageNumberPagination()
        paginated_samples = paginator.paginate_queryset(samples, request)

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_samples, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    # Retrieve a single sample
    def retrieve(self, request, pk=None):
        sample = get_object_or_404(speakingActivitySample, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(sample, context={'request': request})
        return Response(serializer.data)

    # Create a new sample
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a sample completely (PUT)
    def update(self, request, pk=None):
        sample = get_object_or_404(speakingActivitySample, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(sample, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    def partial_update(self, request, pk=None):
        sample = get_object_or_404(speakingActivitySample, pk=pk)
        
        # Handle uploaded files
        if 'sample_question' in request.FILES:
            sample.sample_question = request.FILES['sample_question']
        if 'sample_answer' in request.FILES:
            sample.sample_answer = request.FILES['sample_answer']

        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(sample, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a sample
    def destroy(self, request, pk=None):
        sample = get_object_or_404(speakingActivitySample, pk=pk)
        sample.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
