from rest_framework import serializers
from school.models import SubscriptionHistory
from user.serializers.school_serializers import SchoolBasicSerializer
from school.serializers.subscription_logs_serializers import SubscriptionLogSerializer
class SubscriptionHistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionHistory
        fields = (
            "start_date",
            "end_date",
            "package",
            "remarks",
            "payment_mode",
            "amount",
            "status",
        )

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "End date must be after start date."
            )
        return attrs
    
    
    
from rest_framework import serializers
from school.models import SubscriptionHistory

class SubscriptionHistoryListSerializer(serializers.ModelSerializer):
    school = SchoolBasicSerializer(read_only=True)
    logs = SubscriptionLogSerializer(many=True, read_only=True)  # nested logs

    class Meta:
        model = SubscriptionHistory
        fields = (
            "id",
            "school",
            
            "package",
            "status",
            "payment_mode",
            "amount",
            "start_date",
            "end_date",
            "remarks",
            "created_at",
            "updated_at",
            "logs"
        )




