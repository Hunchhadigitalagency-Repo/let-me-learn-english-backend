from rest_framework import serializers
from tasks.models import ListeningActivityQuestion
import json

# --------------------------
# Serializer for creating/updating a ListeningActivityQuestion
# --------------------------


# --------------------------
# Serializer for listing/retrieving a ListeningActivityQuestion
# --------------------------
from rest_framework import serializers
from tasks.models import ListeningActivityPart, ListeningActivityQuestion


# --------------------------
# Serializer for creating/updating a ListeningActivityQuestion
# --------------------------
class ListeningActivityQuestionCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ListeningActivityQuestion
        fields = [
            'id',
            # 'listening_activity_part',  # ✅ corrected
            'question_type',            # ✅ corrected
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer'
        ]


# --------------------------
# Serializer for listing/retrieving a ListeningActivityQuestion
# --------------------------
class ListeningActivityQuestionListSerializer(serializers.ModelSerializer):
    listening_activity_part = serializers.SerializerMethodField()

    class Meta:
        model = ListeningActivityQuestion
        fields = [
            'id',
            'listening_activity_part',  # ✅ corrected
            'question_type',            # ✅ corrected
            'question',
            'answer_1',
            'answer_2',
            'answer_3',
            'answer_4',
            'is_correct_answer'
        ]

    def get_listening_activity_part(self, obj):
        if obj.listening_activity_part:
            part = obj.listening_activity_part
            activity = part.listening_activity
            return {
                "part_id": part.id,
                "part_name": part.part,
                "listening_activity": {
                    "id": activity.id if activity else None,
                    "title": activity.title if activity else None,
                }
            }
        return None


# --------------------------
# Serializer for Creating ListeningActivityPart
# --------------------------
class ListeningActivityPartCreateSerializer(serializers.ModelSerializer):
    questions = ListeningActivityQuestionCreateSerializer(many=True, required=False)

    class Meta:
        model = ListeningActivityPart
        fields = [
            "id",
            "listening_activity",
            "part",
            "audio_file",
            "instruction",
            "duration",
            "questions",
        ]

    def to_internal_value(self, data):
        # 1. Make the data mutable (CRITICAL for multipart/form-data)
        if hasattr(data, 'dict'):
            data = data.dict()
        else:
            data = data.copy()

        # 2. Parse the JSON string into a Python list
        questions = data.get('questions')
        if isinstance(questions, str):
            try:
                data['questions'] = json.loads(questions)
            except json.JSONDecodeError:
                data['questions'] = []
        
        # 3. Call super with the modified dictionary
        return super().to_internal_value(data)

    def create(self, validated_data):
        # Extract questions
        questions_data = validated_data.pop("questions", [])
        
        # Create the part
        part = ListeningActivityPart.objects.create(**validated_data)

        # Create nested questions
        if questions_data:
            question_instances = [
                ListeningActivityQuestion(listening_activity_part=part, **q_data)
                for q_data in questions_data
            ]
            ListeningActivityQuestion.objects.bulk_create(question_instances)
        
        return part

    def update(self, instance, validated_data):
        print("\n===== UPDATE STARTED =====")
        print("Instance ID:", instance.id)
        print("Validated Data:", validated_data)

        questions_data = validated_data.pop("questions", [])
        print("Questions Data Received:", questions_data)

        # Update Part fields
        for attr, value in validated_data.items():
            print(f"Updating field -> {attr}: {value}")
            setattr(instance, attr, value)
        instance.save()

        sent_question_ids = []

        for q_data in questions_data:
            print("\nProcessing Question:", q_data)

            q_id = q_data.get('id')

            if q_id:
                print(f"Updating existing question ID: {q_id}")
                ListeningActivityQuestion.objects.filter(
                    id=q_id,
                    listening_activity_part=instance
                ).update(**q_data)

                sent_question_ids.append(q_id)

            else:
                print("Creating new question")
                new_q = ListeningActivityQuestion.objects.create(
                    listening_activity_part=instance,
                    **q_data
                )
                print("New Question ID:", new_q.id)
                sent_question_ids.append(new_q.id)
        instance.listeningactivityquestion_set.exclude(id__in=sent_question_ids).delete()
        print("Deleted questions not in payload")


        print("All Processed Question IDs:", sent_question_ids)
        print("===== UPDATE FINISHED =====\n")

        return instance