from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from cms.models import Blog
from cms.serializers.blog_serializers import BlogCreateSerializer, BlogListSerializer
from utils.paginator import CustomPageNumberPagination

class BlogViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]  # uncomment if you want auth
    lookup_field = 'slug'  # use slug instead of pk

    def get_queryset(self):
        return Blog.objects.all().order_by('-created_at')  # latest blogs first

    # List with pagination
    def list(self, request):
        queryset = self.get_queryset()
        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = BlogListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response({
                "message": "Blogs fetched successfully",
                "data": serializer.data
            })

        serializer = BlogListSerializer(queryset, many=True, context={'request': request})
        return Response({
            "message": "Blogs fetched successfully",
            "data": serializer.data
        })

    # Retrieve single blog by slug
    def retrieve(self, request, slug=None):
        blog = get_object_or_404(self.get_queryset(), slug=slug)
        serializer = BlogListSerializer(blog, context={'request': request})
        return Response({
            "message": "Blog retrieved successfully",
            "data": serializer.data
        })

    # Create blog
    def create(self, request):
        serializer = BlogCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        blog = serializer.save()
        return Response({
            "message": "Blog created successfully",
            "data": BlogListSerializer(blog, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)

    # Full update by slug
    def update(self, request, slug=None):
        blog = get_object_or_404(self.get_queryset(), slug=slug)
        serializer = BlogCreateSerializer(blog, data=request.data)
        serializer.is_valid(raise_exception=True)
        blog = serializer.save()
        return Response({
            "message": "Blog updated successfully",
            "data": BlogListSerializer(blog, context={'request': request}).data
        })

    # Partial update by slug
    def partial_update(self, request, slug=None):
        blog = get_object_or_404(self.get_queryset(), slug=slug)
        serializer = BlogCreateSerializer(blog, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        blog = serializer.save()
        return Response({
            "message": "Blog partially updated successfully",
            "data": BlogListSerializer(blog, context={'request': request}).data
        })

    # Delete blog by slug
    def destroy(self, request, slug=None):
        blog = get_object_or_404(self.get_queryset(), slug=slug)
        blog.delete()
        return Response({
            "message": "Blog deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)



