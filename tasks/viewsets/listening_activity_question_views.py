from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from tasks.models import ListeningActivityQuestion
from tasks.serializers.listening_activity_question_serializers import (
    ListeningActivityQuestionCreateSerializer,
    ListeningActivityQuestionListSerializer
)
from utils.paginator import CustomPageNumberPagination
from utils.decorators import has_permission
from rest_framework.decorators import action
from rest_framework import status
from django.db import transaction
import uuid


LISTENING_CHOICES = ['part1', 'form_question']

class ListeningActivityQuestionViewSet(viewsets.ViewSet):

    # Helper to choose serializer depending on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return ListeningActivityQuestionListSerializer
        return ListeningActivityQuestionCreateSerializer

    # ---------------- LIST ----------------
    @has_permission("can_read_listeningquestion")
    @swagger_auto_schema(
        operation_description="List all listening activity questions with pagination",
        responses={200: ListeningActivityQuestionListSerializer(many=True)}
    )
    def list(self, request):
        questions = ListeningActivityQuestion.objects.all().order_by('-id')
        paginator = CustomPageNumberPagination()
        paginated_questions = paginator.paginate_queryset(questions, request)
        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_questions, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    # ---------------- RETRIEVE ----------------
    @has_permission("can_read_listeningquestion")
    @swagger_auto_schema(
        operation_description="Retrieve a single listening activity question by ID",
        responses={200: ListeningActivityQuestionListSerializer()}
    )
    def retrieve(self, request, pk=None):
        question = get_object_or_404(ListeningActivityQuestion, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(question, context={'request': request})
        return Response(serializer.data)

    # ---------------- CREATE ----------------
    @has_permission("can_write_listeningquestion")
    @swagger_auto_schema(
        operation_description="Create a new listening activity question",
        request_body=ListeningActivityQuestionCreateSerializer,
        responses={
            201: ListeningActivityQuestionListSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            response_serializer = ListeningActivityQuestionListSerializer(instance, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- UPDATE (PUT) ----------------
    @has_permission("can_update_listeningquestion")
    @swagger_auto_schema(
        operation_description="Update a listening activity question completely",
        request_body=ListeningActivityQuestionCreateSerializer,
        responses={
            200: ListeningActivityQuestionListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        question = get_object_or_404(ListeningActivityQuestion, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(question, data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            response_serializer = ListeningActivityQuestionListSerializer(instance, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- PARTIAL UPDATE (PATCH) ----------------
    @has_permission("can_update_listeningquestion")
    @swagger_auto_schema(
        operation_description="Partially update a listening activity question",
        request_body=ListeningActivityQuestionCreateSerializer,
        responses={
            200: ListeningActivityQuestionListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        question = get_object_or_404(ListeningActivityQuestion, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(question, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            response_serializer = ListeningActivityQuestionListSerializer(instance, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- DELETE ----------------
    @has_permission("can_delete_listeningquestion")
    @swagger_auto_schema(
        operation_description="Delete a listening activity question",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )
    def destroy(self, request, pk=None):
        question = get_object_or_404(ListeningActivityQuestion, pk=pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @has_permission("can_write_listeningquestion")
    @swagger_auto_schema(
        method='post',
        operation_description="Bulk create ListeningActivityQuestions by type",
        request_body=ListeningActivityQuestionCreateSerializer(many=True),
        responses={201: ListeningActivityQuestionListSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], url_path=r'(?P<question_type>\w+)')
    def create_by_type(self, request, question_type=None):
        """
        Bulk create questions by type.
        URL example: POST /listening-activity-questions/part1/
        """
        if question_type not in LISTENING_CHOICES:
            return Response({"error": f"Invalid type. Valid types: {LISTENING_CHOICES}"},
                            status=status.HTTP_400_BAD_REQUEST)

        questions_data = request.data
        if not isinstance(questions_data, list) or len(questions_data) == 0:
            return Response({"error": "You must provide an array of question objects."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Generate a bundle ID to group this batch
        bundle_id = uuid.uuid4()
        created_questions = []

        with transaction.atomic():
            for item in questions_data:
                item['type'] = question_type      # enforce the type
                item['bundle_id'] = bundle_id     # attach the bundle ID
                serializer = ListeningActivityQuestionCreateSerializer(
                    data=item, context={'request': request}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                created_questions.append(serializer.data)

        return Response({
            "bundle_id": str(bundle_id),
            "questions": created_questions
        }, status=status.HTTP_201_CREATED)
