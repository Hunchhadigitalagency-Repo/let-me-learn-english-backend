from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import Task, SpeakingActivity, speakingActivitySample
from tasks.serializers.task_serializers import TaskSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.decorators import has_permission
# ------------------------------
# Task ViewSet
# ------------------------------
class TaskViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, creating, retrieving, updating, and deleting Tasks
    """
    permission_classes = []  # Define your permissions here
    # List all tasks
    @has_permission("can_read_task")
    @swagger_auto_schema(
        operation_description="List all tasks",
        responses={200: TaskSerializer(many=True)}
    )
    def list(self, request):
        tasks = Task.objects.all().order_by('-id')
        serializer = TaskSerializer(tasks, many=True,context={'request': request})
        return Response(serializer.data)

    # Retrieve single task
    @has_permission("can_read_task")
    @swagger_auto_schema(
        operation_description="Retrieve a single task by ID",
        responses={200: TaskSerializer()}
    )
    def retrieve(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task,context={'request': request})
        return Response(serializer.data)

    # Create new task
    @has_permission("can_write_task")
    @swagger_auto_schema(
        operation_description="Create a new task",
        request_body=TaskSerializer,
        responses={201: TaskSerializer(), 400: "Bad Request"}
    )
    def create(self, request):
        serializer = TaskSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update
    @has_permission("can_update_task")
    @swagger_auto_schema(
        operation_description="Partially update a task",
        request_body=TaskSerializer,
        responses={200: TaskSerializer(), 400: "Bad Request", 404: "Not Found"}
    )
    def partial_update(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete task
    @has_permission("can_delete_task")
    @swagger_auto_schema(
        operation_description="Delete a task",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )
    def destroy(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

