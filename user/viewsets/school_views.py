
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user.serializers.school_serializers import SchoolRegistrationSerializer,SchoolUpdateSerializer
from rest_framework.views import APIView
import requests 
from rest_framework_simplejwt.tokens import RefreshToken
from user.serializers.auth_serializers import UserSerializer
from user.models import User,UserProfile,School

from django.utils import timezone
from datetime import timedelta


class SchoolGoogleLoginView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Get user info from Google
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

        # ---- Create or get User ----
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
            defaults={
                "google_id": google_id,
                "google_avatar": picture,
                "user_type": "school" 
            }
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
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": serializer.data
        })
        
        
        
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from user.models import School, FocalPerson
from school.models import SubscriptionHistory

from user.serializers.school_serializers import (
    SchoolCreateSerializer,
    SchoolGetSerializer,
    SchoolListSerializer,
    SchoolUpdateSerializer,
)

from utils.paginator import CustomPageNumberPagination


class SchoolViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    # ---------------- Swagger Query Params ----------------
    q_search = openapi.Parameter(
        "search", openapi.IN_QUERY,
        description="Search in name/email/city/address/code",
        type=openapi.TYPE_STRING
    )
    q_country_id = openapi.Parameter(
        "country_id", openapi.IN_QUERY,
        description="Filter by country_id",
        type=openapi.TYPE_INTEGER
    )
    q_province_id = openapi.Parameter(
        "province_id", openapi.IN_QUERY,
        description="Filter by province_id",
        type=openapi.TYPE_INTEGER
    )
    q_district_id = openapi.Parameter(
        "district_id", openapi.IN_QUERY,
        description="Filter by district_id",
        type=openapi.TYPE_INTEGER
    )
    q_city = openapi.Parameter(
        "city", openapi.IN_QUERY,
        description="Filter by city (icontains)",
        type=openapi.TYPE_STRING
    )
    q_has_subscription = openapi.Parameter(
        "has_subscription", openapi.IN_QUERY,
        description="true/false — schools that have at least 1 subscription history",
        type=openapi.TYPE_BOOLEAN
    )
    q_status = openapi.Parameter(
        "subscription_status", openapi.IN_QUERY,
        description="Filter schools by subscription status (matches SubscriptionHistory.status)",
        type=openapi.TYPE_STRING
    )
    q_ordering = openapi.Parameter(
        "ordering", openapi.IN_QUERY,
        description="Ordering: name,-name,created_at,-created_at,establish_date,-establish_date",
        type=openapi.TYPE_STRING
    )
    q_page = openapi.Parameter(
        "page", openapi.IN_QUERY,
        description="Page number",
        type=openapi.TYPE_INTEGER
    )
    q_page_size = openapi.Parameter(
        "page_size", openapi.IN_QUERY,
        description="Page size",
        type=openapi.TYPE_INTEGER
    )

    # ---------------- Swagger Response Schemas ----------------
    # This matches your CustomPageNumberPagination response structure
    paginated_schema = openapi.Schema(
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

    # ---------------- QUERYSET (FILTERS INSIDE) ----------------
    def get_queryset(self):
        status_filter = params.get("subscription_status")
        now = timezone.now()

        """
        Supported query params:
          - search=...
          - country_id=...
          - province_id=...
          - district_id=...
          - city=...
          - has_subscription=true/false
          - subscription_status=...
          - ordering=name | -created_at | establish_date ...
        """
        qs = (
            School.objects
            .select_related("country", "province", "district", "user")
            .prefetch_related(
                Prefetch("focalperson_set", queryset=FocalPerson.objects.all()),
                Prefetch(
                    "subscriptionhistory_set",
                    queryset=SubscriptionHistory.objects.prefetch_related("logs").order_by("-start_date"),
                ),
            )
        )

        # ---- Scope: school user sees only their school ----
        profile = getattr(self.request.user, "userprofile", None)
        if profile and profile.user_type == "school":
            qs = qs.filter(user=self.request.user)

        params = self.request.query_params

        # ---- Simple FK filters ----
        country_id = params.get("country_id")
        province_id = params.get("province_id")
        district_id = params.get("district_id")

        if country_id:
            qs = qs.filter(country_id=country_id)
        if province_id:
            qs = qs.filter(province_id=province_id)
        if district_id:
            qs = qs.filter(district_id=district_id)

        # ---- City filter ----
        city = params.get("city")
        if city:
            qs = qs.filter(city__icontains=city.strip())

        # ---- Search (multi-field icontains) ----
        search = params.get("search")
        if search:
            s = search.strip()
            qs = qs.filter(
                Q(name__icontains=s) |
                Q(email__icontains=s) |
                Q(city__icontains=s) |
                Q(address__icontains=s) |
                Q(code__icontains=s)
            )

        # ---- Subscription-related filters ----
        # has_subscription=true/false
        has_sub = params.get("has_subscription")
        if has_sub is not None:
            val = has_sub.strip().lower()
            if val in ("true", "1", "yes"):
                qs = qs.filter(subscriptionhistory__isnull=False)
            elif val in ("false", "0", "no"):
                qs = qs.filter(subscriptionhistory__isnull=True)

        # subscription_status=<string>
        if status_filter:
            if status_filter == "new":
                qs = qs.filter(subscriptionhistory__isnull=True)

            elif status_filter == "deactivated":
                qs = qs.filter(subscriptionhistory__status="deactivated")

            elif status_filter == "inactive":
                qs = qs.filter(subscriptionhistory__status="inactive")

            elif status_filter == "pending":
                qs = qs.filter(subscriptionhistory__status="pending")

            elif status_filter == "active":
                qs = qs.filter(
                    subscriptionhistory__status="paid",
                    subscriptionhistory__end_date__gte=now
                )

            elif status_filter == "expired":
                qs = qs.filter(
                    subscriptionhistory__end_date__lt=now
                )

            elif status_filter == "expiring_soon":
                qs = qs.filter(
                    subscriptionhistory__end_date__gte=now,
                    subscriptionhistory__end_date__lte=now + timedelta(days=7)
                )

            elif status_filter == "on_trial":
                qs = qs.filter(
                    subscriptionhistory__logs__on_trial=True
                )

            qs = qs.distinct()

        # ---- Ordering ----
        ordering = params.get("ordering", "-created_at")
        allowed = {
            "created_at", "-created_at",
            "name", "-name",
            "establish_date", "-establish_date",
        }
        if ordering not in allowed:
            ordering = "-created_at"
        qs = qs.order_by(ordering)

        return qs
    
    


    def get_counts(self):
        now = timezone.now()
        qs = self.get_queryset()

        counts = {
            "new": qs.filter(subscriptionhistory__isnull=True).distinct().count(),

            "deactivated": qs.filter(
                subscriptionhistory__status="deactivated"
            ).distinct().count(),

            "inactive": qs.filter(
                subscriptionhistory__status="inactive"
            ).distinct().count(),

            "pending": qs.filter(
                subscriptionhistory__status="pending"
            ).distinct().count(),

            "active": qs.filter(
                subscriptionhistory__status="paid",
                subscriptionhistory__end_date__gte=now
            ).distinct().count(),

            "expired": qs.filter(
                subscriptionhistory__end_date__lt=now
            ).distinct().count(),

            "expiring_soon": qs.filter(
                subscriptionhistory__end_date__gte=now,
                subscriptionhistory__end_date__lte=now + timedelta(days=7)
            ).distinct().count(),

            "on_trial": qs.filter(
                subscriptionhistory__logs__on_trial=True
            ).distinct().count(),

            "total": qs.distinct().count(),
        }

        return counts

    # ---------------- SERIALIZER ROUTING ----------------
    def get_serializer_class(self):
        if self.action == "create":
            return SchoolCreateSerializer
        if self.action in ["update", "partial_update"]:
            return SchoolUpdateSerializer
        if self.action == "list":
            return SchoolListSerializer
        if self.action == "retrieve":
            return SchoolGetSerializer
        return SchoolGetSerializer

    # ---------------- CREATE ----------------
    @swagger_auto_schema(
        operation_summary="Create school",
        request_body=SchoolCreateSerializer,
        responses={201: openapi.Response("Created", SchoolGetSerializer)},
        tags=["School"],
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        if School.objects.filter(user=user).exists():
            return Response({"detail": "You can only create one school."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        school = serializer.save()

        return Response(
            SchoolGetSerializer(school, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )

    # ---------------- UPDATE ----------------
    @swagger_auto_schema(
        operation_summary="Update school",
        request_body=SchoolUpdateSerializer,
        responses={200: openapi.Response("OK", SchoolGetSerializer)},
        tags=["School"],
    )
    def update(self, request, *args, **kwargs):
        school = get_object_or_404(self.get_queryset(), pk=kwargs.get("pk"))

        serializer = self.get_serializer(
            school,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        school = serializer.save()

        return Response(
            SchoolGetSerializer(school, context={"request": request}).data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # ---------------- LIST (PAGINATED AS-IS) ----------------
    @swagger_auto_schema(
        operation_summary="List schools (paginated)",
        manual_parameters=[
            q_search, q_country_id, q_province_id, q_district_id, q_city,
            q_has_subscription, q_status, q_ordering, q_page, q_page_size
        ],
        responses={200: openapi.Response("OK", paginated_schema)},
        tags=["School"],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True, context={"request": request}) if page else self.get_serializer(queryset, many=True, context={"request": request})

        response_data = {
            "counts": self.get_counts(),
            "results": serializer.data if page else serializer.data
        }

        if page:
            return self.get_paginated_response(response_data)

        return Response(response_data, status=status.HTTP_200_OK)

    # ---------------- RETRIEVE ----------------
    @swagger_auto_schema(
        operation_summary="Retrieve school detail",
        responses={200: openapi.Response("OK", SchoolGetSerializer)},
        tags=["School"],
    )
    def retrieve(self, request, *args, **kwargs):
        school = get_object_or_404(self.get_queryset(), pk=kwargs.get("pk"))
        serializer = self.get_serializer(school, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------------- DELETE ----------------
    @swagger_auto_schema(
        operation_summary="Delete school",
        responses={
            204: openapi.Response("No Content"),
            404: "Not Found",
        },
        tags=["School"],
    )
    def destroy(self, request, *args, **kwargs):
        school = get_object_or_404(self.get_queryset(), pk=kwargs.get("pk"))
        school.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from user.serializers.school_serializers import SchoolDropdownSerializer
class SchoolDropdownViewSet(viewsets.ReadOnlyModelViewSet):
   
    queryset = School.objects.all().order_by("-id")
    serializer_class = SchoolDropdownSerializer

    @swagger_auto_schema(
        operation_summary="School dropdown",
        operation_description="Returns a list of schools for dropdown selection (id and name only).",
        responses={
            200: openapi.Response(
                description="List of schools",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                example=1
                            ),
                            "name": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="Everest Secondary School"
                            ),
                        },
                        required=["id", "name"],
                    ),
                ),
            )
        },
        tags=["School"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)