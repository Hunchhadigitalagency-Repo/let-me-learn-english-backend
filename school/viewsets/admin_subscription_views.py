# school/views/admin_subscription_views.py

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

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