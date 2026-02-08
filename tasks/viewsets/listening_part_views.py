from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from tasks.models import ListeningActivityPart
from tasks.serializers.listening_activity_question_serializers import (
    ListeningActivityPartCreateSerializer,
)
from tasks.serializers.listening_activity_serializers import ListeningActivityPartSerializer
from utils.decorators import has_permission


class ListeningActivityPartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # --------------------------
    # List all parts
    # --------------------------
    @has_permission("can_read_listeningactivitypart")
    @swagger_auto_schema(
        operation_description="List all listening activity parts with nested questions",
        responses={200: ListeningActivityPartSerializer(many=True)}
    )
    def list(self, request):
        parts = ListeningActivityPart.objects.all().order_by('id')
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
    @has_permission("can_write_listeningactivitypart")
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
    @has_permission("can_update_listeningactivitypart")
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