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
            'is_active'
        ]
        read_only_fields = ['id']
