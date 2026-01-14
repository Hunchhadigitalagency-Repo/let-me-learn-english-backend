# from rest_framework_simplejwt.views import TokenVerifyView
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth.models import User

# from user.models import UserProfile
# from user.serializers import RoleWithPermissionsSerializer

# class TokenVerification(TokenVerifyView):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Call parent class's post to validate token
#             super().post(request, *args, **kwargs)
            
#             token = request.data.get('token')
#             from rest_framework_simplejwt.tokens import AccessToken
#             access_token = AccessToken(token)
#             user_id = access_token['user_id']
#             user = User.objects.get(id=user_id)

#             # Get user profile
#             user_profile = UserProfile.objects.get(user=user)
#             user_type = user_profile.user_type

#             # Safely get roles
#             roles_qs = getattr(user, 'roles', None)
#             if roles_qs:
#                 roles_data = RoleWithPermissionsSerializer(
#                     roles_qs.all(),
#                     many=True,
#                     context={'request': request}
#                 ).data
#             else:
#                 roles_data = None  # or [] if you want an empty array

#             return Response(
#                 {'user_type': user_type, 'roles': roles_data},
#                 status=status.HTTP_200_OK
#             )

#         except (InvalidToken, TokenError, User.DoesNotExist, UserProfile.DoesNotExist):
#             return Response(
#                 {'detail': 'Token is invalid or expired', 'code': 'token_not_valid'},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
