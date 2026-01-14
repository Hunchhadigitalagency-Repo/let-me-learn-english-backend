from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import Task, SpeakingActivity, speakingActivitySample
from tasks.serializers.task_serializers import TaskSerializer

# ------------------------------
# Task ViewSet
# ------------------------------
class TaskViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing, creating, retrieving, updating, and deleting Tasks
    """

    # List all tasks
    def list(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True,context={'request': request})
        return Response(serializer.data)

    # Retrieve single task
    def retrieve(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task,context={'request': request})
        return Response(serializer.data)

    # Create new task
    def create(self, request):
        serializer = TaskSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  

    # Partial update
    def partial_update(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete task
    def destroy(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

