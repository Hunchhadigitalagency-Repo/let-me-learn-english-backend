# views/student_listening_attempt_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from tasks.models import (
    ListeningActivity,
    ListeningActivityQuestion,
    StudentListeningAttempt,
    StudentListeningAnswer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
class StudentListeningAttemptViewSet(viewsets.ViewSet):
    """
    student.listening_attempt
    Handles:
    - Start listening attempt
    - Submit/update answer
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
            required=['listening_activity_id'],
            properties={
                'listening_activity_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the Listening Activity to start'
                )
            }
        ),
        responses={
            201: openapi.Response(
                description='Attempt started successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: "listening_activity_id is required",
            404: "Listening activity not found"
        }
    )
    @action(detail=False, methods=['post'])
    def start(self, request):
        listening_activity_id = request.data.get("listening_activity_id")

        if not listening_activity_id:
            return Response({"error": "listening_activity_id is required"}, status=400)

        activity = ListeningActivity.objects.filter(id=listening_activity_id).first()
        if not activity:
            return Response({"error": "Listening activity not found"}, status=404)

        attempt = StudentListeningAttempt.objects.create(
            student=request.user,
            listening_activity=activity
        )

        return Response({
            "message": "Attempt started",
            "attempt_id": attempt.id
        }, status=201)


    # -----------------------------
    # 2️⃣ Submit / Update Answer
    # -----------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['attempt_id', 'question_id', 'selected_answer'],
            properties={
                'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'selected_answer': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description='Answer saved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "attempt_id, question_id and selected_answer required",
            404: "Attempt or Question not found"
        }
    )
    @action(detail=False, methods=['post'])
    def submit_answer(self, request):
        attempt_id = request.data.get("attempt_id")
        question_id = request.data.get("question_id")
        selected_answer = request.data.get("selected_answer")

        if not all([attempt_id, question_id, selected_answer]):
            return Response({"error": "attempt_id, question_id and selected_answer required"}, status=400)

        attempt = StudentListeningAttempt.objects.filter(
            id=attempt_id,
            student=request.user
        ).first()

        if not attempt:
            return Response({"error": "Attempt not found"}, status=404)

        question = ListeningActivityQuestion.objects.filter(id=question_id).first()
        if not question:
            return Response({"error": "Question not found"}, status=404)

        is_correct = question.is_correct_answer == selected_answer

        StudentListeningAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                "selected_answer": selected_answer,
                "is_correct": is_correct
            }
        )

        return Response({
            "message": "Answer saved",
            "is_correct": is_correct
        })


    # -----------------------------
    # 3️⃣ Complete Attempt
    # -----------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['attempt_id'],
            properties={
                'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={
            200: openapi.Response(
                description='Attempt completed',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'correct_answers': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT)
                    }
                )
            ),
            404: "Attempt not found"
        }
    )
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def complete(self, request):
        attempt_id = request.data.get("attempt_id")

        attempt = StudentListeningAttempt.objects.filter(
            id=attempt_id,
            student=request.user
        ).first()

        if not attempt:
            return Response({"error": "Attempt not found"}, status=404)

        if attempt.is_completed:
            return Response({"message": "Already completed"})

        total_questions = ListeningActivityQuestion.objects.filter(
            listening_activity=attempt.listening_activity
        ).count()

        correct_answers = attempt.answers.filter(is_correct=True).count()

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        attempt.total_questions = total_questions
        attempt.correct_answers = correct_answers
        attempt.score = score
        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            "message": "Attempt completed",
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score": score
        })


    # -----------------------------
    # 4️⃣ Get Attempt Result
    # -----------------------------
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='Attempt result',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'activity': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'correct_answers': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'answers': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                                'question': openapi.Schema(type=openapi.TYPE_STRING),
                                'selected_answer': openapi.Schema(type=openapi.TYPE_STRING),
                                'correct_answer': openapi.Schema(type=openapi.TYPE_STRING),
                                'is_correct': openapi.Schema(type=openapi.TYPE_BOOLEAN)
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
        attempt = StudentListeningAttempt.objects.filter(
            id=pk,
            student=request.user
        ).first()

        if not attempt:
            return Response({"error": "Attempt not found"}, status=404)

        answers = attempt.answers.all()

        return Response({
            "attempt_id": attempt.id,
            "activity": attempt.listening_activity.title,
            "total_questions": attempt.total_questions,
            "correct_answers": attempt.correct_answers,
            "score": attempt.score,
            "is_completed": attempt.is_completed,
            "answers": [
                {
                    "question": answer.question.question,
                    "selected_answer": answer.selected_answer,
                    "correct_answer": answer.question.is_correct_answer,
                    "is_correct": answer.is_correct
                }
                for answer in answers
            ]
        })