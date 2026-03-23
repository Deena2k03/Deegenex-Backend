from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
from datetime import date

from .models import ClientMeeting
from .serializers import ClientMeetingSerializer
from meetings.google_meet import generate_meet_link
from utils.email_service import send_email
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes # Add this
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string

@api_view(["POST"])
def schedule_client_meeting(request):
    serializer = ClientMeetingSerializer(data=request.data)

    if serializer.is_valid():
        meeting = serializer.save()
        display_time = meeting.meeting_time.strftime("%I:%M %p")
        
        start_time = datetime.datetime.combine(meeting.meeting_date, meeting.meeting_time)
        meet_link = generate_meet_link(start_time, meeting.email)
        meeting.meet_link = meet_link
        meeting.save()

        # 1. Generate Client Email
        client_html = render_to_string("emails/client_meeting_confirmed.html", {
            "client_name": meeting.name,
            "meeting_date": meeting.meeting_date,
            "meeting_time": display_time,
            "meet_link": meet_link,
            "reschedule_url": f"{settings.FRONTEND_URL}/reschedule/{meeting.id}"
        })

        # 2. Generate Admin Email
        admin_html = render_to_string("emails/admin_meeting_scheduled.html", {
            "client_name": meeting.name,
            "company_name": meeting.company,
            "client_mobile": meeting.phone,
            "meeting_date": meeting.meeting_date,
            "meeting_time": display_time,
            "meet_link": meet_link
        })

        send_email(meeting.email, "Meeting Confirmation – Deegenex", client_html, from_email=settings.EMAIL_FROM)
        send_email(settings.EMAIL_FROM, "New Client Meeting Scheduled", admin_html, from_email=settings.EMAIL_FROM)

        return Response({"message": "Meeting Scheduled", "meet_link": meet_link})

    return Response(serializer.errors, status=400)


@api_view(["POST"])
def reschedule_meeting(request, meeting_id):
    try:
        meeting = ClientMeeting.objects.get(id=meeting_id)
    except ClientMeeting.DoesNotExist:
        return Response({"error": "Meeting not found"}, status=404)

    new_date = request.data.get("date")
    new_time_str = request.data.get("time")

    if not new_date or not new_time_str:
        return Response({"error": "Date and time required"}, status=400)

    # Store previous for admin notification
    previous_date = meeting.meeting_date
    previous_time = meeting.meeting_time.strftime("%I:%M %p")
    
    # Update logic
    # Make sure new_time_str is in 'HH:MM' 24h format from your frontend
    time_obj = datetime.datetime.strptime(new_time_str, '%H:%M').time()
    meeting.meeting_date = new_date
    meeting.meeting_time = time_obj
    meeting.save()

    display_time = time_obj.strftime("%I:%M %p")

    # 1. Render Client HTML
    client_html = render_to_string("emails/client_meeting_rescheduled.html", {
        "client_name": meeting.name,
        "meeting_date": meeting.meeting_date,
        "meeting_time": display_time,
        "meet_link": meeting.meet_link,
        "reschedule_url": f"{settings.FRONTEND_URL}/reschedule/{meeting.id}"
    })

    # 2. Render Admin HTML (FIXED client_mobile line)
    admin_html = render_to_string("emails/admin_meeting_rescheduled.html", {
        "client_name": meeting.name,
        "company_name": meeting.company,
        "client_email": meeting.email,
        "client_mobile": meeting.phone,  # CHANGED from .mobile to .phone
        "previous_meeting": f"{previous_date} at {previous_time}",
        "new_meeting": f"{meeting.meeting_date} at {display_time}",
        "meet_link": meeting.meet_link
    })

    # Sending emails
    send_email(meeting.email, "Meeting Rescheduled – Deegenex", client_html, from_email=settings.EMAIL_FROM)
    send_email(settings.EMAIL_FROM, "Client Meeting Rescheduled – Deegenex", admin_html, from_email=settings.EMAIL_FROM)

    return Response({
        "message": f"Meeting rescheduled successfully to {display_time}",
        "meet_link": meeting.meet_link
    })

# ... keep meeting_stats, meetings_list, meeting_detail, cancel_meeting same ...

@api_view(["POST"])
def admin_reschedule_meeting(request, meeting_id):
    try:
        meeting = ClientMeeting.objects.get(id=meeting_id)
    except ClientMeeting.DoesNotExist:
        return Response({"error": "Meeting not found"}, status=404)

    previous_date = meeting.meeting_date
    previous_time = meeting.meeting_time.strftime("%I:%M %p")

    new_date = request.data.get("date")
    new_time_str = request.data.get("time")
    message = request.data.get("message")

    # Convert HH:MM to time object
    time_obj = datetime.datetime.strptime(new_time_str, '%H:%M').time()

    meeting.meeting_date = new_date
    meeting.meeting_time = time_obj
    meeting.save()

    display_time = time_obj.strftime("%I:%M %p")

    if not message:
        message = "Due to a scheduling adjustment on our side, your previously scheduled meeting has been rescheduled to a new date and time."

    # 1. Render Client Email
    client_html = render_to_string("emails/client_admin_rescheduled.html", {
        "client_name": meeting.name,
        "message": message,
        "new_date": new_date,
        "new_time": display_time,
        "meet_link": meeting.meet_link,
        "reschedule_url": f"{settings.FRONTEND_URL}/reschedule/{meeting.id}"
    })

    # 2. Render Admin Email (with all client details)
    admin_html = render_to_string("emails/admin_reschedule_summary.html", {
        "client_name": meeting.name,
        "client_email": meeting.email,
        "client_phone": meeting.phone,
        "company_name": meeting.company,
        "previous_meeting": f"{previous_date} at {previous_time}",
        "new_meeting": f"{new_date} at {display_time}",
        "meet_link": meeting.meet_link
    })

    send_email(meeting.email, "Meeting Rescheduled – Updated Details", client_html, from_email=settings.EMAIL_FROM)
    send_email(settings.EMAIL_FROM, "Meeting Rescheduled by Admin – Deegenex", admin_html, from_email=settings.EMAIL_FROM)

    return Response({"message": "Meeting rescheduled successfully"})




@api_view(["GET"])
def meeting_stats(request):

    today = date.today()

    completed = ClientMeeting.objects.filter(
        meeting_date__lt=today
    ).count()

    this_month = ClientMeeting.objects.filter(
        meeting_date__month=today.month
    ).count()

    last_month = ClientMeeting.objects.filter(
        meeting_date__month=today.month - 1
    ).count()

    return Response({
        "completed_meetings": completed,
        "this_month_meetings": this_month,
        "last_month_meetings": last_month
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated]) # Added security
def meetings_list(request):

    meetings = ClientMeeting.objects.all().order_by("-meeting_date")

    serializer = ClientMeetingSerializer(meetings, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def meeting_detail(request, meeting_id):

    meeting = ClientMeeting.objects.get(id=meeting_id)

    serializer = ClientMeetingSerializer(meeting)

    return Response(serializer.data)


@api_view(["POST"])
def cancel_meeting(request, meeting_id):

    meeting = ClientMeeting.objects.get(id=meeting_id)

    meeting.delete()

    return Response({
        "message": "Meeting cancelled successfully"
    })






@api_view(["GET"])
@permission_classes([IsAuthenticated])
def meetings_line_chart(request):

    from django.db.models.functions import TruncMonth
    from django.db.models import Count

    meetings = (
        ClientMeeting.objects
        .annotate(month=TruncMonth("meeting_date"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    labels = []
    data = []

    for m in meetings:
        labels.append(m["month"].strftime("%b"))
        data.append(m["total"])

    return Response({
        "labels": labels,
        "data": data
    })


