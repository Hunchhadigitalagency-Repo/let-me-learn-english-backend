from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from user.models import UserProfile
from rest_framework.permissions import IsAuthenticated

from user.serializers.auth_serializers import UserSerializer, UserBasicSerializer, AdminRegisterSerializer
User = get_user_model()


class UserDropdownAPIView(APIView):
    """
    Get users for dropdown (id, name, profile)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = (
            User.objects
            .filter(is_active=True)
            .select_related()
            .order_by("id")
        )

        data = []

        for user in users:
            profile = UserProfile.objects.filter(user=user).first()

            # profile image priority
            if profile and profile.profile_picture:
                profile_image = request.build_absolute_uri(
                    profile.profile_picture.url
                )
            elif profile and profile.google_avatar:
                profile_image = profile.google_avatar
            else:
                profile_image = None

            data.append({
                "id": user.id,
                "name": user.get_full_name() or user.email,
                "profile": profile_image
            })

        return Response(data)



from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from utils.paginator import CustomPageNumberPagination



User = get_user_model()


# ---------- swagger query params ----------
page_param = openapi.Parameter(
    "page",
    openapi.IN_QUERY,
    description="Page number",
    type=openapi.TYPE_INTEGER
)

page_size_param = openapi.Parameter(
    "page_size",
    openapi.IN_QUERY,
    description="Page size (max 100). Default depends on paginator (16).",
    type=openapi.TYPE_INTEGER
)

is_active_param = openapi.Parameter(
    "is_active",
    openapi.IN_QUERY,
    description="Filter by active users: true/false",
    type=openapi.TYPE_STRING,
    enum=["true", "false"]
)

user_type_param = openapi.Parameter(
    "user_type",
    openapi.IN_QUERY,
    description="Filter by userprofile.user_type (e.g. admin, parent, student, school, superadmin)",
    type=openapi.TYPE_STRING
)

search_param = openapi.Parameter(
    "search",
    openapi.IN_QUERY,
    description="Search by email or username (icontains)",
    type=openapi.TYPE_STRING
)


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
            qs = qs.filter(email__icontains=search) | qs.filter(username__icontains=search)

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
        operation_description="Returns a paginated list of users. Supports filters and search.",
        manual_parameters=[page_param, page_size_param, is_active_param, user_type_param, search_param],
        responses={200: UserSerializer(many=True)}
    )
    def list(self, request):
        qs = self.get_queryset()
        paginator, page = self.paginate_queryset(qs)
        serializer = UserSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Retrieve a user",
        operation_description="Retrieve a single user by ID.",
        responses={
            200: UserSerializer(),
            404: openapi.Response(description="User not found")
        }
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
            "Creates a user and profile using AdminRegisterSerializer.\n\n"
            "Send as JSON or multipart/form-data (if profile_picture is included).\n"
            "Required: email, first_name, last_name, password, confirm_password."
        ),
        request_body=AdminRegisterSerializer,
        responses={
            201: openapi.Response(description="Created", schema=openapi.Schema(type=openapi.TYPE_OBJECT)),
            400: openapi.Response(description="Validation error")
        }
    )
    def create(self, request):
        serializer = AdminRegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        created_data = serializer.save()
        return Response(created_data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Update user (PUT)",
        operation_description=(
            "Full update of basic user fields.\n\n"
            "⚠️ Your UserBasicSerializer currently requires email, username, password."
        ),
        request_body=UserBasicSerializer,
        responses={
            200: UserSerializer(),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="User not found")
        }
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
        operation_description=(
            "Partial update of basic user fields.\n\n"
            "⚠️ If UserBasicSerializer has required=True for email/username/password, "
            "PATCH still may require them unless you change serializer extra_kwargs."
        ),
        request_body=UserBasicSerializer,
        responses={
            200: UserSerializer(),
            400: openapi.Response(description="Validation error"),
            404: openapi.Response(description="User not found")
        }
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
            404: openapi.Response(description="User not found")
        }
    )
    def destroy(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
