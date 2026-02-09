from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from tasks.models import ListeningActivity, ListeningActivityPart
from tasks.serializers.listening_activity_question_serializers import (
    ListeningActivityPartCreateSerializer,
)
from tasks.serializers.listening_activity_serializers import ListeningActivityPartSerializer
from utils.decorators import has_permission


class ListeningActivityPartViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    # --------------------------
    # List all parts with filters
    # --------------------------
    @has_permission("can_read_listeningactivitypart")
    @swagger_auto_schema(
        operation_description="List all listening activity parts with optional filters by task or part type",
        manual_parameters=[
            openapi.Parameter(
                name='task_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description='Filter parts by ListeningActivity task ID'
            ),
            openapi.Parameter(
                name='part',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description='Filter parts by part type (e.g., Part1-Conversation)'
            )
        ],
        responses={200: ListeningActivityPartSerializer(many=True)}
    )
    def list(self, request):
        parts = ListeningActivityPart.objects.all().order_by('id')

        # Filter by task_id: get all ListeningActivity for that task
        task_id = request.query_params.get('task_id')
        if task_id:
            activities = ListeningActivity.objects.filter(task_id=task_id)
            parts = parts.filter(listening_activity__in=activities)

        # Optional filter by part type
        part_type = request.query_params.get('part')
        if part_type:
            parts = parts.filter(part=part_type)

        serializer = ListeningActivityPartSerializer(parts, many=True, context={'request': request})
        return Response(serializer.data)

    # --------------------------
    # Retrieve a single part
    # --------------------------
    @has_permission("can_read_listeningactivitypart")
    @swagger_auto_schema(
        operation_description="Retrieve a single listening activity part",
        responses={200: ListeningActivityPartSerializer()}
    )
    def retrieve(self, request, pk=None):
        part = get_object_or_404(ListeningActivityPart, pk=pk)
        serializer = ListeningActivityPartSerializer(part, context={'request': request})
        return Response(serializer.data)

    # --------------------------
    # Create a part + nested questions
    # --------------------------
    # @has_permission("can_write_listeningactivitypart")
    @swagger_auto_schema(
        operation_description="Create a listening activity part with questions",
        request_body=ListeningActivityPartCreateSerializer,
        responses={201: ListeningActivityPartSerializer(), 400: "Bad Request"}
    )
    def create(self, request):
        serializer = ListeningActivityPartCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            part = serializer.save()
            output_serializer = ListeningActivityPartSerializer(part, context={'request': request})
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # Update a part (PUT) + nested questions
    # --------------------------
    @has_permission("can_update_listeningactivitypart")
    @swagger_auto_schema(
        operation_description="Update a listening activity part and replace all its questions",
        request_body=ListeningActivityPartCreateSerializer,
        responses={200: ListeningActivityPartSerializer(), 400: "Bad Request"}
    )
    def update(self, request, pk=None):
        part = get_object_or_404(ListeningActivityPart, pk=pk)
        serializer = ListeningActivityPartCreateSerializer(part, data=request.data, context={'request': request})
        if serializer.is_valid():
            part = serializer.save()  # Nested questions replaced automatically
            output_serializer = ListeningActivityPartSerializer(part, context={'request': request})
            return Response(output_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # Partial update (PATCH) + nested questions
    # --------------------------
    # @has_permission("can_update_listeningactivitypart")
    @swagger_auto_schema(
        operation_description="Partially update a listening activity part and replace its questions",
        request_body=ListeningActivityPartCreateSerializer,
        responses={200: ListeningActivityPartSerializer(), 400: "Bad Request"}
    )
    def partial_update(self, request, pk=None):
        part = get_object_or_404(ListeningActivityPart, pk=pk)
        serializer = ListeningActivityPartCreateSerializer(part, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            part = serializer.save()
            output_serializer = ListeningActivityPartSerializer(part, context={'request': request})
            return Response(output_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --------------------------
    # Delete a part + its questions
    # --------------------------
    @has_permission("can_delete_listeningactivitypart")
    @swagger_auto_schema(
        operation_description="Delete a listening activity part and all its questions",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )
    def destroy(self, request, pk=None):
        part = get_object_or_404(ListeningActivityPart, pk=pk)
        part.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)