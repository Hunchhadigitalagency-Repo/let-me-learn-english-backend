# school/views/subscription_views.py

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from school.models import Subscription, SubscriptionLog
from user.models import School
from school.serializers.subscriptions_serializers import (
    SubscriptionHistoryCreateSerializer,
    SubscriptionHistoryListSerializer,
)
from utils.paginator import CustomPageNumberPagination


class SubscriptionHistoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # ------------------ LIST ------------------
    @swagger_auto_schema(
        operation_description="Get the current subscription for the user's school",
        responses={200: SubscriptionHistoryListSerializer()}
    )
    def list(self, request):
        # OneToOneField — only one subscription per school
        try:
            subscription = Subscription.objects.select_related("school").prefetch_related("logs").get(
                school__user=request.user
            )
        except Subscription.DoesNotExist:
            return Response({"detail": "No subscription found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionHistoryListSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------ RETRIEVE ------------------
    @swagger_auto_schema(
        operation_description="Retrieve subscription by ID",
        responses={200: SubscriptionHistoryListSerializer(), 404: "Not found"}
    )
    def retrieve(self, request, pk=None):
        try:
            subscription = Subscription.objects.select_related("school").prefetch_related("logs").get(
                pk=pk,
                school__user=request.user
            )
        except Subscription.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionHistoryListSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------ CREATE ------------------
    @swagger_auto_schema(
        operation_description="Create a subscription for the user's school",
        request_body=SubscriptionHistoryCreateSerializer,
        responses={201: SubscriptionHistoryListSerializer(), 400: "Bad Request"}
    )
    def create(self, request):
        school = School.objects.filter(user=request.user).first()
        if not school:
            return Response({"detail": "School not found for user."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate — OneToOneField will also raise but better to give a clear message
        if Subscription.objects.filter(school=school).exists():
            return Response(
                {"detail": "A subscription already exists for this school. Use PATCH to update it."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SubscriptionHistoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            subscription = serializer.save(school=school)

            # Log creation as an initial snapshot
            SubscriptionLog.objects.create(
                subscription=subscription,
                changed_by=request.user,
                changed_fields={"created": subscription.snapshot()},
                remarks="Subscription created",
            )

            return Response(
                SubscriptionHistoryListSerializer(subscription).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------ PARTIAL UPDATE ------------------
    @swagger_auto_schema(
        operation_description="Partially update the school's subscription (PATCH)",
        request_body=SubscriptionHistoryCreateSerializer,
        responses={200: SubscriptionHistoryListSerializer(), 400: "Bad Request", 404: "Not found"}
    )
    def partial_update(self, request, pk=None):
        try:
            subscription = Subscription.objects.get(pk=pk, school__user=request.user)
        except Subscription.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # Use the model's update method — handles snapshot + logging automatically
        serializer = SubscriptionHistoryCreateSerializer(subscription, data=request.data, partial=True)
        if serializer.is_valid():
            remarks = serializer.validated_data.pop("remarks", None)
            subscription.update_subscription(
                changed_by=request.user,
                remarks=remarks,
                **serializer.validated_data
            )
            return Response(
                SubscriptionHistoryListSerializer(subscription).data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------ DELETE ------------------
    @swagger_auto_schema(
        operation_description="Delete the school's subscription",
        responses={204: "Deleted successfully", 404: "Not found"}
    )
    def destroy(self, request, pk=None):
        try:
            subscription = Subscription.objects.get(pk=pk, school__user=request.user)
        except Subscription.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        subscription.delete()
        return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    # ------------------ GET BY SCHOOL ------------------
    @swagger_auto_schema(
        operation_description="Get subscription for a specific school by school_id",
        manual_parameters=[
            openapi.Parameter(
                "school_id", openapi.IN_QUERY,
                description="ID of the school",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: SubscriptionHistoryListSerializer(), 404: "School not found"}
    )
    @action(detail=False, methods=["get"], url_path="by-school")
    def by_school(self, request):
        school_id = request.query_params.get("school_id")
        if not school_id:
            return Response({"detail": "school_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            school = School.objects.get(id=school_id)
        except School.DoesNotExist:
            return Response({"detail": "School not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            subscription = Subscription.objects.select_related("school").prefetch_related("logs").get(school=school)
        except Subscription.DoesNotExist:
            return Response({"detail": "No subscription found for this school."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubscriptionHistoryListSerializer(subscription, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)