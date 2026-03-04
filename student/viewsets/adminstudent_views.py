from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from user.models import UserProfile, School, SchoolStudentParent
from tasks.models import (
    StudentSpeakingAttempt,
    StudentReadingAttempt,
    StudentListeningAttempt,
    StudentWritingAttempt,
    UserTaskProgress,
)


# -------------------------
# Swagger Response Schema
# -------------------------
school_exam_data_response = openapi.Response(
    description="School student exam data fetched successfully",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "school_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
            "school_name": openapi.Schema(type=openapi.TYPE_STRING, example="Springfield High"),
            "total_students": openapi.Schema(type=openapi.TYPE_INTEGER, example=42),
            "students": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "student_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=7),
                        "student_name": openapi.Schema(type=openapi.TYPE_STRING, example="John Doe"),
                        "email": openapi.Schema(type=openapi.TYPE_STRING, example="john@school.com"),
                        "grade": openapi.Schema(type=openapi.TYPE_STRING, example="10"),
                        "section": openapi.Schema(type=openapi.TYPE_STRING, example="A"),
                        "task_progress": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "task_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                    "task_name": openapi.Schema(type=openapi.TYPE_STRING, example="IELTS Mock Test 1"),
                                    "task_grade": openapi.Schema(type=openapi.TYPE_STRING, example="10"),
                                    "completed_speaking": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                    "completed_reading": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                                    "completed_listening": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                    "completed_writing": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                                    "last_updated": openapi.Schema(type=openapi.TYPE_STRING, example="2024-01-15T10:30:00Z"),
                                },
                            ),
                        ),
                        "speaking_attempts": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "attempt_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                    "activity_title": openapi.Schema(type=openapi.TYPE_STRING, example="Part 1 Speaking"),
                                    "score": openapi.Schema(type=openapi.TYPE_NUMBER, example=7.5),
                                    "feedback": openapi.Schema(type=openapi.TYPE_STRING, example="Good fluency"),
                                    "is_completed": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                    "started_at": openapi.Schema(type=openapi.TYPE_STRING, example="2024-01-15T09:00:00Z"),
                                    "completed_at": openapi.Schema(type=openapi.TYPE_STRING, example="2024-01-15T09:20:00Z"),
                                },
                            ),
                        ),
                        "reading_attempts": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "attempt_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                                    "activity_title": openapi.Schema(type=openapi.TYPE_STRING, example="Reading Passage 1"),
                                    "total_questions": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
                                    "correct_answers": openapi.Schema(type=openapi.TYPE_INTEGER, example=8),
                                    "score": openapi.Schema(type=openapi.TYPE_NUMBER, example=80.0),
                                    "is_completed": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                    "started_at": openapi.Schema(type=openapi.TYPE_STRING, example="2024-01-15T10:00:00Z"),
                                    "completed_at": openapi.Schema(type=openapi.TYPE_STRING, example="2024-01-15T10:40:00Z"),
                                },
                            ),
                        ),
                        "listening_attempts": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "attempt_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                                    "activity_title": openapi.Schema(type=openapi.TYPE_STRING, example="Listening Part 1"),
                                    "total_questions": openapi.Schema(type=openapi.TYPE_INTEGER, example=8),
                                    "correct_answers": openapi.Schema(type=openapi.TYPE_INTEGER, example=6),
                                    "score": openapi.Schema(type=openapi.TYPE_NUMBER, example=75.0),
                                    "is_completed": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                                    "started_at": openapi.Schema(type=openapi.TYPE_STRING, example="2024-01-15T11:00:00Z"),
                                    "completed_at": openapi.Schema(type=openapi.TYPE_STRING, example="2024-01-15T11:30:00Z"),
                                },
                            ),
                        ),
                        "writing_attempts": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "attempt_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                    "activity_title": openapi.Schema(type=openapi.TYPE_STRING, example="Essay Task 2"),
                                    "score": openapi.Schema(type=openapi.TYPE_NUMBER, example=6.5),
                                    "feedback": openapi.Schema(type=openapi.TYPE_STRING, example="Well structured"),
                                    "is_completed": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                                    "started_at": openapi.Schema(type=openapi.TYPE_STRING, example="2024-01-15T13:00:00Z"),
                                    "completed_at": openapi.Schema(type=openapi.TYPE_STRING, example=None),
                                },
                            ),
                        ),
                        "summary": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "avg_speaking_score": openapi.Schema(type=openapi.TYPE_NUMBER, example=7.2),
                                "avg_reading_score": openapi.Schema(type=openapi.TYPE_NUMBER, example=80.0),
                                "avg_listening_score": openapi.Schema(type=openapi.TYPE_NUMBER, example=75.0),
                                "avg_writing_score": openapi.Schema(type=openapi.TYPE_NUMBER, example=6.5),
                                "total_attempts": openapi.Schema(type=openapi.TYPE_INTEGER, example=4),
                                "completed_attempts": openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                            },
                        ),
                    },
                ),
            ),
        },
    )
)


class SchoolStudentExamDataAPIView(APIView):

    @swagger_auto_schema(
        operation_id="get_school_student_exam_data",
        operation_summary="Get School-Specific Student Exam Data",
        operation_description=(
            "Fetches comprehensive exam data for all students belonging to a specific school.\n\n"
            "Returns per-student breakdowns across all four activity types:\n"
            "- **Speaking** — score, feedback, completion status\n"
            "- **Reading** — score, correct/total questions, completion status\n"
            "- **Listening** — score, correct/total questions, completion status\n"
            "- **Writing** — score, feedback, completion status\n\n"
            "Also includes each student's **task progress flags** and a **summary** of averages.\n\n"
            "**Note:** Students are resolved via the `SchoolStudentParent` junction table "
            "using the provided `school_id`."
        ),
        tags=["School Exam Data"],
        manual_parameters=[
            openapi.Parameter(
                name="school_id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="The ID of the school to fetch student exam data for",
                example=3,
            ),
            openapi.Parameter(
                name="grade",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="Filter students by grade from their UserProfile (e.g. '10')",
                example="10",
            ),
            openapi.Parameter(
                name="task_id",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Filter exam attempts by a specific Task ID",
                example=1,
            ),
            openapi.Parameter(
                name="is_completed",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False,
                description="Filter attempts by completion status (true / false)",
                example=True,
            ),
        ],
        responses={
            200: school_exam_data_response,
            400: openapi.Response(
                description="Bad Request — missing or invalid school_id",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="school_id is required"
                        )
                    },
                ),
            ),
            404: openapi.Response(
                description="School not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="School not found"
                        )
                    },
                ),
            ),
        },
    )
    def get(self, request):

        # -------------------------
        # Validate Params
        # -------------------------
        school_id = request.query_params.get("school_id")
        if not school_id:
            return Response(
                {"error": "school_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            school_id = int(school_id)
        except ValueError:
            return Response(
                {"error": "school_id must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        grade_filter        = request.query_params.get("grade")
        task_id_filter      = request.query_params.get("task_id")
        is_completed_filter = request.query_params.get("is_completed")

        # -------------------------
        # Validate School
        # -------------------------
        school = School.objects.filter(id=school_id, is_deleted=False, is_disabled=False).first()
        if not school:
            return Response(
                {"error": "School not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------
        # Resolve Students via SchoolStudentParent
        # SchoolStudentParent is the real junction table linking
        # students → school. We get distinct student User objects from it.
        # -------------------------
        school_student_relations = (
            SchoolStudentParent.objects
            .filter(school=school)
            .select_related(
                "student",                  # the User object
                "student__userprofile",     # their profile (grade, section, etc.)
            )
            .distinct("student")            # one row per student regardless of parent count
        )

        # Apply grade filter through the related UserProfile
        if grade_filter:
            school_student_relations = school_student_relations.filter(
                student__userprofile__grade=grade_filter
            )

        # -------------------------
        # Build completed filter flag
        # -------------------------
        completed_flag = None
        if is_completed_filter is not None:
            completed_flag = is_completed_filter.lower() == "true"

        # -------------------------
        # Helper
        # -------------------------
        def safe_avg(attempts):
            scores = [a["score"] for a in attempts if a["score"] is not None]
            return round(sum(scores) / len(scores), 2) if scores else None

        # -------------------------
        # Build Per-Student Exam Data
        # -------------------------
        students_data = []

        for relation in school_student_relations:
            student_user = relation.student

            # Safely access profile (guard against missing OneToOne)
            profile = getattr(student_user, "userprofile", None)

            # --- Speaking Attempts ---
            speaking_qs = StudentSpeakingAttempt.objects.filter(
                student=student_user
            ).select_related("speaking_activity")

            if task_id_filter:
                speaking_qs = speaking_qs.filter(speaking_activity__task_id=task_id_filter)
            if completed_flag is not None:
                speaking_qs = speaking_qs.filter(is_completed=completed_flag)

            speaking_attempts = [
                {
                    "attempt_id":     a.id,
                    "activity_title": a.speaking_activity.title,
                    "score":          a.score,
                    "feedback":       a.feedback,
                    "is_completed":   a.is_completed,
                    "started_at":     a.started_at,
                    "completed_at":   a.completed_at,
                }
                for a in speaking_qs
            ]

            # --- Reading Attempts ---
            reading_qs = StudentReadingAttempt.objects.filter(
                student=student_user
            ).select_related("reading_activity")

            if task_id_filter:
                reading_qs = reading_qs.filter(reading_activity__task_id=task_id_filter)
            if completed_flag is not None:
                reading_qs = reading_qs.filter(is_completed=completed_flag)

            reading_attempts = [
                {
                    "attempt_id":      a.id,
                    "activity_title":  a.reading_activity.title,
                    "total_questions": a.total_questions,
                    "correct_answers": a.correct_answers,
                    "score":           a.score,
                    "is_completed":    a.is_completed,
                    "started_at":      a.started_at,
                    "completed_at":    a.completed_at,
                }
                for a in reading_qs
            ]

            # --- Listening Attempts ---
            listening_qs = StudentListeningAttempt.objects.filter(
                student=student_user
            ).select_related("listening_activity")

            if task_id_filter:
                listening_qs = listening_qs.filter(listening_activity__task_id=task_id_filter)
            if completed_flag is not None:
                listening_qs = listening_qs.filter(is_completed=completed_flag)

            listening_attempts = [
                {
                    "attempt_id":      a.id,
                    "activity_title":  a.listening_activity.title,
                    "total_questions": a.total_questions,
                    "correct_answers": a.correct_answers,
                    "score":           a.score,
                    "is_completed":    a.is_completed,
                    "started_at":      a.started_at,
                    "completed_at":    a.completed_at,
                }
                for a in listening_qs
            ]

            # --- Writing Attempts ---
            writing_qs = StudentWritingAttempt.objects.filter(
                student=student_user
            ).select_related("writing_activity")

            if task_id_filter:
                writing_qs = writing_qs.filter(writing_activity__task_id=task_id_filter)
            if completed_flag is not None:
                writing_qs = writing_qs.filter(is_completed=completed_flag)

            writing_attempts = [
                {
                    "attempt_id":     a.id,
                    "activity_title": a.writing_activity.title,
                    "score":          a.score,
                    "feedback":       a.feedback,
                    "is_completed":   a.is_completed,
                    "started_at":     a.started_at,
                    "completed_at":   a.completed_at,
                }
                for a in writing_qs
            ]

            # --- Task Progress ---
            progress_qs = UserTaskProgress.objects.filter(
                user_id=student_user.id
            ).select_related("task")

            if task_id_filter:
                progress_qs = progress_qs.filter(task_id=task_id_filter)

            task_progress = [
                {
                    "task_id":             p.task.id,
                    "task_name":           p.task.name,
                    "task_grade":          p.task.grade,
                    "completed_speaking":  p.did_completed_speaking_activity,
                    "completed_reading":   p.did_completed_reading_activity,
                    "completed_listening": p.did_completed_listening_activity,
                    "completed_writing":   p.did_completed_writing_activity,
                    "last_updated":        p.last_updated,
                }
                for p in progress_qs
            ]

            # --- Summary Aggregates ---
            all_attempts = (
                len(speaking_attempts) +
                len(reading_attempts) +
                len(listening_attempts) +
                len(writing_attempts)
            )
            completed_attempts = sum([
                sum(1 for a in speaking_attempts  if a["is_completed"]),
                sum(1 for a in reading_attempts   if a["is_completed"]),
                sum(1 for a in listening_attempts if a["is_completed"]),
                sum(1 for a in writing_attempts   if a["is_completed"]),
            ])

            students_data.append({
                "student_id":         student_user.id,
                "student_name":       student_user.name,
                "email":              student_user.email,
                "grade":              profile.grade    if profile else None,
                "section":            profile.section  if profile else None,
                "task_progress":      task_progress,
                "speaking_attempts":  speaking_attempts,
                "reading_attempts":   reading_attempts,
                "listening_attempts": listening_attempts,
                "writing_attempts":   writing_attempts,
                "summary": {
                    "avg_speaking_score":  safe_avg(speaking_attempts),
                    "avg_reading_score":   safe_avg(reading_attempts),
                    "avg_listening_score": safe_avg(listening_attempts),
                    "avg_writing_score":   safe_avg(writing_attempts),
                    "total_attempts":      all_attempts,
                    "completed_attempts":  completed_attempts,
                },
            })

        return Response(
            {
                "school_id":      school.id,
                "school_name":    school.name,
                "total_students": len(students_data),
                "students":       students_data,
            },
            status=status.HTTP_200_OK,
        )