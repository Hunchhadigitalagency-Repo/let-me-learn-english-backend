# tasks/viewsets/reading_question_views.py
from urllib import request
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
from rest_framework.decorators import action
from rest_framework.response import Response
import uuid
from django.db import transaction
READ_TYPE = [
    ('true_false','True_False'),
    ('mcq','MCQ'),
    ('note_completion','NoteCompletion'),
    ('sentence_completion','SentenceCompletion'),
    ('summary_completion','SummaryCompletion')
]

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
        reading_activity_id = request.query_params.get("reading_activity_id")

        if not reading_activity_id:
            return Response([])

        queryset = ReadingAcitivityQuestion.objects.filter(
            reading_activity_id=reading_activity_id
        ).order_by('-id')

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(
            queryset,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)


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

    @has_permission("can_write_readingactivityquestion")
    @swagger_auto_schema(
        method='post',
        operation_description="Create multiple questions of a specific type",
        request_body=ReadingActivityQuestionCreateSerializer(many=True),
        responses={201: ReadingActivityQuestionListSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path=r'(?P<question_type>\w+)')
    def create_by_type(self, request, question_type=None):
        """
        Bulk create questions by type.
        URL example: POST /reading-activity-questions/true_false/
        Body: array of question objects
        """
        # Validate question_type
        valid_types = [q[0] for q in READ_TYPE]
        if question_type not in valid_types:
            return Response({"error": f"Invalid question type. Valid types: {valid_types}"},
                            status=status.HTTP_400_BAD_REQUEST)

        questions_data = request.data
        if not isinstance(questions_data, list) or len(questions_data) == 0:
            return Response({"error": "You must provide an array of question objects."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate a bundle_id for this batch
        bundle_id = uuid.uuid4()
        created_questions = []

        with transaction.atomic():
            for item in questions_data:
                item['type'] = question_type  # enforce type
                item['bundle_id'] = bundle_id  # attach bundle_id
                serializer = ReadingActivityQuestionCreateSerializer(data=item, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                created_questions.append(serializer.data)

        return Response({
            "bundle_id": str(bundle_id),
            "questions": created_questions
        }, status=status.HTTP_201_CREATED)