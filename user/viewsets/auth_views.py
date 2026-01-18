from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
User = get_user_model()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.generics import ListAPIView
from user.models import UserProfile
import random
from rest_framework.permissions import AllowAny
from rest_framework import filters
from rest_framework.decorators import action
import requests
import string
from django.db import transaction
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from user.serializers.auth_serializers import UserSerializer,UserProfileUpdateSerializer,UserProfileSerializer,ChangePasswordSerializer,RegisterSerializer
from rest_framework import generics,permissions,viewsets
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import status, views, permissions
from jose import jwt  # install via: pip install python-jose
import requests as external_requests


from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
import random
import string
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from utils.paginator import CustomPageNumberPagination

from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.shortcuts import redirect
from django_q.tasks import async_task
from django.urls import reverse
from django.conf import settings
from user.models import ResetPassword
from user.tasks import send_verification_email

# class GoogleLoginView(APIView):
#     @swagger_auto_schema(
#         operation_description="Endpoint for Google OAuth login",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=['token'],
#             properties={
#                 'id_token': openapi.Schema(
#                     type=openapi.TYPE_STRING,
#                     description='Google OAuth ID token'
#                 )
#             }
#         ),
#         responses={
#             200: openapi.Response(
#                 description="Login successful",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
#                         'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
#                         'user': openapi.Schema(
#                             type=openapi.TYPE_OBJECT,
#                             properties={
#                                 'username': openapi.Schema(type=openapi.TYPE_STRING),
#                                 'email': openapi.Schema(type=openapi.TYPE_STRING),
#                                 'first_name': openapi.Schema(type=openapi.TYPE_STRING),
#                                 'last_name': openapi.Schema(type=openapi.TYPE_STRING),
#                                 'user_type': openapi.Schema(type=openapi.TYPE_STRING),
#                                 'avatar': openapi.Schema(type=openapi.TYPE_STRING),
#                             }
#                         )
#                     }
#                 )
#             ),
#             400: openapi.Response(
#                 description="Bad request",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'error': openapi.Schema(type=openapi.TYPE_STRING)
#                     }
#                 )
#             )
#         }
#     )
#     def post(self, request):
#         access_token = request.data.get("access_token")
#         if not access_token:
#             return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

#         # Fetch user info from Google using the access token
#         response = requests.get(
#             "https://www.googleapis.com/oauth2/v1/userinfo",
#             params={"alt": "json"},
#             headers={"Authorization": f"Bearer {access_token}"}
#         )

#         if response.status_code != 200:
#             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

#         userinfo = response.json()
#         email = userinfo.get("email")
#         name = userinfo.get("name", "")
#         picture = userinfo.get("picture", "")
#         google_id = userinfo.get("id")

#         # Create or get user
#         user, created = User.objects.get_or_create(username=email, defaults={
#             "email": email,
#             "first_name": name.split(" ")[0],
#             "last_name": " ".join(name.split(" ")[1:]),
#         })

#         # Create or update user profile
#         profile, profile_created = UserProfile.objects.get_or_create(
#         user=user,
#         defaults={
#             "google_id": google_id,
#             "google_avatar": picture,
#             "user_type": 'admin', 
#          }
#          )

       
#         if not profile_created:
#             profile.google_id = google_id
#             profile.google_avatar = picture
           
#             if not profile.user_type:
#                 profile.user_type = 'admin'
#             profile.save()
#         if profile.is_deleted:
#                 return Response(
#                     {"error": "Your account is deleted."},
#                     status=403
#                 )

#         if profile.is_disabled:
#             return Response(
#                 {"error": "Your account is disabled."},
#                 status=403
#             )
#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)

#         serializer = UserSerializer(user, context={'request': request})
#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#             "user": serializer.data
#         })

        




class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Login for all users (superadmin/admin/user)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                                'avatar': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Invalid credentials or bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    )
    @transaction.atomic
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Validate input
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate user exists
        user_obj = User.objects.filter(email=email).first()
        if not user_obj:
            return Response(
                {"error": "User with this email does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate user
        user = authenticate(username=user_obj.username, password=password)
        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch user profile
        profile = UserProfile.objects.filter(user=user).first()
        if not profile:
            return Response(
                {"error": "User profile not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Account status checks
        if profile.is_deleted:
            return Response(
                {"error": "Your account has been deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if profile.is_disabled:
            return Response(
                {"error": "Your account is disabled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not profile.is_verified:
            return Response(
                {"error": "Email is not verified. Please verify your email before logging in."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        serialized_user = UserSerializer(user, context={'request': request})

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serialized_user.data
            },
            status=status.HTTP_200_OK
        )

class ForgotPasswordView(APIView):
    @swagger_auto_schema(
        operation_description="Endpoint for forgot password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    format='email',
                    description='Registered email address'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Password reset email sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Password reset email sent"
                        ),
                        'email': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format='email',
                            description='Email where reset link was sent'
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Email is required"
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="Not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="User not found"
                        )
                    }
                )
            ),
            500: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Failed to send password reset email"
                        )
                    }
                )
            )
        }
    )
    def post(self, request):
        email = request.data.get("email", "").strip()
        if not email:
            return Response(
                {"error": "Email is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            
            reset_token = ''.join(random.choices(
                string.ascii_uppercase + string.ascii_lowercase + string.digits, 
                k=6 
            ))
            
            # Delete any existing tokens and create new one
            ResetPassword.objects.filter(user=user).delete()
            ResetPassword.objects.create(
                user=user,
                reset_token=reset_token
            )
            
            # Prepare email content
            subject = f"Password Reset Request for Basera Account"
            message = f"""
            Hello {user.username or 'User'},

            Your password reset token is: {reset_token}

            This token will expire in 3 hours.

            If you didn't request this, please ignore this email or contact support.

            Thank you,
            Basera Team
            """
            
            # Send email
            try:
                async_task(
                    "user.tasks.send_password_reset_email",
                    user.email,
                    user.username,
                    reset_token
                )
                
                return Response(
                    {
                        "message": "Password reset email sent",
                        "email": user.email
                    },
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                import traceback
                traceback.print_exc()  # shows full error in console
                return Response(
                    {"error": f"Failed to send password reset email: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )


        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class VerifyResetView(APIView):
    @swagger_auto_schema(
        operation_description="Endpoint for verify reset",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'reset_token'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'reset_token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token')
            }
        ),
        responses={
            200: openapi.Response(
                description="Reset token verified",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request):
        email = request.data.get("email")
        reset_token = request.data.get("reset_token")
        new_password = request.data.get("new_password")

        # Basic validation
        if not email or not reset_token or not new_password:
            return Response(
                {"error": "Email, reset token, and new password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Avoid user enumeration
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate reset token for that user
        try:
            token_obj = ResetPassword.objects.get(user=user, reset_token=reset_token)
        except ResetPassword.DoesNotExist:
            return Response(
                {"error": "Invalid email or token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check token expiration using your model method
        if token_obj.is_expired():
            return Response(
                {"error": "Reset token has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate password strength (minimum length)
        if len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update password safely
        with transaction.atomic():
            user.set_password(new_password)
            user.save()

            # Since OneToOne → only one token per user, delete it after use
            token_obj.delete()

        return Response(
            {"message": "Password has been reset successfully"},
            status=status.HTTP_200_OK
        )
        
class ResetPasswordView(APIView):
    permission_classes=[AllowAny]
    @swagger_auto_schema(
        operation_description="Endpoint for reset password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'reset_token', 'new_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'reset_token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password')
            }
        ),
        responses={
            200: openapi.Response(
                description="Password reset successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request):
        email = request.data.get("email")
        reset_token = request.data.get("reset_token")
        new_password = request.data.get("new_password")
        if not email or not reset_token or not new_password:
            return Response({"error": "Email, reset token and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            reset_password = ResetPassword.objects.get(user=user, reset_token=reset_token)
            user.set_password(new_password)
            user.save()
            reset_password.delete()  
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        except ResetPassword.DoesNotExist:
            return Response({"error": "Invalid reset token"}, status=status.HTTP_400_BAD_REQUEST)
        

class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class=UserProfileUpdateSerializer
    permission_classes=[permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 
    @swagger_auto_schema(
    operation_description="Update user profile information",
    request_body=UserProfileUpdateSerializer,
    consumes=["multipart/form-data"],  # This line is important!
    responses={
        200: openapi.Response(
            description="User profile updated successfully",
            schema=UserProfileUpdateSerializer()
        ),
        400: openapi.Response(
            description="Bad request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
)

    def patch(self, request):
        profile = request.user.userprofile
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True,context={'request': request} )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Endpoint to logout by blacklisting the refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token to blacklist')
            }
        ),
        responses={
            205: openapi.Response(
                description="Successfully logged out",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid token or token already blacklisted",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(description="Authentication credentials were not provided or invalid")
        }
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Invalid token or token already blacklisted."}, status=status.HTTP_400_BAD_REQUEST)


    


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response('Password updated successfully'),
            400: openapi.Response('Validation error')
        },
        operation_summary="Change User Password",
        operation_description="Allows an authenticated user to change their password."
    )

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        user = request.user

        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class AdminUserAPIView(APIView):
   
    parser_classes = [MultiPartParser, FormParser,JSONParser]

    def get(self, request, user_id=None):
        search_query = request.query_params.get('search')

        if user_id:
            user = get_object_or_404(User, id=user_id, userprofile__user_type='admin')
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)
        else:
            users = User.objects.filter(userprofile__user_type='admin').order_by('id')

            if search_query:
                users = users.filter(
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query) |
                    Q(userprofile__address__icontains=search_query) |
                    Q(email__icontains=search_query)
                )

            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(users, request, view=self)
            serializer = UserSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)


    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_data = serializer.save()
            return Response(user_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id):
        user_profile = get_object_or_404(UserProfile, user__id=user_id, user_type='admin')
        serializer = UserProfileUpdateSerializer(
            user_profile,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()

            refreshed_user = User.objects.get(pk=user_profile.user.pk)
            refreshed_serializer = UserSerializer(refreshed_user, context={'request': request})
            return Response(refreshed_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id, userprofile__user_type='admin')
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()  # creates user and profile

            # Get user instance
            user_instance = User.objects.get(email=user['email'])

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user_instance)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
           
            verify_url = f"{settings.DOMAIN_NAME}/api/v1/email-verify/{access_token}/"

            
            send_verification_email( user_instance.id,verify_url)
               

            # Return user data + tokens
            response_data = {
                'user': user,
                'access': access_token,
                'refresh': refresh_token
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from rest_framework_simplejwt.exceptions import TokenError
from django.views import View
from django.http import HttpResponseRedirect
class VerifyEmailView(View):
    """
    Verify email link view. The frontend sends a request with the token.
    """

    def get(self, request, token):
        frontend_url = getattr(settings, "FRONTEND_VERIFY_REDIRECT_URL", "/")
        try:
            # Decode the JWT token
            access_token = AccessToken(token)
            user_id = access_token['user_id']

            # Fetch user and profile
            user = User.objects.get(id=user_id)
            if hasattr(user, 'userprofile') and not user.userprofile.is_verified:
                user.userprofile.is_verified = True
                user.userprofile.save()

        except (TokenError, User.DoesNotExist, AttributeError):
            # Silently ignore any error
            pass

        # Always redirect to frontend
        return HttpResponseRedirect(frontend_url)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions


class DisableAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)

            if profile.is_disabled:
                return Response({"detail": "Account is already disabled."}, status=status.HTTP_400_BAD_REQUEST)

            # Mark account as disabled
            profile.is_disabled = True
            profile.save()

            return Response({"detail": "Account disabled successfully."}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

class DeleteAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)

            if profile.is_deleted:
                return Response({"detail": "Account is already deleted."}, status=status.HTTP_400_BAD_REQUEST)

          
            profile.is_deleted = True
            profile.save()

            return Response({"detail": "Account deleted successfully."}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)



