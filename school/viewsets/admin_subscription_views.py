from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from school.models import SubscriptionHistory, SubscriptionLog
from user.models import School
from school.serializers.subscriptions_serializers import (
    SubscriptionHistoryCreateSerializer,
    SubscriptionHistoryListSerializer
)
from utils.paginator import CustomPageNumberPagination
from django.db.models import Q
from django.db.models import Q, Count

# ----------------------------
# Swagger query params (Admin - School Subscription)
# ----------------------------
ADMIN_SCHOOL_ID = openapi.Parameter(
    name="school_id",
    in_=openapi.IN_QUERY,
    description="Filter subscriptions by School ID (admin use).",
    type=openapi.TYPE_INTEGER,
    required=False,
)

ADMIN_SEARCH = openapi.Parameter(
    name="search",
    in_=openapi.IN_QUERY,
    description=(
        "Search across: school name, school code, package, status, payment_mode, remarks. "
        "Uses icontains."
    ),
    type=openapi.TYPE_STRING,
    required=False,
)

ADMIN_STATUS = openapi.Parameter(
    name="status",
    in_=openapi.IN_QUERY,
    description="Filter by subscription status (exact match).",
    type=openapi.TYPE_STRING,
    required=False,
)

ADMIN_PAYMENT_MODE = openapi.Parameter(
    name="payment_mode",
    in_=openapi.IN_QUERY,
    description="Filter by payment_mode: cash | online | bank.",
    type=openapi.TYPE_STRING,
    required=False,
    enum=["cash", "online", "bank"],
)

ADMIN_PACKAGE = openapi.Parameter(
    name="package",
    in_=openapi.IN_QUERY,
    description="Filter by package (icontains).",
    type=openapi.TYPE_STRING,
    required=False,
)

ADMIN_START_DATE = openapi.Parameter(
    name="start_date",
    in_=openapi.IN_QUERY,
    description="Filter: Subscription start_date >= start_date (YYYY-MM-DD).",
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATE,
    required=False,
)

ADMIN_END_DATE = openapi.Parameter(
    name="end_date",
    in_=openapi.IN_QUERY,
    description="Filter: Subscription end_date <= end_date (YYYY-MM-DD).",
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_DATE,
    required=False,
)

ADMIN_ORDERING = openapi.Parameter(
    name="ordering",
    in_=openapi.IN_QUERY,
    description=(
        "Ordering field. Supported: id, created_at, updated_at, start_date, end_date, amount. "
        "Prefix with '-' for desc, e.g. '-created_at'."
    ),
    type=openapi.TYPE_STRING,
    required=False,
)

PAGE = openapi.Parameter(
    name="page",
    in_=openapi.IN_QUERY,
    description="Page number (uses your CustomPageNumberPagination if enabled globally).",
    type=openapi.TYPE_INTEGER,
    required=False,
)
PAGE_SIZE = openapi.Parameter(
    name="page_size",
    in_=openapi.IN_QUERY,
    description="Optional page size (if supported by CustomPageNumberPagination).",
    type=openapi.TYPE_INTEGER,
    required=False,
)


class AdminSubscriptionHistoryViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing school subscriptions across all schools.

    - Full CRUD
    - Filter by school_id and other fields
    - Search support
    - Creates SubscriptionLog entries on create/update
    """
    permission_classes = [IsAuthenticated]
    queryset = SubscriptionHistory.objects.all().select_related("school").prefetch_related("logs")
    pagination_class = CustomPageNumberPagination   
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SubscriptionHistoryListSerializer
        return SubscriptionHistoryCreateSerializer

    # ----------------------------
    # Filtering / Search / Ordering
    # ----------------------------
    def get_queryset(self):
        qs = super().get_queryset()

        # school filter
        school_id = self.request.query_params.get("school_id") or self.request.query_params.get("school")
        if school_id:
            qs = qs.filter(school_id=school_id)

        # field filters
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        payment_mode = self.request.query_params.get("payment_mode")
        if payment_mode:
            qs = qs.filter(payment_mode=payment_mode)

        package = self.request.query_params.get("package")
        if package:
            qs = qs.filter(package__icontains=package)

        start_date = self.request.query_params.get("start_date")
        if start_date:
            # compares date string -> works if input is ISO date, DB is datetime
            qs = qs.filter(start_date__date__gte=start_date)

        end_date = self.request.query_params.get("end_date")
        if end_date:
            qs = qs.filter(end_date__date__lte=end_date)

        # search (multi-field)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(school__name__icontains=search) |
                Q(school__code__icontains=search) |
                Q(package__icontains=search) |
                Q(status__icontains=search) |
                Q(payment_mode__icontains=search) |
                Q(remarks__icontains=search)
            )

        # ordering
        ordering = self.request.query_params.get("ordering")
        allowed = {"id", "created_at", "updated_at", "start_date", "end_date", "amount"}
        if ordering:
            raw = ordering.lstrip("-")
            if raw in allowed:
                qs = qs.order_by(ordering)
            else:
                qs = qs.order_by("-id")
        else:
            qs = qs.order_by("-id")

        return qs

    # ----------------------------
    # Logging hooks
    # ----------------------------
    def perform_create(self, serializer):
        """
        Admin must pass school in request body (school id).
        Creates SubscriptionLog as 'created'.
        """
        subscription = serializer.save()
        SubscriptionLog.objects.create(
            subscription=subscription,
            school=subscription.school,
            changed_by=self.request.user,
            new_status=subscription.status,
            new_amount=subscription.amount,
            new_payment_mode=subscription.payment_mode,
            remarks=subscription.remarks or "Subscription created by admin"
        )

    def perform_update(self, serializer):
        """
        Creates SubscriptionLog capturing old vs new values.
        """
        instance = self.get_object()

        old_status = instance.status
        old_amount = instance.amount
        old_payment_mode = instance.payment_mode
        old_remarks = instance.remarks

        updated = serializer.save()

        SubscriptionLog.objects.create(
            subscription=updated,
            school=updated.school,
            changed_by=self.request.user,
            old_status=old_status,
            new_status=updated.status,
            old_amount=old_amount,
            new_amount=updated.amount,
            old_payment_mode=old_payment_mode,
            new_payment_mode=updated.payment_mode,
            remarks=serializer.validated_data.get("remarks", old_remarks) or "Updated by admin"
        )

    # ----------------------------
    # Swagger docs (CRUD)
    # ----------------------------
    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="List subscriptions (admin)",
        operation_description=(
            "Lists subscription histories across schools.\n\n"
            "Filters:\n"
            "- school_id: filter by school\n"
            "- status: exact match\n"
            "- payment_mode: cash|online|bank\n"
            "- package: icontains\n"
            "- start_date: start_date >= (date)\n"
            "- end_date: end_date <= (date)\n\n"
            "Search:\n"
            "- search: icontains across school name, school code, package, status, payment_mode, remarks\n\n"
            "Ordering:\n"
            "- ordering: id, created_at, updated_at, start_date, end_date, amount (prefix with '-')\n"
        ),
        manual_parameters=[
            ADMIN_SCHOOL_ID, ADMIN_STATUS, ADMIN_PAYMENT_MODE, ADMIN_PACKAGE,
            ADMIN_START_DATE, ADMIN_END_DATE, ADMIN_SEARCH, ADMIN_ORDERING, PAGE, PAGE_SIZE
        ],
        responses={200: SubscriptionHistoryListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()  # apply all filters, search, ordering

        # Count paid and pending subscriptions
        total_paid = qs.filter(status="paid").count()
        total_pending = qs.filter(status="pending").count()

        # Paginate the queryset
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "subscriptions": serializer.data,
                "counts": {
                    "paid": total_paid,
                    "pending": total_pending
                }
            })

        # If no pagination
        serializer = self.get_serializer(qs, many=True)
        return Response({
            "subscriptions": serializer.data,
            "counts": {
                "paid": total_paid,
                "pending": total_pending
            }
        })

    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Retrieve subscription (admin)",
        operation_description="Retrieve a subscription history by ID. Includes nested logs.",
        responses={200: SubscriptionHistoryListSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Create subscription (admin)",
        operation_description=(
            "Creates a subscription history for a school.\n\n"
            "Admin must provide `school` (school id) in request body.\n"
            "A SubscriptionLog entry is created automatically."
        ),
        request_body=SubscriptionHistoryCreateSerializer,
        responses={201: SubscriptionHistoryCreateSerializer(), 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Update subscription (admin)",
        operation_description=(
            "Updates a subscription fully (PUT).\n\n"
            "A SubscriptionLog entry is created automatically capturing old/new values."
        ),
        request_body=SubscriptionHistoryCreateSerializer,
        responses={200: SubscriptionHistoryCreateSerializer(), 400: "Bad Request", 404: "Not found"}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Partial update subscription (admin)",
        operation_description=(
            "Updates a subscription partially (PATCH).\n\n"
            "A SubscriptionLog entry is created automatically capturing old/new values."
        ),
        request_body=SubscriptionHistoryCreateSerializer,
        responses={200: SubscriptionHistoryCreateSerializer(), 400: "Bad Request", 404: "Not found"}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["admin.schoolsubscription"],
        operation_summary="Delete subscription (admin)",
        operation_description="Deletes a subscription history by ID.",
        responses={204: "Deleted successfully", 404: "Not found"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)