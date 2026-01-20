from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from school.models import SubscriptionHistory
from school.serializers.subscriptions_serializers import (
    SubscriptionHistoryCreateSerializer,
    SubscriptionHistoryListSerializer
)
from user.models import School
from school.models import SubscriptionLog
from utils.paginator import CustomPageNumberPagination
class SubscriptionHistoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # ------------------ LIST ------------------
    def list(self, request):
        subscriptions = SubscriptionHistory.objects.filter(
            school__user=request.user  
        ).select_related("school").order_by("-id")
        paginator=CustomPageNumberPagination()
        paginated_subscriptions=paginator.paginate_queryset(subscriptions,request)
        serializer = SubscriptionHistoryListSerializer(paginated_subscriptions, many=True)
        return paginator.get_paginated_response(serializer.data)

    # ------------------ RETRIEVE ------------------
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
    # ------------------ CREATE ------------------
    def create(self, request):
        serializer = SubscriptionHistoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            school = School.objects.filter(user=request.user).first()
            if not school:
                return Response({"detail": "School not found for user"}, status=400)

            # SAVE the subscription and assign to a variable
            subscription = serializer.save(school=school)

            # Now subscription exists, create the log
            from school.models import SubscriptionLog
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


    # ------------------ PARTIAL UPDATE (PATCH) ------------------
    # ------------------ PARTIAL UPDATE (PATCH) ------------------
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
    def destroy(self, request, pk=None):
        try:
            subscription = SubscriptionHistory.objects.get(
                pk=pk,
                school__user=request.user  # filter by user via school
            )
        except SubscriptionHistory.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        subscription.delete()
        return Response({"detail": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
