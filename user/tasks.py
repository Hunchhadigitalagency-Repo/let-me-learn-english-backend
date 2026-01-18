from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

User = get_user_model()


def send_verification_email(user_id, verify_url):
    """
    Async task to send email verification link to user.
    """
    try:
        user = User.objects.get(id=user_id)

        
        subject = "Verify your email"
        message = render_to_string(
            "user/verify_email.html", 
            {
                "user": user,
                "verify_url": verify_url
            }
        )

        email = EmailMessage(
            subject=subject,
            body=message,
            to=[user.email],
        )
        email.content_subtype = "html"  
        email.send(fail_silently=False)

    except User.DoesNotExist:
        print(f"User with id {user_id} does not exist.")



from django.conf import settings

def send_password_reset_email(user_email, username, reset_token):
    subject = f"Password Reset Request for Basera Account"
    body = f"""
    Hello {username or 'User'},

    Your password reset token is: {reset_token}

    This token will expire in 3 hours.

    If you didn't request this, please ignore this email or contact support.

    Thank you,
    LetmeLearnEnglish Team
    """

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,  # Ensure from_email is provided
            to=[user_email],
        )
        email.content_subtype = "html"  
        email.send(fail_silently=False)
        print(f"Password reset email sent to {user_email}")

    except Exception as e:
       
        print(f"Failed to send password reset email to {user_email}: {e}")