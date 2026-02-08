from rest_framework import serializers
from tasks.models import (
    ReadingActivity,
    ReadingAcitivityQuestion,
    StudentReadingAttempt,
    StudentReadingAnswer
)
from tasks.serializers import ReadingQuestionSerializer