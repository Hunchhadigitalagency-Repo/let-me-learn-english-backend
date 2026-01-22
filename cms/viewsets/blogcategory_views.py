from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from cms.models import BlogCategory
from cms.serializers.blogcategory_serializers import BlogCategoryCreateSerializer, BlogCategoryListSerializer
from utils.paginator import CustomPageNumberPagination

class BlogCategoryViewSet(viewsets.ViewSet):
   

    def get_queryset(self):
        return BlogCategory.objects.all().order_by('-created_at')  # latest first

    def list(self, request):
        queryset = self.get_queryset()

        # Apply pagination
        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = BlogCategoryListSerializer(page, many=True)
            return paginator.get_paginated_response({
                "message": "Blog categories fetched successfully",
                "data": serializer.data
            })

        # If no pagination, return all
        serializer = BlogCategoryListSerializer(queryset, many=True)
        return Response({
            "message": "Blog categories fetched successfully",
            "data": serializer.data
        })

    def retrieve(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = BlogCategoryListSerializer(category)
        return Response({
            "message": "Blog category retrieved successfully",
            "data": serializer.data
        })

    def create(self, request):
        serializer = BlogCategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response({
            "message": "Blog category created successfully",
            "data": BlogCategoryListSerializer(category).data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = BlogCategoryCreateSerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response({
            "message": "Blog category updated successfully",
            "data": BlogCategoryListSerializer(category).data
        })

    def partial_update(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = BlogCategoryCreateSerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response({
            "message": "Blog category partially updated successfully",
            "data": BlogCategoryListSerializer(category).data
        })

    def destroy(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        category.delete()
        return Response({
            "message": "Blog category deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)
