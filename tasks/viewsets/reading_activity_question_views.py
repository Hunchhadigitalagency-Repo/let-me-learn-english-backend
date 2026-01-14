# tasks/viewsets/reading_question_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import ReadingAcitivityQuestion
from tasks.serializers.reading_activity_question_serializers import ReadingActivityQuestionSerializer

class ReadingActivityQuestionViewSet(viewsets.ViewSet):

    # List all questions
    def list(self, request):
        questions = ReadingAcitivityQuestion.objects.all()
        serializer = ReadingActivityQuestionSerializer(
            questions, many=True, context={'request': request}
        )
        return Response(serializer.data)

    # Retrieve a single question
    def retrieve(self, request, pk=None):
        question = get_object_or_404(ReadingAcitivityQuestion, pk=pk)
        serializer = ReadingActivityQuestionSerializer(question, context={'request': request})
        return Response(serializer.data)

    # Create a new question
    def create(self, request):
        serializer = ReadingActivityQuestionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a question completely (PUT)
    def update(self, request, pk=None):
        question = get_object_or_404(ReadingAcitivityQuestion, pk=pk)
        serializer = ReadingActivityQuestionSerializer(
            question, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    def partial_update(self, request, pk=None):
        question = get_object_or_404(ReadingAcitivityQuestion, pk=pk)
        serializer = ReadingActivityQuestionSerializer(
            question, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a question
    def destroy(self, request, pk=None):
        question = get_object_or_404(ReadingAcitivityQuestion, pk=pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
