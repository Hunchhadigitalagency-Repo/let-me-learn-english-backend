# school/serializers/subscription_logs_serializers.py

from rest_framework import serializers
from school.models import SubscriptionLog

class SubscriptionLogSerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SubscriptionLog
        fields = (
            "id",
            "subscription",
            "changed_by",
            "changed_fields",   # single JSONField replaces all old_*/new_* fields
            "remarks",
            "created_at",
        )
        read_only_fields = (
            "id",
            "subscription",
            "changed_by",
            "changed_fields",
            "created_at",
        )