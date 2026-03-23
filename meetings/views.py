from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.template.loader import render_to_string


# Models
from careers.models import Application, Application as Candidate  # Aliased for dashboard logic
from .models import Interview
from jobs.models import Job 
from client_meetings.models import ClientMeeting 
from axes.models import AccessAttempt 

# Services
from .google_meet import generate_meet_link, get_free_slots
from utils.email_service import send_email


@api_view(["POST"])
def schedule_interview(request):
    application_id = request.data.get("application_id")
    interview_date_str = request.data.get("interview_date")
    is_reschedule = request.data.get("reschedule") in [True, "true"]

    if not application_id or not interview_date_str:
        return Response({"error": "Missing data"}, status=400)

    dt = parse_datetime(interview_date_str)
    if not dt:
        return Response({"error": "Invalid date format"}, status=400)

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())

    date_display = dt.strftime("%d %B %Y")
    time_display = dt.strftime("%I:%M %p")

    try:
        application = Application.objects.get(id=application_id)
        Interview.objects.filter(application=application).delete()
        
        meet_link = generate_meet_link(dt, application.email)
        Interview.objects.create(application=application, interview_date=dt, meet_link=meet_link)

        application.status = "interview"
        application.save()

        resume_url = request.build_absolute_uri(application.resume.url) if application.resume else "#"
        subject = "Interview Rescheduled – Deegenex" if is_reschedule else "Interview Invitation – Deegenex"

        # 1. Candidate Email
        candidate_html = render_to_string("emails/interview_invitation.html", {
            "subject": subject,
            "candidate_name": application.name,
            "interview_date": date_display,
            "interview_time": time_display,
            "meet_link": meet_link
        })

        # 2. Admin Email
        admin_html = render_to_string("emails/admin_interview_scheduled.html", {
            "candidate_name": application.name,
            "candidate_email": application.email,
            "candidate_phone": application.phone,
            "resume_url": resume_url,
            "interview_date": date_display,
            "interview_time": time_display,
            "meet_link": meet_link
        })

        send_email(application.email, subject, candidate_html, from_email=settings.HR_EMAIL)
        send_email(settings.HR_EMAIL, f"Admin Alert: {subject} - {application.name}", admin_html, from_email=settings.HR_EMAIL)

        return Response({"message": "Interview scheduled", "meet_link": meet_link})
    
    except Application.DoesNotExist:
        return Response({"error": "Candidate not found"}, status=404)
    
    
@api_view(["GET"])
def available_slots(request):
    date = request.GET.get("date")
    if not date:
        return Response({"error": "Date required"}, status=400)
    try:
        slots = get_free_slots(date)
        return Response(slots)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def candidate_interviews(request, id):
    interviews = Interview.objects.filter(application_id=id)
    data = [{"date": i.interview_date, "meet_link": i.meet_link, "status": i.status} for i in interviews]
    return Response(data)

@api_view(["GET"])
def interview_list(request):
    interviews = Interview.objects.select_related("application").all()
    data = [{"application_name": i.application.name, "interview_date": i.interview_date, "meet_link": i.meet_link} for i in interviews]
    return Response(data)


# Backend/meetings/views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    # Calculate Status-Specific Counts
    applied_count = Candidate.objects.filter(status="applied").count()
    interview_count = Candidate.objects.filter(status="interview").count()
    selected_count = Candidate.objects.filter(status="selected").count()
    rejected_count = Candidate.objects.filter(status="rejected").count()

    # General Totals
    total_applications = Candidate.objects.count()
    total_jobs = Job.objects.count()
    total_meetings = ClientMeeting.objects.count()
    
    # FIX HERE: Changed 'failures_count' to 'failures_since_start'
    security_alerts = AccessAttempt.objects.filter(failures_since_start__gt=3).count()
    
    # Recent Activity (Using 'created_at' as discussed)
    recent_activity = Candidate.objects.all().order_by('-id')[:5].values('name', 'created_at')

    return Response({
        "applied": applied_count,
        "interview": interview_count,
        "selected": selected_count,
        "rejected": rejected_count,
        "total_applications": total_applications,
        "total_interviews": interview_count,
        "total_jobs": total_jobs,
        "total_meetings": total_meetings,
        "security_alerts": security_alerts,
        "recent_activity": list(recent_activity)
    })



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_reschedule_interview(request, interview_id):
    if not request.user.is_staff:
        return Response({"error": "Unauthorized Access"}, status=403)
        
    try:
        # Fetching by application_id passed from frontend
        interview = Interview.objects.get(application_id=interview_id)
        application = interview.application
        
        # Format the previous date for the HR summary
        previous_display = interview.interview_date.strftime("%d %B %Y at %I:%M %p")

        new_date_str = request.data.get("interview_date")
        reason = request.data.get("reason") or "Due to a scheduling adjustment on our side, your previously scheduled interview has been rescheduled."
        
        dt = parse_datetime(new_date_str)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())

        # Update Database
        interview.interview_date = dt
        interview.save()

        # Formatting data for templates
        date_display = dt.strftime("%d %B %Y")
        time_display = dt.strftime("%I:%M %p")
        resume_url = request.build_absolute_uri(application.resume.url) if application.resume else "#"

        # 1. CANDIDATE EMAIL
        candidate_html = render_to_string("emails/candidate_interview_rescheduled.html", {
            "subject": "Interview Schedule Updated – Deegenex",
            "candidate_name": application.name,
            "message": reason,
            "interview_date": date_display,
            "interview_time": time_display,
            "meet_link": interview.meet_link,
        })

        # 2. ADMIN/HR EMAIL
        admin_html = render_to_string("emails/admin_interview_rescheduled_alert.html", {
            "subject": "Admin Alert: Interview Rescheduled",
            "candidate_name": application.name,
            "candidate_email": application.email,
            "candidate_phone": application.phone,
            "resume_url": resume_url,
            "previous_schedule": previous_display,
            "new_schedule": f"{date_display} at {time_display}",
            "meet_link": interview.meet_link,
        })

        # Send Emails
        send_email(application.email, "Updated Interview Schedule – Deegenex", candidate_html, from_email=settings.HR_EMAIL)
        send_email(settings.HR_EMAIL, f"HR Alert: Rescheduled - {application.name}", admin_html, from_email=settings.HR_EMAIL)

        return Response({"message": f"Rescheduled to {time_display}"})

    except Exception as e:
        return Response({"error": str(e)}, status=500)