from celery import shared_task
from django.core.mail import send_mail
from django.utils.http import urlencode
from rest_framework.reverse import reverse


@shared_task
def send_email(message, recipient_list, subject):
    send_mail(
        from_email=None, message=message, recipient_list=recipient_list, subject=subject
    )


def send_email_verification(request, user):
    uri_path = reverse(
        "public-user-email-verifying",
        kwargs={"pk": user.id},
        request=request,
    )
    query = urlencode({"token": user.email_verifying_token})
    send_email.delay(
        message=f"{uri_path}?{query}",
        recipient_list=[user.email],
        subject="Konbinein Email Verification",
    )
