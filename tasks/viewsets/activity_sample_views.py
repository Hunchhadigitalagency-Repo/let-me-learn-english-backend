from tasks.serializers.activity_sample_serializers import SpeakingActivitySampleSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import speakingActivitySample

class SpeakingActivitySampleViewSet(viewsets.ViewSet):

    def list(self, request):
        samples = speakingActivitySample.objects.all()
        serializer = SpeakingActivitySampleSerializer(samples, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        sample = get_object_or_404(speakingActivitySample, pk=pk)
        serializer = SpeakingActivitySampleSerializer(sample, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        serializer = SpeakingActivitySampleSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        sample = get_object_or_404(speakingActivitySample, pk=pk)
        serializer = SpeakingActivitySampleSerializer(sample, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        sample = get_object_or_404(speakingActivitySample, pk=pk)
        if 'sample_question' in request.FILES:
            sample.sample_question = request.FILES['sample_question']
        if 'sample_answer' in request.FILES:
            sample.sample_answer = request.FILES['sample_answer']
        serializer = SpeakingActivitySampleSerializer(sample, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        sample = get_object_or_404(speakingActivitySample, pk=pk)
        sample.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
