from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

import requests
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta, date

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from user.models import User, UserProfile, School, FocalPerson
from school.models import Subscription                          # updated

from user.serializers.auth_serializers import UserSerializer
from user.serializers.school_serializers import (
    SchoolCreateSerializer,
    SchoolGetSerializer,
    SchoolListSerializer,
    SchoolUpdateSerializer,
    SchoolDropdownSerializer,
)
from utils.paginator import CustomPageNumberPagination


# ─────────────────────────────────────────
# Google Login
# ─────────────────────────────────────────

def _validate_school_status(self):
    profile = getattr(self.request.user, "userprofile", None)
    if not profile:
        return Response(
            {"detail": "User profile not found."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Admin & Superadmin bypass school status checks
    if profile.user_type in ["admin", "superadmin"]:
        return None

    # For school or any other user_type
    school = School.objects.filter(user=self.request.user).first()

    if not school:
        return Response(
            {"detail": "School not found for this user."},
            status=status.HTTP_404_NOT_FOUND
        )

    if school.is_deleted:
        return Response(
            {"detail": "Your school account has been deleted."},
            status=status.HTTP_403_FORBIDDEN
        )

    if school.is_disabled:
        return Response(
            {"detail": "Your school account has been disabled."},
            status=status.HTTP_403_FORBIDDEN
        )

    return None


class SchoolGoogleLoginView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        userinfo = response.json()
        email = userinfo.get("email")
        name = userinfo.get("name", "")
        picture = userinfo.get("picture", "")
        google_id = userinfo.get("id")

        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": name.split(" ")[0],
                "last_name": " ".join(name.split(" ")[1:]),
            }
        )

        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={"google_id": google_id, "google_avatar": picture, "user_type": "school"}
        )

        if not profile_created:
            profile.google_id = google_id
            profile.google_avatar = picture
            profile.save()

        if profile.is_deleted:
            return Response({"error": "Your account is deleted."}, status=403)
        if profile.is_disabled:
            return Response({"error": "Your account is disabled."}, status=403)

        if profile.user_type == "school":
            School.objects.get_or_create(user=user)

        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user, context={"request": request})
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": serializer.data,
        })


# ─────────────────────────────────────────
# School ViewSet
# ─────────────────────────────────────────

class SchoolViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    # ---- Swagger params ----
    q_search = openapi.Parameter("search", openapi.IN_QUERY, type=openapi.TYPE_STRING,
        description="Search in name/email/city/address/code")
    q_country_id = openapi.Parameter("country_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
    q_province_id = openapi.Parameter("province_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
    q_district_id = openapi.Parameter("district_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
    q_city = openapi.Parameter("city", openapi.IN_QUERY, type=openapi.TYPE_STRING,
        description="Filter by city (icontains)")
    q_has_subscription = openapi.Parameter("has_subscription", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
        description="true/false — schools that have a subscription")
    q_status = openapi.Parameter("subscription_status", openapi.IN_QUERY, type=openapi.TYPE_STRING,
        description="Filter schools by subscription status")
    q_ordering = openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING,
        description="name, -name, created_at, -created_at, establish_date, -establish_date")
    q_page = openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
    q_page_size = openapi.Parameter("page_size", openapi.IN_QUERY, type=openapi.TYPE_INTEGER)

    paginated_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "links": openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                "next": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                "previous": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
            }),
            "count": openapi.Schema(type=openapi.TYPE_INTEGER),
            "page_size": openapi.Schema(type=openapi.TYPE_INTEGER),
            "total_pages": openapi.Schema(type=openapi.TYPE_INTEGER),
            "current_page": openapi.Schema(type=openapi.TYPE_INTEGER),
            "results": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
        },
        required=["links", "count", "page_size", "total_pages", "current_page", "results"],)
    

    # ---- Queryset ----
    def get_queryset(self):
        params = self.request.query_params
        status_filter = params.get("subscription_status")
        today = date.today()                                    # DateField now, not datetime

        qs = (
            School.objects
            .select_related("country", "province", "district", "user")
            .prefetch_related(
                Prefetch("focalperson_set", queryset=FocalPerson.objects.all()),
                # OneToOneField reverse — prefetch as single related object with its logs
                Prefetch(
                    "subscription",
                    queryset=Subscription.objects.prefetch_related("logs"),
                ),
            )
        )

        # Scope: school user only sees their own school
        profile = getattr(self.request.user, "userprofile", None)
        if profile and profile.user_type == "school":
            qs = qs.filter(user=self.request.user)

        # FK filters
        if params.get("country_id"):
            qs = qs.filter(country_id=params["country_id"])
        if params.get("province_id"):
            qs = qs.filter(province_id=params["province_id"])
        if params.get("district_id"):
            qs = qs.filter(district_id=params["district_id"])
        if params.get("city"):
            qs = qs.filter(city__icontains=params["city"].strip())

        # Search
        search = params.get("search")
        if search:
            s = search.strip()
            qs = qs.filter(
                Q(name__icontains=s) | Q(email__icontains=s) |
                Q(city__icontains=s) | Q(address__icontains=s) | Q(code__icontains=s)
            )

        # has_subscription — OneToOne so use isnull on the reverse accessor
        has_sub = params.get("has_subscription")
        if has_sub is not None:
            val = has_sub.strip().lower()
            if val in ("true", "1", "yes"):
                qs = qs.filter(subscription__isnull=False)
            elif val in ("false", "0", "no"):
                qs = qs.filter(subscription__isnull=True)

        # Subscription status filters — all now hit subscription__ directly
        if status_filter:
            if status_filter == "new":
                qs = qs.filter(subscription__isnull=True)
            elif status_filter == "deactivated":
                qs = qs.filter(subscription__status="deactivated")
            elif status_filter == "inactive":
                qs = qs.filter(subscription__status="inactive")
            elif status_filter == "pending":
                qs = qs.filter(subscription__status="pending")
            elif status_filter == "paid":
                qs = qs.filter(subscription__status="paid")
            elif status_filter == "active":
                qs = qs.filter(subscription__status="paid", subscription__end_date__gte=today)
            elif status_filter == "expired":
                qs = qs.filter(subscription__end_date__lt=today)
            elif status_filter == "expiring_soon":
                qs = qs.filter(
                    subscription__end_date__gte=today,
                    subscription__end_date__lte=today + timedelta(days=7)
                )
            elif status_filter == "on_trial":
                # on_trial is now a field on Subscription, not on logs
                qs = qs.filter(subscription__on_trial=True)

            qs = qs.distinct()

        # Ordering
        allowed_ordering = {"created_at", "-created_at", "name", "-name", "establish_date", "-establish_date"}
        ordering = params.get("ordering", "-created_at")
        if ordering not in allowed_ordering:
            ordering = "-created_at"
        qs = qs.order_by(ordering)

        return qs

    # ---- Counts ----
    def get_counts(self):
        today = date.today()
        # Base unfiltered queryset for accurate global counts
        qs = School.objects.all()

        return {
            "total": qs.count(),
            "new": qs.filter(subscription__isnull=True).count(),
            "deactivated": qs.filter(subscription__status="deactivated").count(),
            "inactive": qs.filter(subscription__status="inactive").count(),
            "pending": qs.filter(subscription__status="pending").count(),
            "paid": qs.filter(subscription__status="paid").count(),
            "active": qs.filter(
                subscription__status="paid",
                subscription__end_date__gte=today
            ).count(),
            "expired": qs.filter(subscription__end_date__lt=today).count(),
            "expiring_soon": qs.filter(
                subscription__end_date__gte=today,
                subscription__end_date__lte=today + timedelta(days=7)
            ).count(),
            "on_trial": qs.filter(subscription__on_trial=True).count(),
        }

    # ---- Serializer routing ----
    def get_serializer_class(self):
        if self.action == "create":
            return SchoolCreateSerializer
        if self.action in ["update", "partial_update"]:
            return SchoolUpdateSerializer
        if self.action == "list":
            return SchoolListSerializer
        return SchoolGetSerializer

    # ---- CREATE ----
    @swagger_auto_schema(
        operation_summary="Create school",
        request_body=SchoolCreateSerializer,
        responses={201: openapi.Response("Created", SchoolGetSerializer)},
        tags=["School"],
    )
    def create(self, request, *args, **kwargs):
        if School.objects.filter(user=request.user).exists():
            return Response({"detail": "You can only create one school."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        school = serializer.save()

        return Response(
            SchoolGetSerializer(school, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )

    # ---- UPDATE ----
    @swagger_auto_schema(
        operation_summary="Update school",
        request_body=SchoolUpdateSerializer,
        responses={200: openapi.Response("OK", SchoolGetSerializer)},
        tags=["School"],
    )
    def update(self, request, *args, **kwargs):
        school = get_object_or_404(self.get_queryset(), pk=kwargs.get("pk"))
        serializer = self.get_serializer(school, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        school = serializer.save()
        return Response(SchoolGetSerializer(school, context={"request": request}).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # ---- LIST ----
    @swagger_auto_schema(
        operation_summary="List schools (paginated)",
        manual_parameters=[
            q_search, q_country_id, q_province_id, q_district_id, q_city,
            q_has_subscription, q_status, q_ordering, q_page, q_page_size,
        ],
        responses={200: openapi.Response("OK", paginated_schema)},
        tags=["School"],
    )
    def list(self, request, *args, **kwargs):
        
        error = _validate_school_status(self)
        if error:
            return error

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        data = self.get_serializer(
            page if page else queryset,
            many=True,
            context={"request": request}
        ).data

        response_data = {"counts": self.get_counts(), "results": data}

        return self.get_paginated_response(response_data) if page else Response(response_data)

    # ---- RETRIEVE ----
    @swagger_auto_schema(
        operation_summary="Retrieve school detail",
        responses={200: openapi.Response("OK", SchoolGetSerializer)},
        tags=["School"],
    )
    def retrieve(self, request, *args, **kwargs):
        error = _validate_school_status(self)
        if error:
            return error

        school = get_object_or_404(self.get_queryset(), pk=kwargs.get("pk"))
        return Response(SchoolGetSerializer(school, context={"request": request}).data)

    # ---- DELETE ----
    @swagger_auto_schema(
        operation_summary="Delete school",
        responses={204: openapi.Response("No Content"), 404: "Not Found"},
        tags=["School"],
    )
    def destroy(self, request, *args, **kwargs):
        school = get_object_or_404(self.get_queryset(), pk=kwargs.get("pk"))
        school.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─────────────────────────────────────────
# Dropdown
# ─────────────────────────────────────────

class SchoolDropdownViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all().order_by("-id")
    serializer_class = SchoolDropdownSerializer


    @swagger_auto_schema(
        operation_summary="School dropdown",
        operation_description="Returns id and name only for dropdown selection.",
        responses={200: openapi.Response("OK", SchoolDropdownSerializer(many=True))},
        tags=["School"],
    )
    def list(self, request, *args, **kwargs):
        error = _validate_school_status(self)
        if error:
            return error
        return super().list(request, *args, **kwargs)