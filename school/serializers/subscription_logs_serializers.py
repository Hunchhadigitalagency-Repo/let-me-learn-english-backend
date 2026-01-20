from rest_framework import serializers
from school.models import SubscriptionLog

class SubscriptionLogSerializer(serializers.ModelSerializer):
    # Display the user as a string (username) instead of full object
    changed_by = serializers.StringRelatedField(read_only=True)  

    class Meta:
        model = SubscriptionLog
        fields = (
            "id",
            "subscription",       # you can remove if using nested serializer
            "school",
            "changed_by",
            "old_status",
            "new_status",
            "old_amount",
            "new_amount",
            "old_payment_mode",
            "new_payment_mode",
            "remarks",
            "created_at",
        )
        read_only_fields = (
            "id",
            "subscription",
            "school",
            "changed_by",
            "created_at",
        )
