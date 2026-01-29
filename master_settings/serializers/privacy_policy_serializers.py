from rest_framework import serializers
from master_settings.models import PrivacyPolicy

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
       
        fields = ['id', 'topic', 'effective_date', 'description', 'created_at']
