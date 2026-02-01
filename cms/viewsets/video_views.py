from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from cms.models import Videos
from cms.serializers.video_serializers import VideoCreateSerializer, VideoListSerializer
from utils.paginator import CustomPageNumberPagination
from utils.decorators import has_permission

class VideoViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    # GET /videos/
    @has_permission("can_read_video")
    def list(self, request):
        queryset = Videos.objects.all().order_by('-created_at')

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = VideoListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response({
                "message": "Videos fetched successfully",
                "data": serializer.data
            })

        serializer = VideoListSerializer(queryset, many=True, context={'request': request})
        return Response({
            "message": "Videos fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # POST /videos/
    @has_permission("can_write_video")
    def create(self, request):
        serializer = VideoCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Video uploaded successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET /videos/{id}/
    @has_permission("can_read_video")
    
    def retrieve(self, request, pk=None):
        video = get_object_or_404(Videos, pk=pk)
        serializer = VideoListSerializer(video, context={'request': request})
        return Response({
            "message": "Video fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # PATCH /videos/{id}/
    @has_permission("can_update_video")
    def partial_update(self, request, pk=None):
        video = get_object_or_404(Videos, pk=pk)
        serializer = VideoCreateSerializer(
            video,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Video updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /videos/{id}/
    @has_permission("can_delete_video")
    def destroy(self, request, pk=None):
        video = get_object_or_404(Videos, pk=pk)
        video.delete()
        return Response({
            "message": "Video deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)
