# nowknowit/serializers.py
from rest_framework import serializers
from cms.models import NowKnowIt

class NowKnowItSerializer(serializers.ModelSerializer):
    class Meta:
        model = NowKnowIt
        fields = [
            'id',
            'common_nepali_english',
            'natural_english',
            'reason',
            'forced_publish',
            'used_status',
            'is_active'
        ]
        read_only_fields = ['id']
        
        
        
        
# nowknowit/serializers.py
