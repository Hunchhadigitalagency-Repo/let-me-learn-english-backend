# tasks/viewsets/listening_views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tasks.models import ListeningActivity
from tasks.serializers.listening_activity_serializers import (
    ListeningActivityCreateSerializer,
    ListeningActivityListSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.paginator import CustomPageNumberPagination
from utils.decorators import has_permission
class ListeningActivityViewSet(viewsets.ViewSet):
    
    # Helper to choose serializer depending on action
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return ListeningActivityListSerializer
        return ListeningActivityCreateSerializer

    @has_permission("can_read_listeningactivity")
    @swagger_auto_schema(
        operation_description="List all listening activities with pagination",
        responses={200: ListeningActivityListSerializer(many=True)}
    )
    def list(self, request):
        activities = ListeningActivity.objects.all().order_by('-id')
        
        # Apply custom pagination
        paginator = CustomPageNumberPagination()
        paginated_activities = paginator.paginate_queryset(activities, request)
        
        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(paginated_activities, many=True, context={'request': request})
        
        # Return paginated response using your CustomPageNumberPagination
        return paginator.get_paginated_response(serializer.data)



    # Retrieve a single listening activity
    @has_permission("can_read_listeningactivity")
    @swagger_auto_schema(
        operation_description="Retrieve a single listening activity question by ID",
        responses={200: ListeningActivityListSerializer()}
    )
    def retrieve(self, request, pk=None):
        activity = get_object_or_404(ListeningActivity, pk=pk)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(activity, context={'request': request})
        return Response(serializer.data)

    # Create a new listening activity
    @has_permission("can_write_listeningactivity")
    @swagger_auto_schema(
        operation_description="Create a new listening activity question",
        request_body=ListeningActivityCreateSerializer,
        responses={
            201: ListeningActivityListSerializer(),
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

    # Update a listening activity completely (PUT)
    @has_permission("can_update_listeningactivity")
    @swagger_auto_schema(
        operation_description="Update a listening activity question completely",
        request_body=ListeningActivityCreateSerializer,
        responses={
            200: ListeningActivityListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        activity = get_object_or_404(ListeningActivity, pk=pk)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(activity, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Partial update (PATCH)
    @has_permission("can_update_listeningactivity")
    
    @swagger_auto_schema(
        operation_description="Partially update a listening activity question",
        request_body=ListeningActivityCreateSerializer,
        responses={
            200: ListeningActivityListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        activity = get_object_or_404(ListeningActivity, pk=pk)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(activity, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a listening activity
    @has_permission("can_delete_listeningactivity")
    @swagger_auto_schema(
        operation_description="Delete a listening activity question",
        responses={204: "Deleted successfully", 404: "Not Found"}
    )

    def destroy(self, request, pk=None):
        activity = get_object_or_404(ListeningActivity, pk=pk)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
