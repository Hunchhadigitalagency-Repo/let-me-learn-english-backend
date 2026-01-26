from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from cms.models import BlogCategory
from cms.serializers.blogcategory_serializers import (
    BlogCategoryCreateSerializer,
    BlogCategoryListSerializer
)
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action

class BlogCategoryViewSet(viewsets.ViewSet):

    def get_queryset(self):
        return BlogCategory.objects.all().order_by('-created_at')

    # ---------------- LIST ----------------
    @swagger_auto_schema(
        operation_description="List all blog categories with pagination (latest first)",
        responses={200: BlogCategoryListSerializer(many=True)}
    )
    def list(self, request):
        queryset = self.get_queryset()

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = BlogCategoryListSerializer(page, many=True)
            return paginator.get_paginated_response({
                "message": "Blog categories fetched successfully",
                "data": serializer.data
            })

        serializer = BlogCategoryListSerializer(queryset, many=True)
        return Response({
            "message": "Blog categories fetched successfully",
            "data": serializer.data
        })

    # ---------------- RETRIEVE ----------------
    @swagger_auto_schema(
        operation_description="Retrieve a single blog category by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Blog category ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: BlogCategoryListSerializer(),
            404: "Not Found"
        }
    )
    def retrieve(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = BlogCategoryListSerializer(category)
        return Response({
            "message": "Blog category retrieved successfully",
            "data": serializer.data
        })

    # ---------------- CREATE ----------------
    @swagger_auto_schema(
        operation_description="Create a new blog category",
        request_body=BlogCategoryCreateSerializer,
        responses={
            201: BlogCategoryListSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer = BlogCategoryCreateSerializer(data=request.data)

        if serializer.is_valid():
            category = serializer.save()
            return Response({
                "message": "Blog category created successfully",
                "data": BlogCategoryListSerializer(category).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- UPDATE (PUT) ----------------
    @swagger_auto_schema(
        operation_description="Update a blog category completely by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Blog category ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=BlogCategoryCreateSerializer,
        responses={
            200: BlogCategoryListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = BlogCategoryCreateSerializer(category, data=request.data)

        if serializer.is_valid():
            category = serializer.save()
            return Response({
                "message": "Blog category updated successfully",
                "data": BlogCategoryListSerializer(category).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- PARTIAL UPDATE (PATCH) ----------------
    @swagger_auto_schema(
        operation_description="Partially update a blog category by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Blog category ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=BlogCategoryCreateSerializer,
        responses={
            200: BlogCategoryListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = BlogCategoryCreateSerializer(
            category, data=request.data, partial=True
        )

        if serializer.is_valid():
            category = serializer.save()
            return Response({
                "message": "Blog category partially updated successfully",
                "data": BlogCategoryListSerializer(category).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- DELETE ----------------
    @swagger_auto_schema(
        operation_description="Delete a blog category by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Blog category ID",
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
        category = get_object_or_404(self.get_queryset(), pk=pk)
        category.delete()
        return Response(
            {"message": "Blog category deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

        
    @swagger_auto_schema(
        operation_description="Get blog categories for dropdown (no pagination)",
        responses={200: BlogCategoryListSerializer(many=True)}
    )   
    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request):
        queryset = self.get_queryset().order_by("name")  # better UX

        serializer = BlogCategoryListSerializer(
            queryset,
            many=True,
            context={"request": request}
        )

        return Response({serializer.data})
