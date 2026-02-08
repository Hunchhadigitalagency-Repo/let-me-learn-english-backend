# tasks/viewsets/student_writing_attempt_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from tasks.models import (
    WritingActivity,
    StudentWritingAttempt,
    StudentWritingAnswer
)
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

class StudentWritingAttemptViewSet(viewsets.ViewSet):
    """
    student.writing_attempt
    Handles:
    - Start writing attempt
    - Submit writing answer (text/file)
    - Complete attempt
    - Get attempt result
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    # -----------------------------
    # 1️⃣ Start Attempt
    # -----------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['writing_activity_id'],
            properties={
                'writing_activity_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the Writing Activity to start')
            }
        ),
        responses={
            200: openapi.Response(
                description='Writing attempt started',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'writing_activity': openapi.Schema(type=openapi.TYPE_STRING),
                        'started_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                    }
                )
            ),
            400: "writing_activity_id is required",
            404: "Writing activity not found"
        }
    )
    @action(detail=False, methods=["post"], url_path="start")
    def start_attempt(self, request):
        writing_activity_id = request.data.get("writing_activity_id")
        if not writing_activity_id:
            return Response({"detail": "writing_activity_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        writing_activity = get_object_or_404(WritingActivity, id=writing_activity_id)
        attempt, created = StudentWritingAttempt.objects.get_or_create(
            student=request.user,
            writing_activity=writing_activity,
            is_completed=False
        )

        return Response({
            "attempt_id": attempt.id,
            "writing_activity": writing_activity.title,
            "started_at": attempt.started_at
        })

    # -----------------------------
    # 2️⃣ Submit Writing Answer
    # -----------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['attempt_id'],
            properties={
                'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Attempt ID'),
                'submission_text': openapi.Schema(type=openapi.TYPE_STRING, description='Text submission'),
                'file': openapi.Schema(type=openapi.TYPE_FILE, description='Optional file upload'),
            }
        ),
        responses={
            200: openapi.Response(
                description='Writing submitted successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
                )
            ),
            400: "attempt_id is required or submission_text/file missing",
            404: "Attempt not found"
        }
    )
    @action(detail=False, methods=["post"], url_path="submit")
    def submit_writing(self, request):
        attempt_id = request.data.get("attempt_id")
        submission_text = request.data.get("submission_text")
        file = request.FILES.get("file")

        if not attempt_id:
            return Response({"detail": "attempt_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        attempt = get_object_or_404(StudentWritingAttempt, id=attempt_id, student=request.user)
        if attempt.is_completed:
            return Response({"detail": "Attempt already completed"}, status=status.HTTP_400_BAD_REQUEST)

        if not submission_text and not file:
            return Response({"detail": "Either submission_text or file is required"}, status=status.HTTP_400_BAD_REQUEST)

        StudentWritingAnswer.objects.create(
            attempt=attempt,
            submission_text=submission_text,
            file=file
        )

        return Response({"message": "Writing submitted successfully."})

    # -----------------------------
    # 3️⃣ Complete Attempt
    # -----------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['attempt_id'],
            properties={'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER)}
        ),
        responses={
            200: openapi.Response(
                description='Writing attempt completed',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'completed_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                    }
                )
            ),
            400: "Submission required before completing",
            404: "Attempt not found"
        }
    )
    @action(detail=False, methods=["post"], url_path="complete")
    def complete_attempt(self, request):
        attempt_id = request.data.get("attempt_id")
        if not attempt_id:
            return Response({"detail": "attempt_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        attempt = get_object_or_404(StudentWritingAttempt, id=attempt_id, student=request.user)
        if not attempt.submissions.exists():
            return Response({"detail": "You must submit your writing before completing."}, status=status.HTTP_400_BAD_REQUEST)

        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            "message": "Writing attempt completed successfully.",
            "completed_at": attempt.completed_at
        })

    # -----------------------------
    # 4️⃣ Get Attempt Result
    # -----------------------------
    @swagger_auto_schema(
        method='get',
        responses={
            200: openapi.Response(
                description='Writing attempt result',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'activity': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'feedback': openapi.Schema(type=openapi.TYPE_STRING),
                        'submissions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                                'submission_text': openapi.Schema(type=openapi.TYPE_STRING),
                                'file': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                            })
                        )
                    }
                )
            ),
            404: "Attempt not found"
        }
    )
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        attempt = StudentWritingAttempt.objects.filter(id=pk, student=request.user).first()
        if not attempt:
            return Response({"error": "Attempt not found"}, status=404)

        submissions = attempt.submissions.all()
        return Response({
            "attempt_id": attempt.id,
            "activity": attempt.writing_activity.title,
            "is_completed": attempt.is_completed,
            "score": attempt.score,
            "feedback": attempt.feedback,
            "submissions": [
                {
                    "submission_text": s.submission_text,
                    "file": request.build_absolute_uri(s.file.url) if s.file else None,
                    "created_at": s.created_at
                }
                for s in submissions
            ]
        })