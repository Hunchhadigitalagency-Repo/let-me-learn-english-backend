from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from cms.models import ContactUs
from cms.serializers.contactus_serializers import ContactUsSerializer
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ContactUsViewSet(viewsets.ViewSet):
    """
    CRUD API for ContactUs model.
    """

    def get_queryset(self):
        return ContactUs.objects.all().order_by('-created_at')

    # ---------------- LIST ----------------
    @swagger_auto_schema(
        operation_description="List all contact messages with pagination (latest first)",
        responses={200: ContactUsSerializer(many=True)}
    )
    def list(self, request):
        queryset = self.get_queryset()

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ContactUsSerializer(
                page, many=True, context={'request': request}
            )
            return paginator.get_paginated_response({
                "message": "Contact messages fetched successfully",
                "data": serializer.data
            })

        serializer = ContactUsSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response({
            "message": "Contact messages fetched successfully",
            "data": serializer.data
        })

    # ---------------- RETRIEVE ----------------
    @swagger_auto_schema(
        operation_description="Retrieve a single contact message by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Contact message ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: ContactUsSerializer(),
            404: "Not Found"
        }
    )
    def retrieve(self, request, pk=None):
        contact = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ContactUsSerializer(
            contact, context={'request': request}
        )
        return Response({
            "message": "Contact message retrieved successfully",
            "data": serializer.data
        })

    # ---------------- CREATE ----------------
    @swagger_auto_schema(
        operation_description="Create a new contact message",
        request_body=ContactUsSerializer,
        responses={
            201: ContactUsSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer = ContactUsSerializer(
            data=request.data, context={'request': request}
        )

        if serializer.is_valid():
            contact = serializer.save()
            return Response({
                "message": "Contact message created successfully",
                "data": ContactUsSerializer(
                    contact, context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- UPDATE (PUT) ----------------
    @swagger_auto_schema(
        operation_description="Update a contact message completely by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Contact message ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=ContactUsSerializer,
        responses={
            200: ContactUsSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        contact = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ContactUsSerializer(
            contact, data=request.data, context={'request': request}
        )

        if serializer.is_valid():
            contact = serializer.save()
            return Response({
                "message": "Contact message updated successfully",
                "data": ContactUsSerializer(
                    contact, context={'request': request}
                ).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- PARTIAL UPDATE (PATCH) ----------------
    @swagger_auto_schema(
        operation_description="Partially update a contact message by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Contact message ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=ContactUsSerializer,
        responses={
            200: ContactUsSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        contact = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ContactUsSerializer(
            contact,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            contact = serializer.save()
            return Response({
                "message": "Contact message partially updated successfully",
                "data": ContactUsSerializer(
                    contact, context={'request': request}
                ).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ---------------- DELETE ----------------
    @swagger_auto_schema(
        operation_description="Delete a contact message by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Contact message ID",
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
        contact = get_object_or_404(self.get_queryset(), pk=pk)
        contact.delete()
        return Response(
            {"message": "Contact message deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
