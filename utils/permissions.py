# utils/permissions.py
# user/permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUserType(BasePermission):
   

    def has_permission(self, request, view):
        
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        if request.user.userprofile.user_type=='superadmin':
            return True

       
        return hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'admin'
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
import user
from user.models import CustomPermissionClass, UserProfile
from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Allows access only to users with user_type='superadmin' in UserProfile.
    """
    def has_permission(self, request, view):
        # Make sure the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            # Get the related UserProfile
            profile = UserProfile.objects.get(user=request.user)
            # Check if user_type is 'superadmin'
            return profile.user_type == 'superadmin'
        except UserProfile.DoesNotExist:
            return False

def is_swagger_request(request):
    """
    Returns True if the request is coming from Swagger UI.
    Adjust detection rules as needed.
    """
    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    return "swagger" in user_agent or "mozilla" in user_agent


class PermissionCheckingError(Exception):
    """Raised when permission checking cannot be completed."""
    pass


def permission_checking(request, permission_name):
    """
    Checks if the current user has the specified permission.
    Returns True if the user has it, otherwise False.
    """
    try:
        print("Checking if request is from Swagger UI...")
        # Allow Swagger without permission check
        if is_swagger_request(request):
            print("Request is from Swagger UI. Permission granted.")
            return True

        print("Getting user from request...")
        user = request.user
        print(f"User: {user}")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            print("User is not authenticated or is anonymous.")
            raise PermissionDenied("Authentication credentials were not provided or invalid.")

        try:
            user_profile = UserProfile.objects.get(user=user)
            print(f"user is {user_profile.user_type}")
        except UserProfile.DoesNotExist:
            print("User profile does not exist.")
            
            raise PermissionCheckingError("User profile does not exist.")

        print("Checking if user is super admin...")
        if user_profile.user_type == "superadmin":
            print("User is super admin. Permission granted.")
            return True
        
        if user_profile.user_type == "user":
            print("User is user. Permission granted.")
            return True

        print("Checking if user profile has a role...")
        roles = user.roles.all()
        if not roles:
            print("User profile has no associated role.")
            raise PermissionCheckingError("User profile has no associated role.")

        roles = user.roles.all()
        if not roles.exists():
            print("User profile has no associated role.")
            raise PermissionCheckingError("User profile has no associated role.")

        role_ids = roles.values_list('id', flat=True)
        permissions = CustomPermissionClass.objects.filter(role_id__in=role_ids, name=permission_name)

        has_permission = permissions.exists()
        print(f"User has permission '{permission_name}': {has_permission}")

        return has_permission


    except PermissionDenied:
        print("PermissionDenied exception raised.")
        raise
    except PermissionCheckingError as e:
        print(f"PermissionCheckingError: {str(e)}")
        raise PermissionCheckingError(f"Permission checking failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error during permission check: {str(e)}")
        raise PermissionCheckingError(f"Unexpected error during permission check: {str(e)}")
