from rest_framework import serializers
from user.models import CustomPermissionClass,CustomRole,User
from user.serializers.auth_serializers import UserSerializer
class CustomPermissionClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermissionClass
        fields = ['id', 'name', 'role']



class CustomRoleSerializer(serializers.ModelSerializer):
    permissions = CustomPermissionClassSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    group = serializers.CharField(source='group.name', read_only=True)


    class Meta:
        model = CustomRole
        fields = ['id', 'role', 'permissions', 'user', 'group', 'is_active']

class PermissionlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomPermissionClass
        fields = ['id', 'name']

class RoleWithPermissionsSerializer(serializers.ModelSerializer):
    permissions = PermissionlistSerializer(many=True, read_only=True)
    user = UserSerializer(many=True)
    group = serializers.CharField(source='group.name', read_only=True)



    class Meta:
        model = CustomRole
        fields = ['id', 'role', 'permissions', 'user', 'group', 'is_active']
        
    def to_representation(self, instance):
       
        representation = super().to_representation(instance)
        representation['user'] = UserSerializer(instance.user.all(), many=True, context=self.context).data
        return representation
        
        