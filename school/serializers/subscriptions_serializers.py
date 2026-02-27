# school/serializers/subscriptions_serializers.py

from rest_framework import serializers
from school.models import Subscription
from user.serializers.school_serializers import SchoolBasicSerializer
from school.serializers.subscription_logs_serializers import SubscriptionLogSerializer


class SubscriptionHistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            "school",
            "package",
            "subscription_type",
            "amount",
            "payment_mode",
            "status",
            "on_trial",
            "start_date",
            "end_date",
            "remarks",
        )

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date.")
        return attrs


class SubscriptionHistoryListSerializer(serializers.ModelSerializer):
    school = SchoolBasicSerializer(read_only=True)
    logs = SubscriptionLogSerializer(many=True, read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "school",
            "package",
            "subscription_type",
            "amount",
            "payment_mode",
            "status",
            "on_trial",
            "start_date",
            "end_date",
            "remarks",
            "created_at",
            "updated_at",
            "logs",
        )