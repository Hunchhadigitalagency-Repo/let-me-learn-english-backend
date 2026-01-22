from rest_framework import serializers
from cms.models import Blog, BlogCategory
from utils.urlsfixer import build_https_url

# Nested serializer for BlogCategory
class BlogCategoryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'is_active']
        read_only_fields = ['id', 'name', 'is_active']

# Serializer for creating/updating a blog
class BlogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            'title', 'sub_title', 'author', 'category', 'tags',
            'cover_image', 'description', 'slug',
            'is_active', 'send_as_newsletter'
        ]
        read_only_fields = ['slug']  # slug is auto-generated if blank

# Serializer for listing/retrieving blogs
class BlogListSerializer(serializers.ModelSerializer):
    category = BlogCategoryNestedSerializer(read_only=True)  # nested category
    cover_image = serializers.SerializerMethodField()         # use custom method for HTTPS URL

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'sub_title', 'author', 'category',
            'tags', 'cover_image', 'description', 'slug',
            'created_at', 'updated_at', 'is_active', 'send_as_newsletter'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_cover_image(self, obj):
        request = self.context.get('request')  # get the request from serializer context
        if obj.cover_image:
            return build_https_url(request, obj.cover_image.url)
        return None
