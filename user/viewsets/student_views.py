from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from user.models import User, UserProfile
from user.serializers.student_serializers import (
    StudentRegisterSerializer, 
    StudentLoginSerializer, 
    StudentResponseSerializer
)
import random
import string
from user.serializers.auth_serializers import UserSerializer
class StudentRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
       
        serializer = StudentRegisterSerializer(data=request.data,context={"request": request}
)
        serializer.is_valid(raise_exception=True)

        
          
        user = serializer.save()

      
        refresh = RefreshToken.for_user(user)
        response_data = StudentResponseSerializer(user).data
        response_data.update({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

        return Response(response_data, status=201)

class StudentLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login_code = serializer.validated_data['login_code']

        try:
            user = User.objects.get(login_code=login_code)
            profile = UserProfile.objects.filter(user=user).first()

            if profile and profile.is_disabled:
                return Response({"error": "Your account is disabled."}, status=403)
            if profile and profile.is_deleted:
                return Response({"error": "Your account is deleted."}, status=403)
            serialized_user = UserSerializer(user, context={'request': request})
            
            

          
            refresh = RefreshToken.for_user(user)
            data = {
                "id": user.id,
                
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serialized_user.data
            }
            return Response(data, status=200)

        except User.DoesNotExist:
            return Response({"error": "Invalid login code"}, status=400)
