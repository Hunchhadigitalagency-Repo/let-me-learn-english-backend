from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from utils.permissions import permission_checking
from user.models import UserProfile

from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Allows access only to users whose UserProfile user_type is 'superadmin'.
    """
    def has_permission(self, request, view):
        user = request.user
        # Ensure user is logged in and has a profile
        if not user or not user.is_authenticated:
            return False
        
        # Safely access userprofile (avoid AttributeError if it doesn’t exist)
        profile = getattr(user, 'userprofile', None)
        return bool(profile and profile.user_type == 'superadmin')

class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.userprofile.user_type == 'admin')


class IsUser(BasePermission):
    """
    Allows access only to normal users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.userprofile.user_type == 'user')


class IsAdminOrSuperAdmin(BasePermission):
    """
    Allows access to admin and superadmin users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_type = request.user.userprofile.user_type
        return user_type == 'admin' or user_type == 'superadmin'

class IsAdminOrSuperAdmin(BasePermission):
    """
    Allows access to admin and superadmin users for all actions.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_type = request.auth.get('user_type') if request.auth else None
        if not user_type:
            try:
                profile = UserProfile.objects.get(user=request.user)
                user_type = profile.user_type
            except UserProfile.DoesNotExist:
                return False
        return user_type in ['admin', 'superadmin']

class IsAdminOrSuperAdminAllMethods(BasePermission):
    """
    Allows access to admin and superadmin users for all actions (explicitly named for clarity).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_type = request.auth.get('user_type') if request.auth else None
        if not user_type:
            try:
                profile = UserProfile.objects.get(user=request.user)
                user_type = profile.user_type
            except UserProfile.DoesNotExist:
                return False
        return user_type in ['admin', 'superadmin']

class IsAdminOrSuperAdminForPostPatchDelete(BasePermission):
    """
    Allows access to admin and superadmin users for POST, PATCH, DELETE actions.
    Allows all authenticated users for list and retrieve (GET) actions.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ['POST', 'PATCH', 'DELETE']:
            user_type = request.auth.get('user_type') if request.auth else None
            if not user_type:
                try:
                    profile = UserProfile.objects.get(user=request.user)
                    user_type = profile.user_type
                except UserProfile.DoesNotExist:
                    return False
            return user_type in ['admin', 'superadmin']
        return True  # Allow GET (list, retrieve) for all authenticated users

class IsOwnerOrSuperAdmin(BasePermission):
    """
    Allows access to superadmin or the object owner for object-level actions.
    """
    def has_object_permission(self, request, view, obj):
        user_type = request.auth.get('user_type') if request.auth else None
        if not user_type:
            try:
                profile = UserProfile.objects.get(user=request.user)
                user_type = profile.user_type
            except UserProfile.DoesNotExist:
                return False
        return user_type == 'superadmin' or obj.user == request.user
    
class IsAdminOrSuperAdminForPatchDelete(BasePermission):
    """
    Allows access to admin and superadmin users for POST, PATCH, DELETE actions.
    Allows all authenticated users for list and retrieve (GET) actions.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ['POST', 'PATCH', 'DELETE']:
            user_type = request.auth.get('user_type') if request.auth else None
            if not user_type:
                try:
                    profile = UserProfile.objects.get(user=request.user)
                    user_type = profile.user_type
                except UserProfile.DoesNotExist:
                    return False
            return user_type in ['admin', 'superadmin']
        return True 
    



class HasAnyCustomPermission(BasePermission):
    """
    Checks if a user has ANY of the required permissions
    based solely on the HTTP method.
    """

    method_permission_keywords = {
        'GET': 'read',
        'HEAD': 'read',
        'OPTIONS': 'read',
        'POST': 'write',
        'PUT': 'update',
        'PATCH': 'update',
        'DELETE': 'delete',
    }

    def has_permission(self, request, view):
        all_permissions = getattr(view, "required_permissions", None)
        if not all_permissions:
            return True  # No permissions defined → allow

        keyword = self.method_permission_keywords.get(request.method)
        if not keyword:
            return True  # Unknown HTTP method → allow

        matched_permissions = {p for p in all_permissions if keyword in p}
        if not matched_permissions:
            return True  # No matching permission → allow

        has_any_permission = any(permission_checking(request, perm) for perm in matched_permissions)
        

        if not has_any_permission:
            raise PermissionDenied("You do not have permission to perform this action.")

        return True
