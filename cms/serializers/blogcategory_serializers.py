from rest_framework import serializers
from cms.models import BlogCategory

# Serializer for creating a category
class BlogCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['name', 'is_active']  # Only these fields are required for creation

# Serializer for listing categories
class BlogCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'created_at', 'is_active']  # Full details for listing
        read_only_fields = ['id', 'created_at']  # Auto-generated fields
