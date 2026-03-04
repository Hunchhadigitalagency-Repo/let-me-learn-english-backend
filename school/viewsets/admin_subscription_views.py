# school/views/admin_subscription_views.py

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count

from school.models import Subscription, SubscriptionLog
from user.models import School
from school.serializers.subscriptions_serializers import (
    SubscriptionHistoryCreateSerializer,
    SubscriptionHistoryListSerializer,
)
from utils.paginator import CustomPageNumberPagination
from utils.decorators import has_permission


# ------------------ Swagger Params ------------------

ADMIN_SCHOOL_ID = openapi.Parameter("school_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
    description="Filter by School ID.")
ADMIN_SEARCH = openapi.Parameter("search", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
    description="Search: school name, package, status, payment_mode, remarks.")
ADMIN_STATUS = openapi.Parameter("status", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
    description="Filter by status (exact).")
ADMIN_PAYMENT_MODE = openapi.Parameter("payment_mode", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
    enum=["cash", "online", "bank"], description="Filter by payment mode.")
ADMIN_PACKAGE = openapi.Parameter("package", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
    description="Filter by package (icontains).")
ADMIN_SUBSCRIPTION_TYPE = openapi.Parameter("subscription_type", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
    enum=["monthly", "quarterly", "yearly", "custom"], description="Filter by subscription type.")
ADMIN_ON_TRIAL = openapi.Parameter("on_trial", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False,
    description="Filter by trial status.")
ADMIN_START_DATE = openapi.Parameter("start_date", openapi.IN_QUERY, type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATE, required=False, description="start_date >= (YYYY-MM-DD).")
ADMIN_END_DATE = openapi.Parameter("end_date", openapi.IN_QUERY, type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATE, required=False, description="end_date <= (YYYY-MM-DD).")
ADMIN_ORDERING = openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
    description="Order by: id, created_at, updated_at, start_date, end_date, amount. Prefix '-' for desc.")
PAGE = openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False)
PAGE_SIZE = openapi.Parameter("page_size", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False)


class AdminSubscriptionHistoryViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing school subscriptions.
    One subscription per school — all changes are tracked in logs.
    """
    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all().select_related("school").prefetch_related("logs")
    pagination_class = CustomPageNumberPagination
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SubscriptionHistoryListSerializer
        return SubscriptionHistoryCreateSerializer

    # ------------------ Filtering ------------------

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        school_id = params.get("school_id") or params.get("school")
        if school_id:
            qs = qs.filter(school_id=school_id)

        if params.get("status"):
            qs = qs.filter(status=params["status"])

        if params.get("payment_mode"):
            qs = qs.filter(payment_mode=params["payment_mode"])

        if params.get("package"):
            qs = qs.filter(package__icontains=params["package"])

        if params.get("subscription_type"):
            qs = qs.filter(subscription_type=params["subscription_type"])

        if params.get("on_trial") is not None:
            on_trial = params["on_trial"].lower() == "true"
            qs = qs.filter(on_trial=on_trial)

        if params.get("start_date"):
            qs = qs.filter(start_date__gte=params["start_date"])

        if params.get("end_date"):
            qs = qs.filter(end_date__lte=params["end_date"])

        if params.get("search"):
            search = params["search"]
            qs = qs.filter(
                Q(school__name__icontains=search) |
                Q(school__code__icontains=search) |
                Q(package__icontains=search) |
                Q(status__icontains=search) |
                Q(payment_mode__icontains=search) |
                Q(remarks__icontains=search)
            )

        allowed_ordering = {"id", "created_at", "updated_at", "start_date", "end_date", "amount"}
        ordering = params.get("ordering", "-id")
        if ordering.lstrip("-") in allowed_ordering:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by("-id")

        return qs

    # ------------------ Logging Hooks ------------------

    def perform_create(self, serializer):
        subscription = serializer.save()
        SubscriptionLog.objects.create(
            subscription=subscription,
            changed_by=self.request.user,
            changed_fields={"created": subscription.snapshot()},
            remarks="Subscription created by admin",
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        remarks = serializer.validated_data.pop("remarks", None)

        # Use the model's update method to capture snapshot diff + create log
        instance.update_subscription(
            changed_by=self.request.user,
            remarks=remarks or "Updated by admin",
            **serializer.validated_data
        )

    # ------------------ Swagger Docs ------------------

    @has_permission("can_read_subscriptions")
    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="List subscriptions (admin)",
        manual_parameters=[
            ADMIN_SCHOOL_ID, ADMIN_STATUS, ADMIN_PAYMENT_MODE, ADMIN_PACKAGE,
            ADMIN_SUBSCRIPTION_TYPE, ADMIN_ON_TRIAL, ADMIN_START_DATE,
            ADMIN_END_DATE, ADMIN_SEARCH, ADMIN_ORDERING, PAGE, PAGE_SIZE
        ],
        responses={200: SubscriptionHistoryListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        counts = {
            "paid": Subscription.objects.filter(status="paid").count(),
            "pending": Subscription.objects.filter(status="pending").count(),
            "inactive": Subscription.objects.filter(status="inactive").count(),
            "on_trial": Subscription.objects.filter(on_trial=True).count(),
        }

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "subscriptions": serializer.data,
                "counts": counts,
            })

        serializer = self.get_serializer(qs, many=True)
        return Response({"subscriptions": serializer.data, "counts": counts})

    @has_permission("can_read_subscriptions")
    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Retrieve subscription (admin)",
        responses={200: SubscriptionHistoryListSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_write_subscriptions")
    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Create subscription (admin)",
        request_body=SubscriptionHistoryCreateSerializer,
        responses={201: SubscriptionHistoryListSerializer(), 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        # Guard: one subscription per school
        school_id = request.data.get("school")
        if school_id and Subscription.objects.filter(school_id=school_id).exists():
            return Response(
                {"detail": "A subscription already exists for this school. Use PATCH to update it."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    @has_permission("can_update_subscriptions")
    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Update subscription (admin)",
        request_body=SubscriptionHistoryCreateSerializer,
        responses={200: SubscriptionHistoryListSerializer(), 400: "Bad Request", 404: "Not found"}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("can_update_subscriptions")
    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Partial update subscription (admin)",
        request_body=SubscriptionHistoryCreateSerializer,
        responses={200: SubscriptionHistoryListSerializer(), 400: "Bad Request", 404: "Not found"}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @has_permission("can_delete_subscriptions")
    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Delete subscription (admin)",
        responses={204: "Deleted successfully", 404: "Not found"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
import datetime

from user.models import UserProfile, School
from school.models import Subscription


# ═══════════════════════════════════════════════════════
# Shared Constants
# ═══════════════════════════════════════════════════════

MONTH_LABELS = [
    "", "JAN", "FEB", "MAR", "APR", "MAY",
    "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
]


# ═══════════════════════════════════════════════════════
# Shared Helpers
# ═══════════════════════════════════════════════════════

def get_month_range(year, month):
    start = timezone.make_aware(datetime.datetime(year, month, 1))
    end   = timezone.make_aware(
        datetime.datetime(year + 1, 1, 1) if month == 12
        else datetime.datetime(year, month + 1, 1)
    )
    return start, end


def calc_growth(current, previous):
    if previous == 0:
        percent = 100.0 if current > 0 else 0.0
        trend   = "up" if current > 0 else "same"
    else:
        percent = round(((current - previous) / previous) * 100, 2)
        trend   = "up" if percent > 0 else ("down" if percent < 0 else "same")
    return abs(percent), trend


def build_card(current_value, previous_value):
    percent, trend = calc_growth(current_value, previous_value)
    return {
        "value":            current_value,
        "increase_percent": percent,
        "trend":            trend,
    }


def build_summary(data: list) -> dict:
    if not data:
        return {"total_revenue": 0, "peak_label": None, "peak_revenue": 0}
    peak  = max(data, key=lambda x: x["revenue"])
    total = sum(d["revenue"] for d in data)
    return {
        "total_revenue": total,
        "peak_label":    peak["label"],
        "peak_revenue":  peak["revenue"],
    }


def revenue_by_week() -> list:
    """Last 7 days individually. Label: MON, TUE ... (actual weekday of each day)."""
    today = timezone.now().date()

    qs = (
        Subscription.objects
        .filter(
            status="active",
            start_date__gte=today - datetime.timedelta(days=6),
            start_date__lte=today,
        )
        .annotate(day=TruncDay("start_date"))
        .values("day")
        .annotate(revenue=Sum("amount"))
        .order_by("day")
    )

    lookup = {
        (row["day"].date() if hasattr(row["day"], "date") else row["day"]): row["revenue"]
        for row in qs
    }

    result = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        result.append({
            "label":   day.strftime("%a").upper(),
            "revenue": lookup.get(day, 0),
        })
    return result


def revenue_by_month() -> list:
    """Every day of the current month. Label: 1, 2 ... 31."""
    today       = timezone.now().date()
    month_start = today.replace(day=1)

    qs = (
        Subscription.objects
        .filter(
            status="active",
            start_date__gte=month_start,
            start_date__lte=today,
        )
        .annotate(day=TruncDay("start_date"))
        .values("day")
        .annotate(revenue=Sum("amount"))
        .order_by("day")
    )

    lookup = {
        (row["day"].date() if hasattr(row["day"], "date") else row["day"]): row["revenue"]
        for row in qs
    }

    result  = []
    current = month_start
    while current <= today:
        result.append({
            "label":   str(current.day),
            "revenue": lookup.get(current, 0),
        })
        current += datetime.timedelta(days=1)
    return result


def revenue_by_year() -> list:
    """Jan → current month of this year. Label: JAN, FEB ..."""
    today      = timezone.now().date()
    year_start = today.replace(month=1, day=1)

    qs = (
        Subscription.objects
        .filter(
            status="active",
            start_date__gte=year_start,
            start_date__year=today.year,
        )
        .annotate(month=TruncMonth("start_date"))
        .values("month")
        .annotate(revenue=Sum("amount"))
        .order_by("month")
    )

    lookup = {}
    for row in qs:
        m         = row["month"]
        month_num = m.month if hasattr(m, "month") else m.date().month
        lookup[month_num] = row["revenue"]

    return [
        {"label": MONTH_LABELS[m], "revenue": lookup.get(m, 0)}
        for m in range(1, today.month + 1)
    ]


# ═══════════════════════════════════════════════════════
# Swagger Schemas
# ═══════════════════════════════════════════════════════

dashboard_response = openapi.Response(
    description="Dashboard summary metrics",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "total_revenue": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "value":            openapi.Schema(type=openapi.TYPE_INTEGER, example=156891),
                    "increase_percent": openapi.Schema(type=openapi.TYPE_NUMBER,  example=5.0),
                    "trend":            openapi.Schema(type=openapi.TYPE_STRING,  example="up"),
                },
            ),
            "total_students": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "value":            openapi.Schema(type=openapi.TYPE_INTEGER, example=5689),
                    "increase_percent": openapi.Schema(type=openapi.TYPE_NUMBER,  example=5.0),
                    "trend":            openapi.Schema(type=openapi.TYPE_STRING,  example="up"),
                },
            ),
            "total_schools": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "value":            openapi.Schema(type=openapi.TYPE_INTEGER, example=152),
                    "increase_percent": openapi.Schema(type=openapi.TYPE_NUMBER,  example=5.0),
                    "trend":            openapi.Schema(type=openapi.TYPE_STRING,  example="up"),
                },
            ),
            "total_courses": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "value":            openapi.Schema(type=openapi.TYPE_INTEGER, example=158),
                    "increase_percent": openapi.Schema(type=openapi.TYPE_NUMBER,  example=5.0),
                    "trend":            openapi.Schema(type=openapi.TYPE_STRING,  example="up"),
                },
            ),
        },
    ),
)

revenue_activity_response = openapi.Response(
    description="Revenue activity chart data",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "filter": openapi.Schema(type=openapi.TYPE_STRING, example="month"),
            "data": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "label":   openapi.Schema(type=openapi.TYPE_STRING,  example="JAN"),
                        "revenue": openapi.Schema(type=openapi.TYPE_INTEGER, example=32000),
                    },
                ),
            ),
            "summary": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "total_revenue": openapi.Schema(type=openapi.TYPE_INTEGER, example=245000),
                    "peak_label":    openapi.Schema(type=openapi.TYPE_STRING,  example="MAY"),
                    "peak_revenue":  openapi.Schema(type=openapi.TYPE_INTEGER, example=40000),
                },
            ),
        },
    ),
)


# ═══════════════════════════════════════════════════════
# 1. Dashboard Summary
# ═══════════════════════════════════════════════════════

class DashboardSummaryAPIView(APIView):

    @swagger_auto_schema(
        operation_id="get_dashboard_summary",
        operation_summary="Get Dashboard Summary Metrics",
        operation_description=(
            "Returns the four main dashboard cards with current totals and "
            "month-over-month growth percentages.\n\n"
            "| Card | Source |\n"
            "|---|---|\n"
            "| **Total Revenue** | Sum of `amount` on `active` Subscriptions |\n"
            "| **Total Students** | `UserProfile` where `user_type='student'` |\n"
            "| **Total Schools** | `School` (not deleted / not disabled) |\n"
            "| **Total Courses** | `Course` model (plug in when ready) |\n\n"
            "Growth % = `((this_month - last_month) / last_month) × 100`.\n"
            "If last month was 0, growth defaults to **100%** when current > 0."
        ),
        tags=["Dashboard"],
        responses={
            200: dashboard_response,
            500: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING, example="Something went wrong")},
                ),
            ),
        },
    )
    def get(self, request):
        try:
            now        = timezone.now()
            this_year  = now.year
            this_month = now.month

            last_year, last_month = (this_year - 1, 12) if this_month == 1 else (this_year, this_month - 1)

            this_start, this_end = get_month_range(this_year, this_month)
            last_start, last_end = get_month_range(last_year, last_month)

            # ── Revenue ──────────────────────────────
            revenue_this_month = (
                Subscription.objects
                .filter(status="active", start_date__gte=this_start.date(), start_date__lt=this_end.date())
                .aggregate(total=Sum("amount"))["total"] or 0
            )
            revenue_last_month = (
                Subscription.objects
                .filter(status="active", start_date__gte=last_start.date(), start_date__lt=last_end.date())
                .aggregate(total=Sum("amount"))["total"] or 0
            )

            # ── Students ─────────────────────────────
            students_this_month = (
                UserProfile.objects
                .filter(
                    user_type="student", is_deleted=False, is_disabled=False,
                    user__date_joined__gte=this_start, user__date_joined__lt=this_end,
                ).count()
            )
            students_last_month = (
                UserProfile.objects
                .filter(
                    user_type="student", is_deleted=False, is_disabled=False,
                    user__date_joined__gte=last_start, user__date_joined__lt=last_end,
                ).count()
            )

            # ── Schools ──────────────────────────────
            schools_this_month = (
                School.objects
                .filter(is_deleted=False, is_disabled=False, created_at__gte=this_start, created_at__lt=this_end)
                .count()
            )
            schools_last_month = (
                School.objects
                .filter(is_deleted=False, is_disabled=False, created_at__gte=last_start, created_at__lt=last_end)
                .count()
            )

            # ── Courses (plug in your model) ──────────
            courses_this_month = 0  # ← swap with real query
            courses_last_month = 0  # ← swap with real query

            return Response(
                {
                    "total_revenue":  build_card(revenue_this_month,  revenue_last_month),
                    "total_students": build_card(students_this_month, students_last_month),
                    "total_schools":  build_card(schools_this_month,  schools_last_month),
                    "total_courses":  build_card(courses_this_month,  courses_last_month),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ═══════════════════════════════════════════════════════
# 2. Revenue Activity Chart
# ═══════════════════════════════════════════════════════

class RevenueActivityAPIView(APIView):

    @swagger_auto_schema(
        operation_id="get_revenue_activity",
        operation_summary="Get Revenue Activity Chart Data",
        operation_description=(
            "Returns time-series revenue data for the activity line chart.\n\n"
            "| Filter   | Data Points                       | Label Format  |\n"
            "|----------|-----------------------------------|---------------|\n"
            "| `week`   | Last 7 days individually          | `MON`, `TUE`  |\n"
            "| `month`  | Every day of the current month    | `1`, `2` ...  |\n"
            "| `yearly` | Jan → current month of this year  | `JAN`, `FEB`  |\n\n"
            "Revenue = **sum of `Subscription.amount`** where `status=active`, grouped by period.\n"
            "Days/months with no subscriptions return `revenue: 0`."
        ),
        tags=["Dashboard"],
        manual_parameters=[
            openapi.Parameter(
                name="filter",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                enum=["week", "month", "yearly"],
                default="month",
                description="Time range filter (default: month)",
            ),
        ],
        responses={
            200: revenue_activity_response,
            400: openapi.Response(
                description="Invalid filter value",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING, example="Invalid filter. Use: week, month, yearly")},
                ),
            ),
            500: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING, example="Something went wrong")},
                ),
            ),
        },
    )
    def get(self, request):
        filter_by = request.query_params.get("filter", "month").lower().strip()

        if filter_by not in {"week", "month", "yearly"}:
            return Response(
                {"error": "Invalid filter. Use: week, month, yearly"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if filter_by == "week":
                data = revenue_by_week()
            elif filter_by == "month":
                data = revenue_by_month()
            else:
                data = revenue_by_year()

            return Response(
                {
                    "filter":  filter_by,
                    "data":    data,
                    "summary": build_summary(data),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# ═══════════════════════════════════════════════════════
# Subscription Expiring Soon View
# ═══════════════════════════════════════════════════════

expiring_soon_response = openapi.Response(
    description="Subscriptions expiring soon",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "filter":      openapi.Schema(type=openapi.TYPE_STRING,  example="week"),
            "total":       openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
            "subscriptions": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "subscription_id":   openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                        "school_id":         openapi.Schema(type=openapi.TYPE_INTEGER, example=7),
                        "school_name":       openapi.Schema(type=openapi.TYPE_STRING,  example="Little Angel English Boarding School Pvt. Ltd"),
                        "phone":             openapi.Schema(type=openapi.TYPE_STRING,  example="+98234567654"),
                        "location":          openapi.Schema(type=openapi.TYPE_STRING,  example="Kathmandu"),
                        "end_date":          openapi.Schema(type=openapi.TYPE_STRING,  example="2024-03-10"),
                        "days_remaining":    openapi.Schema(type=openapi.TYPE_INTEGER, example=13),
                        "package":           openapi.Schema(type=openapi.TYPE_STRING,  example="Premium"),
                        "subscription_type": openapi.Schema(type=openapi.TYPE_STRING,  example="monthly"),
                        "status":            openapi.Schema(type=openapi.TYPE_STRING,  example="active"),
                        "on_trial":          openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                    },
                ),
            ),
        },
    ),
)


class SubscriptionExpiringSoonAPIView(APIView):

    @swagger_auto_schema(
        operation_id="get_subscriptions_expiring_soon",
        operation_summary="Get Subscriptions Expiring Soon",
        operation_description=(
            "Returns a list of school subscriptions whose `end_date` falls within "
            "the selected time window, ordered by soonest expiry first.\n\n"
            "| Filter   | Window                     |\n"
            "|----------|----------------------------|\n"
            "| `week`   | Expiring within 7 days     |\n"
            "| `month`  | Expiring within 30 days    |\n"
            "| `yearly` | Expiring within 365 days   |\n\n"
            "`days_remaining` is calculated as `end_date - today` (minimum 0).\n"
            "`location` resolves in priority order: `city → district → province → —`."
        ),
        tags=["Dashboard"],
        manual_parameters=[
            openapi.Parameter(
                name="filter",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                enum=["week", "month", "yearly"],
                default="week",
                description="Expiry window filter (default: week)",
            ),
            openapi.Parameter(
                name="page",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Page number",
            ),
            openapi.Parameter(
                name="page_size",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Results per page (default: 10)",
            ),
        ],
        responses={
            200: expiring_soon_response,
            400: openapi.Response(
                description="Invalid filter value",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Invalid filter. Use: week, month, yearly"
                        )
                    },
                ),
            ),
            500: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request):
        filter_by = request.query_params.get("filter", "week").lower().strip()

        FILTER_DAYS = {
            "week":   7,
            "month":  30,
            "yearly": 365,
        }

        if filter_by not in FILTER_DAYS:
            return Response(
                {"error": "Invalid filter. Use: week, month, yearly"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            today      = timezone.now().date()
            cutoff     = today + datetime.timedelta(days=FILTER_DAYS[filter_by])

            # Fetch active subscriptions expiring within the window,
            # ordered by soonest end_date first
            qs = (
                Subscription.objects
                .filter(
                    status="active",
                    end_date__gte=today,      # not already expired
                    end_date__lte=cutoff,     # within the window
                )
                .select_related(
                    "school",
                    "school__district",
                    "school__province",
                )
                .order_by("end_date")
            )

            # ── Pagination ────────────────────────────
            try:
                page      = max(1, int(request.query_params.get("page", 1)))
                page_size = max(1, int(request.query_params.get("page_size", 10)))
            except (ValueError, TypeError):
                page, page_size = 1, 10

            total     = qs.count()
            start_idx = (page - 1) * page_size
            end_idx   = start_idx + page_size
            paginated = qs[start_idx:end_idx]

            # ── Serialize ────────────────────────────
            def resolve_location(school) -> str:
                """city → district name → province name → fallback."""
                if school.city:
                    return school.city
                if school.district:
                    return school.district.name
                if school.province:
                    return school.province.name
                return "—"

            subscriptions = []
            for sub in paginated:
                days_remaining = (sub.end_date - today).days
                subscriptions.append({
                    "subscription_id":   sub.id,
                    "school_id":         sub.school.id,
                    "school_name":       sub.school.name,
                    "phone":             sub.school.landline or "—",
                    "location":          resolve_location(sub.school),
                    "end_date":          str(sub.end_date),
                    "days_remaining":    max(days_remaining, 0),
                    "package":           sub.package,
                    "subscription_type": sub.subscription_type,
                    "status":            sub.status,
                    "on_trial":          sub.on_trial,
                })

            return Response(
                {
                    "filter":        filter_by,
                    "total":         total,
                    "page":          page,
                    "page_size":     page_size,
                    "total_pages":   (total + page_size - 1) // page_size,
                    "subscriptions": subscriptions,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ═══════════════════════════════════════════════════════
# School Onboarding Helpers
# ═══════════════════════════════════════════════════════

def onboarding_by_week() -> list:
    """Last 7 days individually. Label: MON, TUE ... (actual weekday of each day)."""
    today = timezone.now().date()

    qs = (
        School.objects
        .filter(
            is_deleted=False,
            is_disabled=False,
            created_at__date__gte=today - datetime.timedelta(days=6),
            created_at__date__lte=today,
        )
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    lookup = {
        (row["day"].date() if hasattr(row["day"], "date") else row["day"]): row["count"]
        for row in qs
    }

    result = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        result.append({
            "label": day.strftime("%a").upper(),
            "count": lookup.get(day, 0),
        })
    return result


def onboarding_by_month() -> list:
    """Every day of the current month. Label: 1, 2 ... 31."""
    today       = timezone.now().date()
    month_start = today.replace(day=1)

    qs = (
        School.objects
        .filter(
            is_deleted=False,
            is_disabled=False,
            created_at__date__gte=month_start,
            created_at__date__lte=today,
        )
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    lookup = {
        (row["day"].date() if hasattr(row["day"], "date") else row["day"]): row["count"]
        for row in qs
    }

    result  = []
    current = month_start
    while current <= today:
        result.append({
            "label": str(current.day),
            "count": lookup.get(current, 0),
        })
        current += datetime.timedelta(days=1)
    return result


def onboarding_by_year() -> list:
    """Jan → current month of this year. Label: JAN, FEB ..."""
    today      = timezone.now().date()
    year_start = today.replace(month=1, day=1)

    qs = (
        School.objects
        .filter(
            is_deleted=False,
            is_disabled=False,
            created_at__date__gte=year_start,
            created_at__year=today.year,
        )
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    lookup = {}
    for row in qs:
        m         = row["month"]
        month_num = m.month if hasattr(m, "month") else m.date().month
        lookup[month_num] = row["count"]

    return [
        {"label": MONTH_LABELS[m], "count": lookup.get(m, 0)}
        for m in range(1, today.month + 1)
    ]


def build_onboarding_summary(data: list) -> dict:
    if not data:
        return {"total_schools": 0, "peak_label": None, "peak_count": 0}
    peak  = max(data, key=lambda x: x["count"])
    total = sum(d["count"] for d in data)
    return {
        "total_schools": total,
        "peak_label":    peak["label"],
        "peak_count":    peak["count"],
    }


# ═══════════════════════════════════════════════════════
# School Onboarding Chart View
# ═══════════════════════════════════════════════════════

school_onboarding_response = openapi.Response(
    description="School onboarding chart data",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "filter": openapi.Schema(type=openapi.TYPE_STRING, example="month"),
            "data": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "label": openapi.Schema(type=openapi.TYPE_STRING,  example="JAN"),
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                    },
                ),
            ),
            "summary": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "total_schools": openapi.Schema(type=openapi.TYPE_INTEGER, example=152),
                    "peak_label":    openapi.Schema(type=openapi.TYPE_STRING,  example="MAY"),
                    "peak_count":    openapi.Schema(type=openapi.TYPE_INTEGER, example=40),
                },
            ),
        },
    ),
)


class SchoolOnboardingActivityAPIView(APIView):

    @swagger_auto_schema(
        operation_id="get_school_onboarding_activity",
        operation_summary="Get School Onboarding Chart Data",
        operation_description=(
            "Returns time-series school onboarding data for the bar chart.\n\n"
            "| Filter   | Data Points                      | Label Format |\n"
            "|----------|----------------------------------|--------------|\n"
            "| `week`   | Last 7 days individually         | `MON`, `TUE` |\n"
            "| `month`  | Every day of the current month   | `1`, `2` ...  |\n"
            "| `yearly` | Jan → current month of this year | `JAN`, `FEB` |\n\n"
            "Count = **number of Schools created** in each period "
            "where `is_deleted=false` and `is_disabled=false`.\n"
            "Days/months with no onboardings return `count: 0`."
        ),
        tags=["Dashboard"],
        manual_parameters=[
            openapi.Parameter(
                name="filter",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                enum=["week", "month", "yearly"],
                default="month",
                description="Time range filter (default: month)",
            ),
        ],
        responses={
            200: school_onboarding_response,
            400: openapi.Response(
                description="Invalid filter value",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Invalid filter. Use: week, month, yearly"
                        )
                    },
                ),
            ),
            500: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, example="Something went wrong")
                    },
                ),
            ),
        },
    )
    def get(self, request):
        filter_by = request.query_params.get("filter", "month").lower().strip()

        if filter_by not in {"week", "month", "yearly"}:
            return Response(
                {"error": "Invalid filter. Use: week, month, yearly"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if filter_by == "week":
                data = onboarding_by_week()
            elif filter_by == "month":
                data = onboarding_by_month()
            else:
                data = onboarding_by_year()

            return Response(
                {
                    "filter":  filter_by,
                    "data":    data,
                    "summary": build_onboarding_summary(data),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)