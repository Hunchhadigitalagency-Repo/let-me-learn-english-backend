# tasks/viewsets/student_speaking_attempt_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from tasks.models import (
    SpeakingActivity,
    SpeakingActivityQuestion,
    StudentSpeakingAttempt,
    StudentSpeakingAnswer
)
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

class StudentSpeakingAttemptViewSet(viewsets.ViewSet):
    """
    students.speaking_attempt
    Handles:
    - Start speaking attempt
    - Submit audio answer
    - Complete attempt
    - Get attempt result
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


    # -----------------------------------
    # 1️⃣ Start Attempt
    # -----------------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['speaking_activity_id'],
            properties={
                'speaking_activity_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Response(
                description='Attempt started',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'speaking_activity': openapi.Schema(type=openapi.TYPE_STRING),
                        'started_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                    }
                )
            ),
            400: "speaking_activity_id is required",
            404: "Speaking activity not found"
        }
    )
    @action(detail=False, methods=["post"], url_path="start")
    def start_attempt(self, request):
        speaking_activity_id = request.data.get("speaking_activity_id")
        if not speaking_activity_id:
            return Response(
                {"detail": "speaking_activity_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        activity = get_object_or_404(SpeakingActivity, id=speaking_activity_id)
        attempt, created = StudentSpeakingAttempt.objects.get_or_create(
            student=request.user,
            speaking_activity=activity,
            is_completed=False
        )

        return Response({
            "attempt_id": attempt.id,
            "speaking_activity": activity.title,
            "started_at": attempt.started_at
        })

    # -----------------------------------
    # 2️⃣ Submit Answer (Audio)
    # -----------------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['attempt_id', 'question_id', 'audio_file'],
            properties={
                'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Attempt ID"),
                'question_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Question ID"),
                'audio_file': openapi.Schema(type=openapi.TYPE_FILE, description="Audio file upload"),
            }
        ),
        responses={
            200: openapi.Response(
                description='Answer submitted',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'question_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: "attempt_id, question_id and audio_file are required",
            404: "Attempt or Question not found"
        }
    )
    @action(detail=False, methods=["post"], url_path="submit-answer")
    def submit_answer(self, request):
        attempt_id = request.data.get("attempt_id")
        question_id = request.data.get("question_id")
        audio_file = request.FILES.get("audio_file")

        if not all([attempt_id, question_id, audio_file]):
            return Response(
                {"detail": "attempt_id, question_id and audio_file are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        attempt = get_object_or_404(StudentSpeakingAttempt, id=attempt_id, student=request.user)
        if attempt.is_completed:
            return Response({"detail": "Attempt already completed"}, status=status.HTTP_400_BAD_REQUEST)

        question = get_object_or_404(
            SpeakingActivityQuestion,
            id=question_id,
            speaking_activity=attempt.speaking_activity
        )

        StudentSpeakingAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={"audio_file": audio_file}
        )

        return Response({"message": "Answer saved successfully", "question_id": question.id})

    # -----------------------------------
    # 3️⃣ Complete Attempt
    # -----------------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['attempt_id'],
            properties={'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER)}
        ),
        responses={
            200: openapi.Response(
                description='Attempt completed',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'completed_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                    }
                )
            ),
            400: "Must answer all questions before completing",
            404: "Attempt not found"
        }
    )
    @action(detail=False, methods=["post"], url_path="complete")
    def complete_attempt(self, request):
        attempt_id = request.data.get("attempt_id")
        attempt = get_object_or_404(StudentSpeakingAttempt, id=attempt_id, student=request.user)

        total_questions = SpeakingActivityQuestion.objects.filter(speaking_activity=attempt.speaking_activity).count()
        answered_questions = attempt.answers.count()

        if answered_questions < total_questions:
            return Response(
                {
                    "detail": "You must answer all questions before completing.",
                    "answered": answered_questions,
                    "total": total_questions
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            "message": "Speaking attempt completed successfully",
            "completed_at": attempt.completed_at
        })

    # -----------------------------------
    # 4️⃣ Get Speaking Attempt Result
    # -----------------------------------
    @swagger_auto_schema(
        method='get',
        responses={
            200: openapi.Response(
                description='Attempt result',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'activity': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'feedback': openapi.Schema(type=openapi.TYPE_STRING),
                        'answers': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'question': openapi.Schema(type=openapi.TYPE_STRING),
                                    'audio_file': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                                    'transcript': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            ),
            404: "Attempt not found"
        }
    )
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        attempt = StudentSpeakingAttempt.objects.filter(id=pk, student=request.user).first()
        if not attempt:
            return Response({"error": "Attempt not found"}, status=404)

        answers = attempt.answers.all()
        return Response({
            "attempt_id": attempt.id,
            "activity": attempt.speaking_activity.title,
            "is_completed": attempt.is_completed,
            "score": attempt.score,
            "feedback": attempt.feedback,
            "answers": [
                {
                    "question": answer.question.text_question or answer.question.instruction,
                    "audio_file": request.build_absolute_uri(answer.audio_file.url),
                    "transcript": answer.transcript
                }
                for answer in answers
            ]
        })