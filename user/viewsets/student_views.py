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
from user.models import SchoolStudentParent
import random
from rest_framework import status
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



from user.serializers.student_serializers import StudentEditSerializer,StudentReadSerializer
from utils.paginator import CustomPageNumberPagination
class StudentEditView(APIView):
    
    def get(self, request, student_id=None):
        school_user = request.user

        # 🔹 RETRIEVE single student
        if student_id:
            link = SchoolStudentParent.objects.filter(
                student__id=student_id,
                school__user=school_user
            ).first()

            if not link:
                return Response(
                    {"error": "Student not found or not linked to your school"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = StudentReadSerializer(
                link.student,
                context={'request': request}
            )
            return Response(
                {"student": serializer.data},
                status=status.HTTP_200_OK
            )

        # 🔹 LIST students (school-wise, paginated)
        links = SchoolStudentParent.objects.filter(
            school__user=school_user
        ).select_related('student')

        students = [link.student for link in links]

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(students, request)

        serializer = StudentReadSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return paginator.get_paginated_response({
            "message": "Students fetched successfully",
            "students": serializer.data
        })
   

    def patch(self, request, student_id):
        
        school_user = request.user
        link = SchoolStudentParent.objects.filter(student__id=student_id, school__user=school_user).first()
        if not link:
            return Response({"error": "Student not found or not linked to your school"}, status=status.HTTP_404_NOT_FOUND)

        student = link.student
        serializer = StudentEditSerializer(student, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, student_id):
        school_user = request.user

        # Find the link between student and school
        link = SchoolStudentParent.objects.filter(
            student__id=student_id,
            school__user=school_user
        ).first()

        if not link:
            return Response(
                {"error": "Student not found or not linked to your school"},
                status=status.HTTP_404_NOT_FOUND
            )

        student = link.student

        # Delete the SchoolStudentParent link first
        link.delete()

        # Optionally, delete the student user completely
        student.delete()

        return Response(
            {"message": "Student deleted successfully"},
            status=status.HTTP_200_OK
        )
