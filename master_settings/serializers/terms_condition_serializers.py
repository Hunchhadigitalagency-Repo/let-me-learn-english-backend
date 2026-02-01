from rest_framework import serializers
from master_settings.models import TermsandConditions

class TermsandConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsandConditions
        # Include all fields
        fields = ['id', 'topic', 'description', 'is_active','effective_date', 'created_at', 'updated_at']
