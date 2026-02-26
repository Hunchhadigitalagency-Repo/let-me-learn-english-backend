from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from school.models import SubscriptionHistory, SubscriptionLog
from user.models import School
from school.serializers.subscriptions_serializers import (
    SubscriptionHistoryCreateSerializer,
    SubscriptionHistoryListSerializer
)
from utils.paginator import CustomPageNumberPagination
from rest_framework.decorators import action

class SubscriptionHistoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # ------------------ LIST ------------------
    @swagger_auto_schema(
        operation_description="List all subscriptions for the current user's school",
        responses={200: SubscriptionHistoryListSerializer(many=True)}
    )
    def list(self, request):
        subscriptions = SubscriptionHistory.objects.filter(
            school__user=request.user  
        ).select_related("school").order_by("-id")
        paginator = CustomPageNumberPagination()
        paginated_subscriptions = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscriptionHistoryListSerializer(paginated_subscriptions, many=True)
        return paginator.get_paginated_response(serializer.data)

    # ------------------ RETRIEVE ------------------
    @swagger_auto_schema(
        operation_description="Retrieve a specific subscription by ID",
        responses={
            200: SubscriptionHistoryListSerializer(),
            404: "Not found"
        }
    )
    def retrieve(self, request, pk=None):
        try:
            subscription = SubscriptionHistory.objects.get(
                pk=pk,
                school__user=request.user  
            )
        except SubscriptionHistory.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionHistoryListSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------ CREATE ------------------
    @swagger_auto_schema(
        operation_description="Create a new subscription",
        request_body=SubscriptionHistoryCreateSerializer,
        responses={
            201: SubscriptionHistoryCreateSerializer(),
            400: "Bad Request"
        }
    )
    def create(self, request):
        serializer = SubscriptionHistoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            school = School.objects.filter(user=request.user).first()
            if not school:
                return Response({"detail": "School not found for user"}, status=400)

            subscription = serializer.save(school=school)

            # Create log
            SubscriptionLog.objects.create(
                subscription=subscription,
                school=school,
                changed_by=request.user,
                new_status=subscription.status,
                new_amount=subscription.amount,
                new_payment_mode=subscription.payment_mode,
                remarks=subscription.remarks or "Subscription created"
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------ PARTIAL UPDATE ------------------
    @swagger_auto_schema(
        operation_description="Update a subscription partially (PATCH)",
        request_body=SubscriptionHistoryCreateSerializer,
        responses={
            200: SubscriptionHistoryCreateSerializer(),
            400: "Bad Request",
            404: "Not found"
        }
    )
    def partial_update(self, request, pk=None):
        try:
            subscription = SubscriptionHistory.objects.get(
                pk=pk,
                school__user=request.user
            )
        except SubscriptionHistory.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        old_status = subscription.status
        old_amount = subscription.amount
        old_payment_mode = subscription.payment_mode
        old_remarks = subscription.remarks

        serializer = SubscriptionHistoryCreateSerializer(subscription, data=request.data, partial=True)
        if serializer.is_valid():
            school = School.objects.filter(user=request.user).first()
            updated_subscription = serializer.save(school=school)

            SubscriptionLog.objects.create(
                subscription=subscription,
                school=school,
                changed_by=request.user,
                old_status=old_status,
                new_status=updated_subscription.status,
                old_amount=old_amount,
                new_amount=updated_subscription.amount,
                old_payment_mode=old_payment_mode,
                new_payment_mode=updated_subscription.payment_mode,
                remarks=serializer.validated_data.get('remarks', old_remarks)
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------ DELETE ------------------
    @swagger_auto_schema(
        operation_description="Delete a subscription",
        responses={
            204: "Deleted successfully",
            404: "Not found"
        }
    )
    def destroy(self, request, pk=None):
        try:
            subscription = SubscriptionHistory.objects.get(
                pk=pk,
                school__user=request.user
            )
        except SubscriptionHistory.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        subscription.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    

    # ------------------ GET BY SCHOOL ------------------
    @swagger_auto_schema(
        operation_description="Get subscription details for a specific school using school_id query param",
        manual_parameters=[
            openapi.Parameter(
                "school_id",
                openapi.IN_QUERY,
                description="ID of the school",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: SubscriptionHistoryListSerializer(many=True), 404: "School not found"}
    )
    @action(detail=False, methods=["get"], url_path="by-school")
    def by_school(self, request):
        school_id = request.query_params.get("school_id")
        if not school_id:
            return Response({"detail": "school_id query parameter is required"}, status=400)

        # Make sure the school belongs to the requesting user
        try:
            school = School.objects.get(id=school_id)
        except School.DoesNotExist:
            return Response({"detail": "School not found"}, status=404)

        subscriptions = SubscriptionHistory.objects.filter(
            school=school
        ).select_related("school").order_by("-id")

        paginator = CustomPageNumberPagination()
        paginated_subscriptions = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscriptionHistoryListSerializer(paginated_subscriptions, context={"request": request}, many=True)    

        return paginator.get_paginated_response(serializer.data)
