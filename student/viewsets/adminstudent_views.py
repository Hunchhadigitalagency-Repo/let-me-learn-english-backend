from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from user.models import User
from student.serializers.admin_student_serializers import StudentSerializer
from utils.permissions.admins.admin_perms_mixins import IsAdminUserType
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
class StudentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminUserType]
    school_param = openapi.Parameter(
        'school_id', openapi.IN_QUERY,
        description="Filter students by school ID",
        type=openapi.TYPE_INTEGER
    )
    grade_param = openapi.Parameter(
        'grade', openapi.IN_QUERY,
        description="Filter students by grade",
        type=openapi.TYPE_STRING
    )
    search_param = openapi.Parameter(
        'search', openapi.IN_QUERY,
        description="Search students by name or email",
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(
        manual_parameters=[school_param, grade_param, search_param],
        responses={200: StudentSerializer(many=True)}
    )

    def list(self, request):
        
        school_id = request.query_params.get('school_id')
        grade = request.query_params.get('grade')
        search_query = request.query_params.get('search', '').strip()

       
        students_qs = User.objects.filter(userprofile__user_type='student')

       
        if school_id:
            students_qs = students_qs.filter(student_school_relations__school_id=school_id)


       
        if grade:
            students_qs = students_qs.filter(userprofile__grade__iexact=grade)

       
        if search_query:
            students_qs = students_qs.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        serializer = StudentSerializer(students_qs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
