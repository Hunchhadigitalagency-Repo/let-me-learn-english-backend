from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db import transaction

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from user.models import UserProfile, School, CustomRole

User = get_user_model()


# -------------------------
# Request Body Schema
# -------------------------
create_org_user_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["email", "password", "role_id"],
    properties={
        # --- Required ---
        "email": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            description="User's email address (used as username)"
        ),
        "password": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_PASSWORD,
            description="User's password"
        ),
        "role_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="ID of an active CustomRole to assign to the user"
        ),

        # --- User Info ---
        "name": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Full name of the user"
        ),
        "user_type": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Type of user (e.g. 'school', 'student', 'teacher')"
        ),

        # --- Profile Fields ---
        "bio": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Short biography of the user"
        ),
        "display_name": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Display name shown in the UI"
        ),
        "phone_number": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Contact phone number"
        ),
        "address": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Physical address of the user"
        ),
        "dateofbirth": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            description="Date of birth in YYYY-MM-DD format"
        ),
        "profile_picture": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_BINARY,
            description="Profile picture file (multipart/form-data upload)"
        ),

        # --- Status Flags ---
        "is_verified": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="Whether the user is verified (default: false)"
        ),
        "is_disabled": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="Whether the user account is disabled (default: false)"
        ),
        "is_deleted": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="Soft delete flag (default: false)"
        ),
        "is_active": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="Whether the user is active (default: true)"
        ),

        # --- Student-Specific Fields ---
        "grade": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Grade level (applicable for students)"
        ),
        "section": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Class section (applicable for students)"
        ),
        "student_parent_name": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Name of the student's parent/guardian"
        ),
        "student_parent_email": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            description="Email of the student's parent/guardian"
        ),
        "student_parent_phone_number": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Phone number of the student's parent/guardian"
        ),

        # --- School Assignment ---
        "school_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="School ID to assign — only used when user_type is 'school'"
        ),
    },
    example={
        "email": "john.doe@school.com",
        "password": "SecurePass123!",
        "role_id": 2,
        "name": "John Doe",
        "user_type": "student",
        "bio": "10th grade student",
        "display_name": "Johnny",
        "phone_number": "+1234567890",
        "address": "123 Main St, Springfield",
        "dateofbirth": "2008-05-14",
        "is_verified": False,
        "is_disabled": False,
        "is_deleted": False,
        "is_active": True,
        "grade": "10",
        "section": "A",
        "student_parent_name": "Jane Doe",
        "student_parent_email": "jane.doe@email.com",
        "student_parent_phone_number": "+1987654321",
        "school_id": 5
    }
)


# -------------------------
# Response Schemas
# -------------------------
create_org_user_201_response = openapi.Response(
    description="User created successfully",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "message": openapi.Schema(
                type=openapi.TYPE_STRING,
                example="User created successfully"
            ),
            "user_id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                example=42
            ),
            "role": openapi.Schema(
                type=openapi.TYPE_STRING,
                example="Teacher"
            ),
            "profile_id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                example=17
            ),
        }
    )
)

create_org_user_400_response = openapi.Response(
    description="Bad Request — validation error or duplicate user",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "error": openapi.Schema(
                type=openapi.TYPE_STRING,
                example="email, password and role_id are required"
            )
        }
    )
)


# -------------------------
# View
# -------------------------
class CreateOrganizationUserAPIView(APIView):

    @swagger_auto_schema(
        operation_id="create_organization_user",
        operation_summary="Create an Organization User",
        operation_description=(
            "Creates a new user along with their profile, optional school assignment, "
            "and role. All fields except `email`, `password`, and `role_id` are optional.\n\n"
            "**Notes:**\n"
            "- `school_id` is only applied when `user_type` is `'school'`.\n"
            "- `grade`, `section`, and parent fields are intended for students.\n"
            "- Profile picture must be sent as `multipart/form-data`.\n"
            "- The entire operation is wrapped in a database transaction."
        ),
        tags=["Organization Users"],
        request_body=create_org_user_request_body,
        responses={
            201: create_org_user_201_response,
            400: create_org_user_400_response,
        },
        consumes=["multipart/form-data", "application/json"],
    )
    @transaction.atomic
    def post(self, request):
        try:
            data = request.data

            email = data.get("email")
            password = data.get("password")
            role_id = data.get("role_id")
            user_type = data.get("user_type")

            if not email or not password or not role_id:
                return Response(
                    {"error": "email, password and role_id are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "User already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            role = CustomRole.objects.filter(id=role_id, is_active=True).first()
            if not role:
                return Response(
                    {"error": "Invalid role"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                name=data.get("name")
            )

            profile = UserProfile.objects.create(
                user=user,
                bio=data.get("bio"),
                display_name=data.get("display_name"),
                phone_number=data.get("phone_number"),
                address=data.get("address"),
                user_type=user_type,
                is_verified=data.get("is_verified", False),
                is_disabled=data.get("is_disabled", False),
                is_deleted=data.get("is_deleted", False),
                is_active=data.get("is_active", True),
                grade=data.get("grade"),
                section=data.get("section"),
                dateofbirth=data.get("dateofbirth"),
                student_parent_name=data.get("student_parent_name"),
                student_parent_email=data.get("student_parent_email"),
                student_parent_phone_number=data.get("student_parent_phone_number"),
            )

            if request.FILES.get("profile_picture"):
                profile.profile_picture = request.FILES.get("profile_picture")
                profile.save()

            school_id = data.get("school_id")
            if user_type == "school" and school_id:
                school = School.objects.filter(id=school_id).first()
                if school:
                    school.user = user
                    school.save()

            role.user.add(user)

            if role.group:
                user.groups.add(role.group)

            return Response(
                {
                    "message": "User created successfully",
                    "user_id": user.id,
                    "role": role.role,
                    "profile_id": profile.id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )