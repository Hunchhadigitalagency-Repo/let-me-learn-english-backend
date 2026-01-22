from rest_framework import serializers
from cms.models import ContactUs

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = [
            'id', 'name', 'subject', 'message', 'phone_number', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
