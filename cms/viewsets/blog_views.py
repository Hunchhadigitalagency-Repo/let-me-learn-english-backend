from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from cms.models import Blog
from cms.serializers.blog_serializers import BlogCreateSerializer, BlogListSerializer
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.decorators import has_permission

class BlogViewSet(viewsets.ViewSet):
    lookup_field = 'slug'

    # Helper to choose serializer
    def get_serializer_class(self, action):
        if action in ['list', 'retrieve']:
            return BlogListSerializer
        return BlogCreateSerializer

    def get_queryset(self):
        return Blog.objects.all().order_by('-created_at')

    # ---------------- LIST ----------------
    @has_permission("can_read_blog")
    @swagger_auto_schema(
        operation_description="List all blogs with pagination (latest first)",
        responses={200: BlogListSerializer(many=True)}
    )
    def list(self, request):
        queryset = self.get_queryset()

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer_class = self.get_serializer_class('list')
        serializer = serializer_class(
            paginated_queryset, many=True, context={'request': request}
        )

        return paginator.get_paginated_response({
            "message": "Blogs fetched successfully",
            "data": serializer.data
        })

    # ---------------- RETRIEVE ----------------
    @has_permission("can_read_blog")
    @swagger_auto_schema(
        operation_description="Retrieve a single blog by slug",
        manual_parameters=[
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Blog slug",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: BlogListSerializer(),
            404: "Not Found"
        }
    )
    def retrieve(self, request, slug=None):
        blog = get_object_or_404(self.get_queryset(), slug=slug)
        serializer_class = self.get_serializer_class('retrieve')
        serializer = serializer_class(blog, context={'request': request})

        return Response({
            "message": "Blog retrieved successfully",
            "data": serializer.data
        })

    # ---------------- CREATE ----------------
    @has_permission("can_write_blog")
    @swagger_auto_schema(
        operation_description="Create a new blog",
        request_body=BlogCreateSerializer,
        responses={
            201: BlogListSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer_class = self.get_serializer_class('create')
        serializer = serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid():
            blog = serializer.save()
            return Response({
                "message": "Blog created successfully",
                "data": BlogListSerializer(blog, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- UPDATE (PUT) ----------------
    @has_permission("can_update_blog")
    @swagger_auto_schema(
        operation_description="Update a blog completely by slug",
        manual_parameters=[
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Blog slug",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=BlogCreateSerializer,
        responses={
            200: BlogListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, slug=None):
        blog = get_object_or_404(self.get_queryset(), slug=slug)
        serializer_class = self.get_serializer_class('update')
        serializer = serializer_class(
            blog, data=request.data, context={'request': request}
        )

        if serializer.is_valid():
            blog = serializer.save()
            return Response({
                "message": "Blog updated successfully",
                "data": BlogListSerializer(blog, context={'request': request}).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- PARTIAL UPDATE (PATCH) ----------------
    @has_permission("can_update_blog")
    
    @swagger_auto_schema(
        operation_description="Partially update a blog by slug",
        manual_parameters=[
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Blog slug",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=BlogCreateSerializer,
        responses={
            200: BlogListSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, slug=None):
        blog = get_object_or_404(self.get_queryset(), slug=slug)
        serializer_class = self.get_serializer_class('partial_update')
        serializer = serializer_class(
            blog, data=request.data, partial=True, context={'request': request}
        )

        if serializer.is_valid():
            blog = serializer.save()
            return Response({
                "message": "Blog partially updated successfully",
                "data": BlogListSerializer(blog, context={'request': request}).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- DELETE ----------------
    @has_permission("can_delete_blog")
    @swagger_auto_schema(
        operation_description="Delete a blog by slug",
        manual_parameters=[
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Blog slug",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: "Deleted successfully",
            404: "Not Found"
        }
    )
    def destroy(self, request, slug=None):
        blog = get_object_or_404(self.get_queryset(), slug=slug)
        blog.delete()
        return Response(
            {"message": "Blog deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
