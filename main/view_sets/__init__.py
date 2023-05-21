from django.core.mail import send_mail
from django.utils.http import urlencode
from rest_framework.reverse import reverse


def send_email_verification(request, user):
    uri_path = reverse(
        "public-user-email-verifying",
        kwargs={"pk": user.id},
        request=request,
    )
    query = urlencode({"token": user.email_verifying_token})
    send_mail(
        from_email=None,
        message=f"{uri_path}?{query}",
        recipient_list=(user.email,),
        subject="Konbinein Email Verification",
    )
