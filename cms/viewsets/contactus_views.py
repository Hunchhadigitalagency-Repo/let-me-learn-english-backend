from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from cms.models import ContactUs
from cms.serializers.contactus_serializers import ContactUsSerializer
from utils.paginator import CustomPageNumberPagination

class ContactUsViewSet(viewsets.ViewSet):
    """
    CRUD API for ContactUs model.
    """

    def get_queryset(self):
        return ContactUs.objects.all().order_by('-created_at')

    # List with pagination
    def list(self, request):
        queryset = self.get_queryset()
        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = ContactUsSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response({
                "message": "Contact messages fetched successfully",
                "data": serializer.data
            })

        serializer = ContactUsSerializer(queryset, many=True, context={'request': request})
        return Response({
            "message": "Contact messages fetched successfully",
            "data": serializer.data
        })

    # Retrieve single contact message
    def retrieve(self, request, pk=None):
        contact = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ContactUsSerializer(contact, context={'request': request})
        return Response({
            "message": "Contact message retrieved successfully",
            "data": serializer.data
        })

    # Create contact message
    def create(self, request):
        serializer = ContactUsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        return Response({
            "message": "Contact message created successfully",
            "data": ContactUsSerializer(contact, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)

    # Full update
    def update(self, request, pk=None):
        contact = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ContactUsSerializer(contact, data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        return Response({
            "message": "Contact message updated successfully",
            "data": ContactUsSerializer(contact, context={'request': request}).data
        })

    # Partial update
    def partial_update(self, request, pk=None):
        contact = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ContactUsSerializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        return Response({
            "message": "Contact message partially updated successfully",
            "data": ContactUsSerializer(contact, context={'request': request}).data
        })

    # Delete contact message
    def destroy(self, request, pk=None):
        contact = get_object_or_404(self.get_queryset(), pk=pk)
        contact.delete()
        return Response({
            "message": "Contact message deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)
