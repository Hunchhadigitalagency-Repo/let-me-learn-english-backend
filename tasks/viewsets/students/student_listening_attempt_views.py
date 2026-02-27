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
    StudentListeningAnswer,
    StudentSpeakingAttempt
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
            required=['attempt_id', 'answers'],
            properties={
                'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'answers': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        required=['question_id', 'selected_answer'],
                        properties={
                            'question_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'selected_answer': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            }
        ),
        responses={
            200: openapi.Response(
                description='Answers saved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'correct_answers': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'current_score': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "attempt_id and answers array required",
            404: "Attempt or Question not found"
        }
    )

    @action(detail=False, methods=['post'])
    def submit_answer(self, request):
        attempt_id = request.data.get("attempt_id")
        answers = request.data.get("answers")

        if not attempt_id or not isinstance(answers, list):
            return Response(
                {"detail": "attempt_id and answers array are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        attempt = StudentListeningAttempt.objects.filter(
            id=attempt_id,
            student=request.user
        ).first()

        if not attempt:
            return Response({"detail": "Attempt not found"}, status=404)

        # -----------------------------
        # 1️⃣ Collect all question IDs
        # -----------------------------
        question_ids = [item.get("question_id") for item in answers if item.get("question_id")]
        if not question_ids:
            return Response({"detail": "No valid question_id provided"}, status=400)

        # -----------------------------
        # 2️⃣ Fetch all questions in ONE query
        # -----------------------------
        questions = ListeningActivityQuestion.objects.filter(id__in=question_ids)
        question_map = {q.id: q for q in questions}

        if len(question_map) != len(set(question_ids)):
            return Response({"detail": "One or more questions not found"}, status=404)

        # -----------------------------
        # 3️⃣ Process answers
        # -----------------------------
        for item in answers:
            question_id = item.get("question_id")
            selected_answer = item.get("selected_answer")
            if not question_id or not selected_answer:
                continue

            question = question_map.get(question_id)
            is_correct = question.is_correct_answer.strip().lower() == selected_answer.strip().lower()

            StudentListeningAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    "selected_answer": selected_answer,
                    "is_correct": is_correct
                }
            )

        # -----------------------------
        # 4️⃣ Recalculate Score
        # -----------------------------
        correct_count = StudentListeningAnswer.objects.filter(
            attempt=attempt,
            is_correct=True
        ).count()

        attempt.correct_answers = correct_count
        attempt.score = (correct_count / attempt.total_questions * 100) if attempt.total_questions > 0 else 0

        # Optional: Auto-complete attempt when all answered
        if StudentListeningAnswer.objects.filter(attempt=attempt).count() == attempt.total_questions:
            attempt.is_completed = True

        attempt.save()

        return Response({
            "total_questions": attempt.total_questions,
            "correct_answers": correct_count,
            "current_score": attempt.score,
            "is_completed": attempt.is_completed
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

        parts = attempt.listening_activity.listeningactivitypart_set.all()


        total_questions = ListeningActivityQuestion.objects.filter(
            listening_activity_part__in=parts
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
        method='get',
        responses={
            200: openapi.Response(
                description='Attempt result',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'activity': openapi.Schema(type=openapi.TYPE_STRING),
                        'activity_detail': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'correct_answers': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'score': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'duration_seconds': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'answers': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT)
                        )
                    }
                )
            ),
            404: "Attempt not found"
        }
    )
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        # Fetch attempt
        attempt = StudentListeningAttempt.objects.filter(
            id=pk,
            student=request.user
        ).select_related("listening_activity") \
        .prefetch_related("answers__question__listening_activity_part") \
        .first()

        if not attempt:
            return Response({"error": "Attempt not found"}, status=404)

        answers = attempt.answers.all()

        # Calculate duration
        duration = None
        if attempt.completed_at:
            duration = int((attempt.completed_at - attempt.started_at).total_seconds())

        activity = attempt.listening_activity

        activity_detail = {
            "id": activity.id,
            "title": activity.title,
            "duration": activity.duration,
            "instruction": activity.instruction,
            "audio_file": request.build_absolute_uri(activity.audio_file.url)
            if activity.audio_file else None
        }

        answer_list = []
        for answer in answers:
            q = answer.question
            part = None
            part_audio = None
            if q.listening_activity_part:
                part = q.listening_activity_part.part
                if q.listening_activity_part.audio_file:
                    part_audio = request.build_absolute_uri(q.listening_activity_part.audio_file.url)

            # Include all options and correct answer for all question types
            options = {
                "answer_1": q.answer_1,
                "answer_2": q.answer_2,
                "answer_3": q.answer_3,
                "answer_4": q.answer_4,
            }

            correct_answer = q.is_correct_answer

            answer_list.append({
                "question_id": q.id,
                "bundle_id": str(q.bundle_id),
                "question": q.question,
                "question_type": q.question_type,
                "selected_answer": answer.selected_answer,
                "is_correct": answer.is_correct,
                "part": part,
                "part_audio": part_audio,
                "options": options,
                "correct_answer": correct_answer,
                # "created_at": answer.created_at if answer.created_at else None,  # ✅ use answer's created_at

            })

        return Response({
            "attempt_id": attempt.id,
            "activity": activity.title,
            "activity_detail": activity_detail,
            "total_questions": attempt.total_questions,
            "correct_answers": attempt.correct_answers,
            "score": attempt.score,
            "is_completed": attempt.is_completed,
            "duration_seconds": duration,
            "answers": answer_list
        })