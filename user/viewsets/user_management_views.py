from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from user.models import UserProfile
from rest_framework.permissions import IsAuthenticated
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


from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from utils.paginator import CustomPageNumberPagination
from user.serializers.auth_serializers import UserSerializer, UserUpsertSerializer   # your READ serializer

User = get_user_model()


# ---- swagger query params ----
page_param = openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page number")
page_size_param = openapi.Parameter("page_size", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page size")
is_active_param = openapi.Parameter("is_active", openapi.IN_QUERY, type=openapi.TYPE_STRING, enum=["true","false"], description="Filter is_active")
user_type_param = openapi.Parameter("user_type", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Filter by userprofile.user_type")
search_param = openapi.Parameter("search", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Search email/username")

PAGINATED_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "links": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "next": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                "previous": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
            },
        ),
        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
        "page_size": openapi.Schema(type=openapi.TYPE_INTEGER),
        "total_pages": openapi.Schema(type=openapi.TYPE_INTEGER),
        "current_page": openapi.Schema(type=openapi.TYPE_INTEGER),
        "results": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
    },
)


class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        qs = (
            User.objects
            .select_related("userprofile")
            .filter(userprofile__user_type="admin")
            .order_by("id")
        )
        qp = self.request.query_params

        is_active = qp.get("is_active")
        if is_active in ["true", "false"]:
            qs = qs.filter(is_active=(is_active == "true"))

        user_type = qp.get("user_type")
        if user_type:
            qs = qs.filter(userprofile__user_type=user_type)

        search = qp.get("search")
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

    # ---------- LIST ----------
    @swagger_auto_schema(
        operation_summary="List users (paginated)",
        manual_parameters=[page_param, page_size_param, is_active_param, user_type_param, search_param],
        responses={200: openapi.Response("OK", PAGINATED_SCHEMA)},
        tags=["User"],
    )
    def list(self, request):
        qs = self.get_queryset()
        paginator, page = self.paginate_queryset(qs)
        serializer = UserSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    # ---------- RETRIEVE ----------
    @swagger_auto_schema(
        operation_summary="Retrieve user",
        responses={200: openapi.Response("OK", UserSerializer), 404: "Not Found"},
        tags=["User"],
    )
    def retrieve(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserSerializer(user, context={"request": request}).data, status=status.HTTP_200_OK)

    # ---------- CREATE ----------
    @swagger_auto_schema(
        operation_summary="Create user + profile (all fields)",
        request_body=UserUpsertSerializer,
        responses={201: openapi.Response("Created", UserSerializer), 400: "Bad Request"},
        tags=["User"],
    )
    def create(self, request):
        serializer = UserUpsertSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data, status=status.HTTP_201_CREATED)

    # ---------- UPDATE (PUT) ----------
    @swagger_auto_schema(
        operation_summary="Update user + profile (all fields)",
        request_body=UserUpsertSerializer,
        responses={200: openapi.Response("OK", UserSerializer), 400: "Bad Request", 404: "Not Found"},
        tags=["User"],
    )
    def update(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpsertSerializer(user, data=request.data, partial=False, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data, status=status.HTTP_200_OK)

    # ---------- PARTIAL UPDATE (PATCH) ----------
    @swagger_auto_schema(
        operation_summary="Partial update user + profile",
        request_body=UserUpsertSerializer,
        responses={200: openapi.Response("OK", UserSerializer), 400: "Bad Request", 404: "Not Found"},
        tags=["User"],
    )
    def partial_update(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpsertSerializer(user, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data, status=status.HTTP_200_OK)

    # ---------- DELETE ----------
    @swagger_auto_schema(
        operation_summary="Delete user",
        responses={204: "No Content", 404: "Not Found"},
        tags=["User"],
    )
    def destroy(self, request, pk=None):
        try:
            user = self.get_object(pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
