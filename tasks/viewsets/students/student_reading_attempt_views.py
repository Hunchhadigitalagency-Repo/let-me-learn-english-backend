# tasks/viewsets/student_reading_attempt_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from tasks.models import (
    ReadingActivity,
    ReadingAcitivityQuestion,
    StudentReadingAttempt,
    StudentReadingAnswer
)
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

class StudentReadingAttemptViewSet(viewsets.ViewSet):
    """
    students.reading_attempt
    Handles:
    - Start reading attempt
    - Submit/update answer
    - Complete attempt
    - Get attempt result
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    # -----------------------------
    # 1️⃣ Start Reading Attempt
    # -----------------------------
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['reading_activity_id'],
            properties={
                'reading_activity_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the Reading Activity to start'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description='Attempt started',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'attempt_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'reading_activity': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'started_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                    }
                )
            ),
            400: "reading_activity_id is required",
            404: "Reading activity not found"
        }
    )
    @action(detail=False, methods=["post"], url_path="start")
    def start_attempt(self, request):
        reading_activity_id = request.data.get("reading_activity_id")

        if not reading_activity_id:
            return Response(
                {"detail": "reading_activity_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        reading_activity = get_object_or_404(
            ReadingActivity,
            id=reading_activity_id
        )

        attempt, created = StudentReadingAttempt.objects.get_or_create(
            student=request.user,
            reading_activity=reading_activity,
            is_completed=False,
            defaults={
                "total_questions": reading_activity.readingacitivityquestion_set.count()
            }
        )

        return Response({
            "attempt_id": attempt.id,
            "reading_activity": reading_activity.title,
            "total_questions": attempt.total_questions,
            "started_at": attempt.started_at
        })


    # -----------------------------
    # 2️⃣ Submit Answer
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
    )
    @action(detail=False, methods=["post"], url_path="submit-answer")
    def submit_answer(self, request):
        attempt_id = request.data.get("attempt_id")
        answers = request.data.get("answers")

        if not attempt_id or not isinstance(answers, list):
            return Response(
                {"detail": "attempt_id and answers array are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        attempt = get_object_or_404(
            StudentReadingAttempt,
            id=attempt_id,
            student=request.user
        )

        if attempt.is_completed:
            return Response(
                {"detail": "Attempt already completed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # 1️⃣ Collect all question IDs
        # -----------------------------
        question_ids = [
            item.get("question_id")
            for item in answers
            if item.get("question_id")
        ]

        if not question_ids:
            return Response(
                {"detail": "No valid question_id provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # 2️⃣ Fetch all questions in ONE query
        # -----------------------------
        questions = ReadingAcitivityQuestion.objects.filter(
            id__in=question_ids
        )

        question_map = {q.id: q for q in questions}

        # Validate missing questions
        if len(question_map) != len(set(question_ids)):
            return Response(
                {"detail": "One or more questions not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # -----------------------------
        # 3️⃣ Process answers
        # -----------------------------
        for item in answers:
            question_id = item.get("question_id")
            selected_answer = item.get("selected_answer")

            if not question_id or not selected_answer:
                continue

            question = question_map.get(question_id)

            is_correct = (
                selected_answer.strip().lower()
                == question.is_correct_answer.strip().lower()
            )

            StudentReadingAnswer.objects.update_or_create(
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
        correct_count = StudentReadingAnswer.objects.filter(
            attempt=attempt,
            is_correct=True
        ).count()

        attempt.correct_answers = correct_count
        attempt.score = (
            (correct_count / attempt.total_questions) * 100
            if attempt.total_questions > 0 else 0
        )

        # Optional: Auto-complete when all answered
        if StudentReadingAnswer.objects.filter(attempt=attempt).count() == attempt.total_questions:
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
                        'final_score': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'correct_answers': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: "You must answer all questions before completing",
            404: "Attempt not found"
        }
    )
    @action(detail=False, methods=["post"], url_path="complete")
    def complete_attempt(self, request):
        attempt_id = request.data.get("attempt_id")

        attempt = get_object_or_404(
            StudentReadingAttempt,
            id=attempt_id,
            student=request.user
        )

        answered_count = attempt.answers.count()

        if answered_count < attempt.total_questions:
            return Response(
                {
                    "detail": "You must answer all questions before completing.",
                    "answered": answered_count,
                    "total": attempt.total_questions
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            "message": "Reading attempt completed successfully.",
            "final_score": attempt.score,
            "correct_answers": attempt.correct_answers,
            "total_questions": attempt.total_questions
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
        attempt = StudentReadingAttempt.objects.filter(
            id=pk,
            student=request.user
        ).select_related("reading_activity").prefetch_related("answers__question").first()

        if not attempt:
            return Response({"error": "Attempt not found"}, status=404)

        answers = attempt.answers.all()

        duration = None
        if attempt.completed_at:
            duration_delta = attempt.completed_at - attempt.started_at
            duration = int(duration_delta.total_seconds())
        def question_details(q):
            qtype = getattr(q, "type", None)
            base = {
                "id": q.id,
                "question": q.question,
                "type": qtype,
                "instruction": getattr(q, "instruction", None)
            }

            if qtype == "mcq":
                options = [
                    getattr(q, "answer_1", None),
                    getattr(q, "answer_2", None),
                    getattr(q, "answer_3", None),
                    getattr(q, "answer_4", None),
                ]
                # filter out empty/None options
                base["options"] = [o for o in options if o]
            else:
                # for other types just include the main question text (already present)
                base["text"] = q.question

            return base

        # include detailed activity info for the frontend
        activity = attempt.reading_activity
        activity_detail = {
            "id": getattr(activity, "id", None),
            "title": getattr(activity, "title", None),
            "passage": getattr(activity, "passage", None),
            "instruction": getattr(activity, "instruction", None),
            "duration": getattr(activity, "duration", None),
            "file": request.build_absolute_uri(getattr(getattr(activity, "file", None), "url", None)),
            "task": {
                "id": getattr(getattr(activity, "task", None), "id", None),
                "name": getattr(getattr(activity, "task", None), "name", None)
            }
        }

        return Response({
            "attempt_id": attempt.id,
            "activity": attempt.reading_activity.title,
            "activity_detail": activity_detail,
            "total_questions": attempt.total_questions,
            "correct_answers": attempt.correct_answers,
            "score": attempt.score,
            "is_completed": attempt.is_completed,
            "duration_seconds": duration,
            "answers": [
                {
                    "question": question_details(answer.question),
                    "selected_answer": answer.selected_answer,
                    "correct_answer": answer.question.is_correct_answer,
                    "is_correct": answer.is_correct
                }
                for answer in answers
            ]
        })