from rest_framework import serializers
from master_settings.models import InstructionTemplate


class InstructionTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructionTemplate
        fields = '__all__'
        read_only_fields = ('id',)
