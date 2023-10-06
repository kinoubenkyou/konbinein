from celery import shared_task
from django.core.mail import send_mail
from django.utils.http import urlencode


@shared_task
def send_email_verification(email, email_verifying_token, uri_path):
    query = urlencode({"token": email_verifying_token})
    send_mail(
        from_email=None,
        message=f"{uri_path}?{query}",
        recipient_list=[email],
        subject="Konbinein Email Verification",
    )
