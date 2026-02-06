# tasks/viewsets/writing_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import WritingActivity
from tasks.serializers.writing_activity_serializers import (
    WritingActivityCreateSerializer,
    WritingActivityListSerializer
)
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.decorators import has_permission
class WritingActivityViewSet(viewsets.ViewSet):
    """
    CRUD ViewSet for WritingActivity with dynamic serializers and pagination.
    """

    # Helper to select serializer based on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return WritingActivityListSerializer
        return WritingActivityCreateSerializer

    # List all writing activities with pagination
    @has_permission("can_read_writingactivity")
    @swagger_auto_schema(
        operation_description="List all writing activities with pagination",
        responses={200: WritingActivityListSerializer(many=True)}
    )
    def list(self, request):
        activities = WritingActivity.objects.all().order_by('-id')
        paginator = CustomPageNumberPagination()
        paginated_activities = paginator.paginate_queryset(activities, request)

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_activities, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    # Retrieve a single writing activity
    @has_permission("can_read_writingactivity")
    @swagger_auto_schema(
        operation_description="Retrieve a single writing activity by ID",
        responses={200: WritingActivityListSerializer()}
    )
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(activity, context={'request': request})
        return Response(serializer.data)

    # Create a new writing activity
    @has_permission("can_create_writingactivity")
    @swagger_auto_schema(
        operation_description="Create a new writing activity",
        request_body=WritingActivityCreateSerializer,
        responses={201: WritingActivityListSerializer(), 400: "Bad Request"}
    )
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a writing activity completely (PUT)
    @has_permission("can_update_writingactivity")
    @swagger_auto_schema(
        operation_description="Update a writing activity completely (PUT)",
        request_body=WritingActivityCreateSerializer,
        responses={200: WritingActivityListSerializer(), 400: "Bad Request", 404: "Not Found"}
    )
    def update(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(activity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    @has_permission("can_update_writingactivity")
    @swagger_auto_schema(
        operation_description="Partially update a writing activity (PATCH)",
        request_body=WritingActivityCreateSerializer,
        responses={200: WritingActivityListSerializer(), 400: "Bad Request", 404: "Not Found"}
    )
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(activity, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a writing activity
    @has_permission("can_delete_writingactivity")
    @swagger_auto_schema(
        operation_description="Delete a writing activity",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )
    def destroy(self, request, pk=None):
        activity = get_object_or_404(WritingActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @has_permission("can_read_writingactivity")
    @action(detail=False, methods=["get"], url_path=r"by-task/(?P<task_id>[^/.]+)")
    @swagger_auto_schema(
        operation_description="Retrieve the writing activity for a given task ID",
        manual_parameters=[
            openapi.Parameter(
                name="task_id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Task ID to fetch writing activity for",
            )
        ],
        responses={200: WritingActivityListSerializer(), 404: "Not Found", 409: "Conflict"},
    )
    def by_task_id(self, request, task_id=None):
        """
        Return the writing activity for the given task_id.
        Route: /writing-activities/by-task/{task_id}/
        """
        qs = WritingActivity.objects.filter(task_id=task_id).order_by("-id")
        if not qs.exists():
            return Response(
                {"detail": "Writing activity not found for the given task_id"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if qs.count() > 1:
            return Response(
                {
                    "detail": "Multiple writing activities found for the given task_id. Expected only one."
                },
                status=status.HTTP_409_CONFLICT,
            )
        activity = qs.first()
        serializer_class = self.get_serializer_class("retrieve")
        serializer = serializer_class(activity, context={"request": request})
        return Response(serializer.data)
