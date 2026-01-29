# user/permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUserType(BasePermission):
   

    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False

       
        return hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'admin'
