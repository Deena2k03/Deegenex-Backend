from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes # Added this
from rest_framework.permissions import AllowAny # Added this
from rest_framework.response import Response
from utils.email_service import send_email

@api_view(["POST"])
@permission_classes([AllowAny])
def contact_us(request):
    data = request.data
    context = {
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone", "Not Provided"),
        "subject": data.get("subject"),
        "message": data.get("message"),
    }

    try:
        # 1. Render Admin Email
        admin_html = render_to_string("emails/admin_contact_inquiry.html", context)
        send_email("info@deegenex.com", f"New Inquiry: {context['subject']}", admin_html, from_email=settings.EMAIL_FROM)
        
        # 2. Render Client Email
        client_html = render_to_string("emails/user_contact_receipt.html", context)
        send_email(context['email'], "We've received your message! – Deegenex", client_html, from_email=settings.EMAIL_FROM)

        return Response({"message": "Inquiry sent successfully"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)