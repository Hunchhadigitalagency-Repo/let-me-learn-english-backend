from rest_framework import serializers
from cms.models import ExpandVocab


class ExpandVocabSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpandVocab
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
