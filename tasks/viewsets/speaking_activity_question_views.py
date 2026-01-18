# tasks/viewsets/activity_question_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import SpeakingActivityQuestion
from tasks.serializers.speaking_activity_question_serializers import (
    SpeakingActivityQuestionCreateSerializer,
    SpeakingActivityQuestionListSerializer
)
from utils.paginator import CustomPageNumberPagination

class SpeakingActivityQuestionViewSet(viewsets.ViewSet):
    """
    Full CRUD ViewSet for SpeakingActivityQuestion with dynamic serializers and pagination.
    """

    # Helper to select serializer based on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return SpeakingActivityQuestionListSerializer
        return SpeakingActivityQuestionCreateSerializer

    # List all questions with pagination
    def list(self, request):
        questions = SpeakingActivityQuestion.objects.all().order_by('-id')
        paginator = CustomPageNumberPagination()
        paginated_questions = paginator.paginate_queryset(questions, request)

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_questions, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    # Retrieve a single question
    def retrieve(self, request, pk=None):
        question = get_object_or_404(SpeakingActivityQuestion, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(question, context={'request': request})
        return Response(serializer.data)

    # Create a new question
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a question completely (PUT)
    def update(self, request, pk=None):
        question = get_object_or_404(SpeakingActivityQuestion, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(question, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH) with file handling
    def partial_update(self, request, pk=None):
        question = get_object_or_404(SpeakingActivityQuestion, pk=pk)

        # Handle attachment upload
        if 'attachment' in request.FILES:
            question.attachment = request.FILES['attachment']

        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(
            question, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a question
    def destroy(self, request, pk=None):
        question = get_object_or_404(SpeakingActivityQuestion, pk=pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
