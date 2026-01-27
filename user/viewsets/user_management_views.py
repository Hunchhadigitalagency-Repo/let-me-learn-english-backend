from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from user.models import UserProfile
from user.serializers.auth_serializers import (
    UserSerializer,
    UserBasicSerializer,
    AdminRegisterSerializer,
)
from utils.paginator import CustomPageNumberPagination


User = get_user_model()


# ---------------- Swagger query params ----------------
page_param = openapi.Parameter(
    "page", openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER
)

page_size_param = openapi.Parameter(
    "page_size", openapi.IN_QUERY, description="Page size (max 100). Default 16.", type=openapi.TYPE_INTEGER
)

is_active_param = openapi.Parameter(
    "is_active",
    openapi.IN_QUERY,
    description="Filter by is_active: true/false",
    type=openapi.TYPE_STRING,
    enum=["true", "false"],
)

user_type_param = openapi.Parameter(
    "user_type",
    openapi.IN_QUERY,
    description="Filter by userprofile.user_type (admin, parent, student, school, superadmin)",
    type=openapi.TYPE_STRING,
)

search_param = openapi.Parameter(
    "search",
    openapi.IN_QUERY,
    description="Search by email/username (icontains)",
    type=openapi.TYPE_STRING,
)


# ---------------- Swagger response schemas (match your paginator) ----------------
PAGINATED_USER_LIST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "links": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "next": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                "previous": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
            },
        ),
        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total items"),
        "page_size": openapi.Schema(type=openapi.TYPE_INTEGER),
        "total_pages": openapi.Schema(type=openapi.TYPE_INTEGER),
        "current_page": openapi.Schema(type=openapi.TYPE_INTEGER),
        "results": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_OBJECT),
        ),
    },
    required=["links", "count", "page_size", "total_pages", "current_page", "results"],
)

USER_DROPDOWN_SCHEMA = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
            "name": openapi.Schema(type=openapi.TYPE_STRING),
            "profile": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
        },
        required=["id", "name", "profile"],
    ),
)


class UserDropdownAPIView(APIView):
    """
    Get users for dropdown (id, name, profile)
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="User dropdown list",
        operation_description="Returns simple list for dropdown (id, name, profile_image).",
        responses={
            200: openapi.Response(description="OK", schema=USER_DROPDOWN_SCHEMA),
            401: "Unauthorized",
        },
        tags=["User"],
    )
    def get(self, request):
        users = (
            User.objects
            .filter(is_active=True)
            .select_related("userprofile")
            .order_by("id")
        )

        data = []
        for user in users:
            profile = getattr(user, "userprofile", None)

            if profile and profile.profile_picture:
                profile_image = request.build_absolute_uri(profile.profile_picture.url)
            elif profile and profile.google_avatar:
                profile_image = profile.google_avatar
            else:
                profile_image = None

            data.append({
                "id": user.id,
                "name": user.get_full_name() or user.email,
                "profile": profile_image
            })

        return Response(data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = CustomPageNumberPagination

    # ---------- helpers ----------
    def get_queryset(self):
        qs = (
            User.objects
            .all()
            .select_related("userprofile")
            .order_by("id")
        )

        is_active = self.request.query_params.get("is_active")
        if is_active in ["true", "false"]:
            qs = qs.filter(is_active=(is_active == "true"))

        user_type = self.request.query_params.get("user_type")
        if user_type:
            qs = qs.filter(userprofile__user_type=user_type)

        search = self.request.query_params.get("search")
        if search:
            s = search.strip()
            qs = qs.filter(Q(email__icontains=s) | Q(username__icontains=s))

        return qs

    def get_object(self, pk):
        return self.get_queryset().get(pk=pk)

    def paginate_queryset(self, queryset):
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, self.request, view=self)
        return paginator, page

    # ---------- methods ----------
    @swagger_auto_schema(
        operation_summary="List users (paginated)",
        operation_description="Paginated list. Uses CustomPageNumberPagination. Supports filters + search via query params.",
        manual_parameters=[page_param, page_size_param, is_active_param, user_type_param, search_param],
        responses={
            200: openapi.Response(description="OK", schema=PAGINATED_USER_LIST_SCHEMA),
            401: "Unauthorized",
        },
        tags=["User"],
    )
    def list(self, request):
        qs = self.get_queryset()
        paginator, page = self.paginate_queryset(qs)
        serializer = UserSerializer(page, many=True, context={"request": request})
        # ✅ paginator response as-is
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Retrieve user by ID",
        responses={
            200: openapi.Response(description="OK", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            404: openapi.Response(description="User not found"),
            401: "Unauthorized",
        },
        tags=["User"],
    )
    def retrieve(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create user (admin create)",
        operation_description=(
            "Creates a user + profile using AdminRegisterSerializer.\n"
            "Send JSON or multipart/form-data (if profile_picture included).\n"
            "Required: email, first_name, last_name, password, confirm_password."
        ),
        request_body=AdminRegisterSerializer,
        responses={
            201: openapi.Response(description="Created", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response(description="Validation error"),
            401: "Unauthorized",
        },
        tags=["User"],
    )
    def create(self, request):
        serializer = AdminRegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        created_data = serializer.save()  # your serializer returns data
        return Response(created_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Update user (PUT)",
        operation_description="Full update using UserBasicSerializer.",
        request_body=UserBasicSerializer,
        responses={
            200: openapi.Response(description="OK", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="User not found"),
            401: "Unauthorized",
        },
        tags=["User"],
    )
    def update(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserBasicSerializer(user, data=request.data, partial=False, context={"request": request})
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        password = validated.pop("password", None)

        for attr, value in validated.items():
            setattr(user, attr, value)

        if password:
            user.set_password(password)

        user.save()
        out = UserSerializer(user, context={"request": request}).data
        return Response(out, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Partial update user (PATCH)",
        operation_description="Partial update using UserBasicSerializer.",
        request_body=UserBasicSerializer,
        responses={
            200: openapi.Response(description="OK", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="User not found"),
            401: "Unauthorized",
        },
        tags=["User"],
    )
    def partial_update(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserBasicSerializer(user, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        password = validated.pop("password", None)

        for attr, value in validated.items():
            setattr(user, attr, value)

        if password:
            user.set_password(password)

        user.save()
        out = UserSerializer(user, context={"request": request}).data
        return Response(out, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Delete user",
        operation_description="Deletes a user by ID.",
        responses={
            204: openapi.Response(description="Deleted"),
            404: openapi.Response(description="User not found"),
            401: "Unauthorized",
        },
        tags=["User"],
    )
    def destroy(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
