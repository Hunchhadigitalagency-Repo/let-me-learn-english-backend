from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import Task, SpeakingActivity, speakingActivitySample, UserTaskProgress
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

    # Get next task for the authenticated user based on grade and progress
    @action(detail=False, methods=['get'], url_path='next-task')
    @swagger_auto_schema(
        operation_description="Get the next task for the authenticated user based on their grade and progress",
        responses={200: TaskSerializer(), 404: "No tasks available"}
    )
    def get_next_task(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not hasattr(user, 'userprofile') or not user.userprofile.grade:
            return Response(
                {"detail": "User grade is not set"},
                status=status.HTTP_400_BAD_REQUEST
            )

        grade = user.userprofile.grade

        # Check if the user has an incomplete task (not all activities done)
        incomplete_progress = (
            UserTaskProgress.objects
            .filter(user_id=user.id, task__grade=grade)
            .exclude(
                did_completed_speaking_activity=True,
                did_completed_reading_activity=True,
                did_completed_listening_activity=True,
                did_completed_writing_activity=True,
            )
            .order_by('-task__id')
            .first()
        )

        if incomplete_progress:
            # User still has an in-progress task — return it with progress data
            serializer = TaskSerializer(incomplete_progress.task, context={'request': request})
            return Response({
                **serializer.data,
                "progress": {
                    "id": incomplete_progress.id,
                    "did_completed_speaking_activity": incomplete_progress.did_completed_speaking_activity,
                    "did_completed_reading_activity": incomplete_progress.did_completed_reading_activity,
                    "did_completed_listening_activity": incomplete_progress.did_completed_listening_activity,
                    "did_completed_writing_activity": incomplete_progress.did_completed_writing_activity,
                    "last_updated": incomplete_progress.last_updated,
                },
            })

        # All previous tasks are fully completed — find the last one
        last_progress = (
            UserTaskProgress.objects
            .filter(user_id=user.id, task__grade=grade)
            .order_by('-task__id')
            .first()
        )

        if last_progress:
            # Get the next task after the last completed one
            next_task = (
                Task.objects
                .filter(grade=grade, id__gt=last_progress.task_id)
                .order_by('id')
                .first()
            )
        else:
            # No progress yet — return the first task for this grade
            next_task = (
                Task.objects
                .filter(grade=grade)
                .order_by('id')
                .first()
            )

        if not next_task:
            return Response(
                {"detail": "No more tasks available for this grade"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TaskSerializer(next_task, context={'request': request})
        return Response(serializer.data)

