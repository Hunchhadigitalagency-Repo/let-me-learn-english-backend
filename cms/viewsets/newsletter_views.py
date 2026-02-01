from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from cms.models import Newsletters
from cms.serializers.newsletter_serializers import (
    NewsletterCreateSerializer,
    NewsletterListSerializer
)
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.decorators import has_permission

class NewsletterViewSet(viewsets.ViewSet):

    def get_queryset(self):
        return Newsletters.objects.all().order_by('-id')

    # ---------------- LIST ----------------
    @has_permission("can_read_newsletter")
    @swagger_auto_schema(
        operation_description="List all newsletters with pagination (latest first)",
        responses={200: NewsletterListSerializer(many=True)}
    )
    def list(self, request):
        queryset = self.get_queryset()

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = NewsletterListSerializer(page, many=True)
            return paginator.get_paginated_response({
                "message": "Newsletters fetched successfully",
                "data": serializer.data
            })

        serializer = NewsletterListSerializer(queryset, many=True)
        return Response({
            "message": "Newsletters fetched successfully",
            "data": serializer.data
        })

    # ---------------- RETRIEVE ----------------
    @has_permission("can_read_newsletter")
    @swagger_auto_schema(
        operation_description="Retrieve a single newsletter by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Newsletter ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: NewsletterListSerializer(),
            404: "Not Found"
        }
    )
    def retrieve(self, request, pk=None):
        newsletter = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = NewsletterListSerializer(newsletter)
        return Response({
            "message": "Newsletter retrieved successfully",
            "data": serializer.data
        })

    # ---------------- CREATE ----------------
    @has_permission("can_write_newsletter")
    @swagger_auto_schema(
        operation_description="Create a new newsletter",
        request_body=NewsletterCreateSerializer,
        responses={
            201: NewsletterListSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer = NewsletterCreateSerializer(data=request.data)

        if serializer.is_valid():
            newsletter = serializer.save()
            return Response({
                "message": "Newsletter created successfully",
                "data": NewsletterListSerializer(newsletter).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- UPDATE (PUT) ----------------
    @has_permission("can_update_newsletter")
    @swagger_auto_schema(
        operation_description="Update a newsletter completely by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Newsletter ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=NewsletterCreateSerializer,
        responses={
            200: NewsletterListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        newsletter = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = NewsletterCreateSerializer(newsletter, data=request.data)

        if serializer.is_valid():
            newsletter = serializer.save()
            return Response({
                "message": "Newsletter updated successfully",
                "data": NewsletterListSerializer(newsletter).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- PARTIAL UPDATE (PATCH) ----------------
    @has_permission("can_update_newsletter")
    @swagger_auto_schema(
        operation_description="Partially update a newsletter by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Newsletter ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=NewsletterCreateSerializer,
        responses={
            200: NewsletterListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        newsletter = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = NewsletterCreateSerializer(
            newsletter, data=request.data, partial=True
        )

        if serializer.is_valid():
            newsletter = serializer.save()
            return Response({
                "message": "Newsletter partially updated successfully",
                "data": NewsletterListSerializer(newsletter).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- DELETE ----------------
    @has_permission("can_delete_newsletter")
    @swagger_auto_schema(
        operation_description="Delete a newsletter by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Newsletter ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Deleted successfully",
            404: "Not Found"
        }
    )
    def destroy(self, request, pk=None):
        newsletter = get_object_or_404(self.get_queryset(), pk=pk)
        newsletter.delete()
        return Response(
            {"message": "Newsletter deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
