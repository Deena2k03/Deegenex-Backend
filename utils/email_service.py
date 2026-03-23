from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_email(to_email, subject, content, from_email=None):

    # If sender not provided → use default EMAIL_FROM
    if not from_email:
        from_email = settings.EMAIL_FROM

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)

    except Exception as e:
        print("SendGrid Error:", e)