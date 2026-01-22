
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user.serializers.school_serializers import SchoolRegistrationSerializer,SchoolUpdateSerializer
from rest_framework.views import APIView
import requests 
from rest_framework_simplejwt.tokens import RefreshToken
from user.serializers.auth_serializers import UserSerializer
from user.models import User,UserProfile,School
# class SchoolRegistrationView(generics.CreateAPIView):
#     serializer_class = SchoolRegistrationSerializer
#     permission_classes = [AllowAny] 

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
          
#             school = serializer.save()
            
#             return Response({
#                 "message": "School and User created successfully",
                
               
               
#             }, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class SchoolUpdateView(APIView):
#     permission_classes = [AllowAny]

#     def get_object(self, user):
#         try:
#             return School.objects.get(user=user)
#         except School.DoesNotExist:
#             return None

#     def patch(self, request):
#         school = self.get_object(request.user)

#         if not school:
#             return Response(
#                 {"detail": "School profile does not exist."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         serializer = SchoolUpdateSerializer(
#             school,
#             data=request.data,
#             partial=True,
#             context={'request': request}
#         )

#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {
#                     "message": "School updated successfully",
#                     "data": serializer.data
#                 },
#                 status=status.HTTP_200_OK
#             )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SchoolGoogleLoginView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Get user info from Google
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        userinfo = response.json()
        email = userinfo.get("email")
        name = userinfo.get("name", "")
        picture = userinfo.get("picture", "")
        google_id = userinfo.get("id")

        # ---- Create or get User ----
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": name.split(" ")[0],
                "last_name": " ".join(name.split(" ")[1:]),
            }
        )

       
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "google_id": google_id,
                "google_avatar": picture,
                "user_type": "school" 
            }
        )

      
        if not profile_created:
            profile.google_id = google_id
            profile.google_avatar = picture
            profile.save()

      
        if profile.is_deleted:
            return Response({"error": "Your account is deleted."}, status=403)
        if profile.is_disabled:
            return Response({"error": "Your account is disabled."}, status=403)

     
        if profile.user_type == "school":
            School.objects.get_or_create(user=user)

      
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": serializer.data
        })
        
        
# class SchoolFacebookLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         access_token = request.data.get("access_token")
#         if not access_token:
#             return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

#         # Facebook Graph API call
#         response = requests.get(
#             "https://graph.facebook.com/v15.0/me",
#             params={
#                 "fields": "id,name,email,picture.width(500).height(500)",
#                 "access_token": access_token
#             }
#         )

#         if response.status_code != 200:
#             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

#         userinfo = response.json()
#         facebook_id = userinfo.get("id")
#         name = userinfo.get("name", "")
#         email = userinfo.get("email")

#         # Get Facebook profile picture
#         picture_data = userinfo.get("picture", {}).get("data", {})
#         if picture_data.get("is_silhouette", True):
#             picture = ""  # default avatar
#         else:
#             picture = picture_data.get("url", "")

#         if not email:
#             return Response({"error": "Facebook account does not have an email."}, status=status.HTTP_400_BAD_REQUEST)

#         # ---- Create or get User ----
#         user, created = User.objects.get_or_create(
#             username=email,
#             defaults={
#                 "email": email,
#                 "first_name": name.split(" ")[0],
#                 "last_name": " ".join(name.split(" ")[1:]),
#             }
#         )

#         # ---- Create or update UserProfile ----
#         profile, profile_created = UserProfile.objects.get_or_create(
#             user=user,
#             defaults={
#                 "facebook_id": facebook_id,
#                 "facebook_avatar": picture,
#                 "user_type": "school"
#             }
#         )

#         if not profile_created:
#             profile.facebook_id = facebook_id
#             profile.facebook_avatar = picture
#             profile.save()

#         # ---- Check account status ----
#         if profile.is_deleted:
#             return Response({"error": "Your account is deleted."}, status=403)
#         if profile.is_disabled:
#             return Response({"error": "Your account is disabled."}, status=403)

#         # ---- Create School if user_type is school ----
#         if profile.user_type == "school":
#             School.objects.get_or_create(user=user)

#         # ---- Generate JWT tokens ----
#         refresh = RefreshToken.for_user(user)
#         serializer = UserSerializer(user, context={'request': request})

#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#             "user": serializer.data
#         })

        
        
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from user.models import School, FocalPerson
from user.serializers.school_serializers import SchoolCreateSerializer, SchoolUpdateSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create']:
            return SchoolCreateSerializer
        return SchoolUpdateSerializer

  
    def create(self, request, *args, **kwargs):
        user = request.user


        if School.objects.filter(user=user).exists():
            return Response({
                "message": "You can only create one school."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        school = serializer.save()

        return Response({
            "message": "School created successfully",
            "data": SchoolCreateSerializer(school, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)

   
    def update(self, request, *args, **kwargs):
        user = request.user

       
        school = get_object_or_404(School, id=kwargs.get('pk'), user=user)

        serializer = self.get_serializer(school, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        school = serializer.save()

        return Response({
            "message": "School updated successfully",
            "data": SchoolCreateSerializer(school, context={'request': request}).data
        })


   
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = SchoolCreateSerializer(queryset, many=True, context={'request': request})
        return Response({
            "message": "Schools fetched successfully",
            "data": serializer.data
        })
