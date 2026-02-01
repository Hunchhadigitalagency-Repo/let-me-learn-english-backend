from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from student.models import StudentAttempts
from student.serializers.studentattempts_serializers import StudentAttemptsCreateSerializer, StudentAttemptsListSerializer
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from utils.decorators import has_permission
class StudentAttemptsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
   
    @has_permission("can_read_studentattempts")
    def list(self, request):
        queryset = StudentAttempts.objects.all().order_by('-started_at')

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = StudentAttemptsListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response({
                "message": "Student attempts fetched successfully",
                "data": serializer.data
            })

        serializer = StudentAttemptsListSerializer(queryset, many=True, context={'request': request})
        return Response({
            "message": "Student attempts fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)



    # RETRIEVE
    @has_permission("can_read_studentattempts")
    def retrieve(self, request, pk=None):
        try:
            attempt = StudentAttempts.objects.get(pk=pk)
        except StudentAttempts.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentAttemptsListSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # CREATE
    @has_permission("can_write_studentattempts")
    def create(self, request):
        serializer = StudentAttemptsCreateSerializer(data=request.data)
        if serializer.is_valid():
           
            if not serializer.validated_data.get('student'):
                serializer.save(student=request.user)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # UPDATE / PATCH
    @has_permission("can_update_studentattempts")
    def update(self, request, pk=None):
        try:
            attempt = StudentAttempts.objects.get(pk=pk)
        except StudentAttempts.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentAttemptsCreateSerializer(attempt, data=request.data, partial=False)
        if serializer.is_valid():
            instance = serializer.save()
           
            if instance.status.lower() == 'completed' and not instance.submitted_at:
                instance.submitted_at = timezone.now()
                instance.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PARTIAL UPDATE
    @has_permission("can_update_studentattempts")
    def partial_update(self, request, pk=None):
        try:
            attempt = StudentAttempts.objects.get(pk=pk)
        except StudentAttempts.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentAttemptsCreateSerializer(attempt, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            if instance.status.lower() == 'completed' and not instance.submitted_at:
                instance.submitted_at = timezone.now()
                instance.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    @has_permission("can_delete_studentattempts")
    def destroy(self, request, pk=None):
        try:
            attempt = StudentAttempts.objects.get(pk=pk)
        except StudentAttempts.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        attempt.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
