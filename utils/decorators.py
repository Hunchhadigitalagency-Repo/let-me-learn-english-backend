from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def has_permission(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):

            user = request.user
            if not user.is_authenticated:
                return Response(
                    {"detail": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

           
            permissions = (
                user.roles
                .filter(is_active=True)
                .values_list("permissions__name", flat=True)
            )

            if permission_name not in permissions:
                return Response(
                    {"detail": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(self, request, *args, **kwargs)

        return wrapper
    return decorator
