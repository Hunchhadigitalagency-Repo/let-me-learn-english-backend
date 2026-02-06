# tasks/viewsets/reading_question_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import ReadingAcitivityQuestion
from tasks.serializers.reading_activity_question_serializers import (
    ReadingActivityQuestionCreateSerializer,
    ReadingActivityQuestionListSerializer
)
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.decorators import has_permission
class ReadingActivityQuestionViewSet(viewsets.ViewSet):

    # Helper to choose serializer based on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return ReadingActivityQuestionListSerializer
        return ReadingActivityQuestionCreateSerializer

    # List all questions with pagination
    @has_permission("can_read_readingactivityquestion")
    @swagger_auto_schema(
        operation_description="List all reading activity questions with pagination",
        responses={200: ReadingActivityQuestionListSerializer(many=True)}
    )
    def list(self, request):
        queryset = ReadingAcitivityQuestion.objects.all().order_by('-id')

        reading_activity_id = request.query_params.get("reading_activity_id")

        if reading_activity_id:
            queryset = queryset.filter(reading_activity_id=reading_activity_id)

        paginator = CustomPageNumberPagination()
        paginated_questions = paginator.paginate_queryset(queryset, request)

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(
            paginated_questions,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response(serializer.data)

    # Retrieve a single question
    @has_permission("can_read_readingactivityquestion")
    @swagger_auto_schema(
        operation_description="Retrieve a single reading activity question by ID",
        responses={200: ReadingActivityQuestionListSerializer()}
    )
    def retrieve(self, request, pk=None):
        question = get_object_or_404(ReadingAcitivityQuestion, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(question, context={'request': request})
        return Response(serializer.data)

    # Create a new question
    @has_permission("can_write_readingactivityquestion")
    @swagger_auto_schema(
        operation_description="Create a new reading activity question",
        request_body=ReadingActivityQuestionCreateSerializer,
        responses={
            201: ReadingActivityQuestionListSerializer(),
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

    # Update a question completely (PUT)
    @has_permission("can_update_readingactivityquestion")
    @swagger_auto_schema(
        operation_description="Update a reading activity question completely",
        request_body=ReadingActivityQuestionCreateSerializer,
        responses={
            200: ReadingActivityQuestionListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        question = get_object_or_404(ReadingAcitivityQuestion, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(question, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    @has_permission("can_update_readingactivityquestion")
    @swagger_auto_schema(
        operation_description="Partially update a reading activity question",
        request_body=ReadingActivityQuestionCreateSerializer,
        responses={
            200: ReadingActivityQuestionListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        question = get_object_or_404(ReadingAcitivityQuestion, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(question, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a question
    @has_permission("can_delete_readingactivityquestion")
    @swagger_auto_schema(
        operation_description="Delete a reading activity question",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )
    def destroy(self, request, pk=None):
        question = get_object_or_404(ReadingAcitivityQuestion, pk=pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
