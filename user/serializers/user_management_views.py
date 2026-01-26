from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from user.models import UserProfile
from rest_framework.permissions import IsAuthenticated
User = get_user_model()


class UserDropdownAPIView(APIView):
    """
    Get users for dropdown (id, name, profile)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = (
            User.objects
            .filter(is_active=True)
            .select_related()
            .order_by("id")
        )

        data = []

        for user in users:
            profile = UserProfile.objects.filter(user=user).first()

            # profile image priority
            if profile and profile.profile_picture:
                profile_image = request.build_absolute_uri(
                    profile.profile_picture.url
                )
            elif profile and profile.google_avatar:
                profile_image = profile.google_avatar
            else:
                profile_image = None

            data.append({
                "id": user.id,
                "name": user.get_full_name() or user.email,
                "profile": profile_image
            })

        return Response(data)
