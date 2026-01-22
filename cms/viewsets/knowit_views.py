from rest_framework import viewsets, status
from rest_framework.response import Response
from cms.models import NowKnowIt
from cms.serializers.knowit_serializers import NowKnowItSerializer
from utils.paginator import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class NowKnowItViewSet(viewsets.ViewSet):
    """
    CRUD API for NowKnowIt model.
    """

    # ---------------- LIST ----------------
    @swagger_auto_schema(
        operation_description="List all NowKnowIt items with pagination",
        responses={200: NowKnowItSerializer(many=True)}
    )
    def list(self, request):
        queryset = NowKnowIt.objects.all()

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = NowKnowItSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # ---------------- RETRIEVE ----------------
    @swagger_auto_schema(
        operation_description="Retrieve a single NowKnowIt item by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="NowKnowIt ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: NowKnowItSerializer(),
            404: "Not Found"
        }
    )
    def retrieve(self, request, pk=None):
        try:
            instance = NowKnowIt.objects.get(pk=pk)
        except NowKnowIt.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NowKnowItSerializer(instance)
        return Response(serializer.data)

    # ---------------- CREATE ----------------
    @swagger_auto_schema(
        operation_description="Create a new NowKnowIt item",
        request_body=NowKnowItSerializer,
        responses={
            201: NowKnowItSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer = NowKnowItSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # ---------------- UPDATE (PUT) ----------------
    @swagger_auto_schema(
        operation_description="Update a NowKnowIt item completely by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="NowKnowIt ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=NowKnowItSerializer,
        responses={
            200: NowKnowItSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, pk=None):
        try:
            instance = NowKnowIt.objects.get(pk=pk)
        except NowKnowIt.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NowKnowItSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # ---------------- PARTIAL UPDATE (PATCH) ----------------
    @swagger_auto_schema(
        operation_description="Partially update a NowKnowIt item by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="NowKnowIt ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=NowKnowItSerializer,
        responses={
            200: NowKnowItSerializer(),
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def partial_update(self, request, pk=None):
        try:
            instance = NowKnowIt.objects.get(pk=pk)
        except NowKnowIt.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NowKnowItSerializer(
            instance,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # ---------------- DELETE ----------------
    @swagger_auto_schema(
        operation_description="Delete a NowKnowIt item by ID",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="NowKnowIt ID",
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
        try:
            instance = NowKnowIt.objects.get(pk=pk)
        except NowKnowIt.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        instance.delete()
        return Response(
            {"detail": "Deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
