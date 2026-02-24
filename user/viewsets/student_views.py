from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status

from user.models import User, UserProfile, SchoolStudentParent
from user.serializers.student_serializers import (
    StudentRegisterSerializer,
    StudentLoginSerializer,
    StudentResponseSerializer,
    StudentEditSerializer,
    StudentReadSerializer,
)
from user.serializers.auth_serializers import UserSerializer
from utils.paginator import CustomPageNumberPagination


# =====================================================
# STUDENT REGISTER
# =====================================================

class StudentRegisterView(APIView):
    permission_classes = [IsAuthenticated]  # School should create student

    @transaction.atomic
    def post(self, request):
        serializer = StudentRegisterSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        response_data = StudentResponseSerializer(user).data
        response_data.update({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

        return Response(response_data, status=status.HTTP_201_CREATED)


# =====================================================
# STUDENT LOGIN (Login Code Based)
# =====================================================

class StudentLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        login_code = serializer.validated_data["login_code"]

        try:
            user = User.objects.get(login_code=login_code)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid login code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = UserProfile.objects.filter(user=user).first()

        # Ensure it's a student account
        if not profile or profile.user_type != "student":
            return Response(
                {"error": "Invalid student account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if profile.is_disabled:
            return Response(
                {"error": "Your account is disabled."},
                status=status.HTTP_403_FORBIDDEN
            )

        if profile.is_deleted:
            return Response(
                {"error": "Your account is deleted."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        serialized_user = UserSerializer(
            user,
            context={"request": request}
        )

        return Response({
            "id": user.id,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": serialized_user.data
        }, status=status.HTTP_200_OK)


# =====================================================
# STUDENT EDIT / LIST / RETRIEVE / DELETE
# =====================================================

class StudentEditView(APIView):
    permission_classes = [IsAuthenticated]

    # -------------------------------------------------
    # GET (Single or List)
    # -------------------------------------------------

    def get(self, request, student_id=None):
        school_user = request.user

        # 🔹 Retrieve Single Student
        if student_id:
            link = SchoolStudentParent.objects.filter(
                student__id=student_id,
                school__user=school_user
            ).select_related("student", "student__userprofile").first()

            if not link:
                return Response(
                    {"error": "Student not found or not linked to your school"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = StudentReadSerializer(
                link.student,
                context={"request": request}
            )

            return Response(
                {"student": serializer.data},
                status=status.HTTP_200_OK
            )

        # 🔹 List Students (Optimized Query)
        students = User.objects.filter(
            schoolstudentparent__school__user=school_user
        ).select_related("userprofile").distinct()

        paginator = CustomPageNumberPagination()
        page = paginator.paginate_queryset(students, request)

        serializer = StudentReadSerializer(
            page,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response({
            "message": "Students fetched successfully",
            "students": serializer.data
        })

    # -------------------------------------------------
    # PATCH (Update Student)
    # -------------------------------------------------

    @transaction.atomic
    def patch(self, request, student_id):
        school_user = request.user

        link = SchoolStudentParent.objects.filter(
            student__id=student_id,
            school__user=school_user
        ).select_related("student").first()

        if not link:
            return Response(
                {"error": "Student not found or not linked to your school"},
                status=status.HTTP_404_NOT_FOUND
            )

        student = link.student

        serializer = StudentEditSerializer(
            student,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Student updated successfully"},
            status=status.HTTP_200_OK
        )

    # -------------------------------------------------
    # DELETE (Delete Student)
    # -------------------------------------------------

    @transaction.atomic
    def delete(self, request, student_id):
        school_user = request.user

        link = SchoolStudentParent.objects.filter(
            student__id=student_id,
            school__user=school_user
        ).select_related("student").first()

        if not link:
            return Response(
                {"error": "Student not found or not linked to your school"},
                status=status.HTTP_404_NOT_FOUND
            )

        student = link.student

        # Delete relation first
        link.delete()

        # Delete student user
        student.delete()

        return Response(
            {"message": "Student deleted successfully"},
            status=status.HTTP_200_OK
        )