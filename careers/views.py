from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from django.template.loader import render_to_string
import os
from django.template.loader import render_to_string

from django.conf import settings

from .models import Application
from .serializers import ApplicationSerializer
from utils.email_service import send_email
from utils.resume_ai import score_resume, extract_text, extract_skills


from rest_framework.decorators import api_view, permission_classes # Add permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.pagination import PageNumberPagination

class ApplicationPagination(PageNumberPagination):
    page_size = 100

def load_css(file_name):
    path = os.path.join(settings.BASE_DIR, "static", "email_css", file_name)
    with open(path) as f:
        return f.read()

# ============================
# Apply Job
# ============================

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def apply_job(request):
    serializer = ApplicationSerializer(data=request.data)

    if serializer.is_valid():
        application = serializer.save()

        try:
            resume_path = application.resume.path
            job_desc = application.job.description if application.job else ""
            raw_text = extract_text(resume_path)

            # Extract skills & score
            found = extract_skills(raw_text)
            application.ai_extracted_skills = ", ".join(found) if found else "No matching skills found"
            application.score = score_resume(resume_path, job_desc)
            application.save()
        except Exception as e:
            print(f"AI Error: {e}")
            application.ai_extracted_skills = "AI Processing Failed"
            application.save()

        job_name = application.job.title if application.job else "General Position"
        resume_full_url = request.build_absolute_uri(application.resume.url)

        # 1. Send Email to Candidate (Matched to your file: candidate_application.html)
        candidate_html = render_to_string(
            "emails/candidate_application.html", 
            {
                "candidate_name": application.name,
                "job_title": job_name
            }
        )

        send_email(
            application.email,
            "Application Received – Deegenex",
            candidate_html,
            settings.HR_EMAIL
        )

        # 2. Send Email to HR (Matched to your file: hr_new_application.html)
        hr_html = render_to_string(
            "emails/hr_new_application.html", 
            {
                "candidate_name": application.name,
                "candidate_email": application.email,
                "mobile_num": application.phone,
                "job_title": job_name,
                "resume_url": resume_full_url,
            }
        )

        send_email(
            settings.HR_EMAIL,
            f"New Application: {application.name} for {job_name}",
            hr_html,
            settings.HR_EMAIL
        )

        return Response({"message": "Success"}, status=201)

    return Response(serializer.errors, status=400)


# ============================
# List Applications
# ============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_list(request):
    # CHANGED: Ordered by '-id' so the newest registrations appear at the top
    # You can also use '-created_at' if you have a timestamp field
    applications = Application.objects.all().order_by('-id')

    paginator = ApplicationPagination()
    result = paginator.paginate_queryset(applications, request)

    data = []
    for app in result:
        interview = app.interviews.last()
        data.append({
            "id": app.id,
            "name": app.name,
            "email": app.email,
            "job_title": app.job.title if app.job else None,
            "status": app.status,
            "skills": app.skills,
            "created_at": app.created_at,
            "meet_link": interview.meet_link if interview else None
        })

    return paginator.get_paginated_response(data)


# ============================
# Update Candidate Status
# ============================

@api_view(['PATCH'])
def update_application_status(request, id):

    try:
        application = Application.objects.get(id=id)

    except Application.DoesNotExist:

        return Response(
            {"error": "Application not found"},
            status=404
        )

    status_value = request.data.get("status")

    application.status = status_value
    application.save()

    return Response({
        "message": "Status updated",
        "status": application.status
    })



# ============================
# Get Single Candidate
# ============================

@api_view(['GET'])
def application_detail(request, id):

    try:
        application = Application.objects.get(id=id)

    except Application.DoesNotExist:
        return Response({"error": "Candidate not found"}, status=404)

    serializer = ApplicationSerializer(application)

    return Response(serializer.data)


# ============================
# Delete Candidate
# ============================

@api_view(['DELETE'])
def delete_application(request, id):

    try:
        application = Application.objects.get(id=id)

    except Application.DoesNotExist:
        return Response({"error": "Candidate not found"}, status=404)

    application.delete()

    return Response({
        "message": "Candidate deleted successfully"
    })



# ============================
# Dashboard Stats
# ============================

from meetings.models import Interview

@api_view(["GET"])
def dashboard_stats(request):
    # Counts
    total_applications = Application.objects.count()
    selected = Application.objects.filter(status="selected").count()
    rejected = Application.objects.filter(status="rejected").count()
    applied = Application.objects.filter(status="applied").count()
    interview = Application.objects.filter(status="interview").count()
    
    # Security alerts (example logic)
    from axes.models import AccessAttempt
    security_alerts = AccessAttempt.objects.filter(failures_since_start__gt=3).count()

    # --- ADD THIS SECTION TO FIX THE ERROR ---
    # Fetch the 5 most recent candidates
    recent_data = Application.objects.all().order_by('-id')[:5].values('id', 'name', 'created_at')
    
    return Response({
        "total_applications": total_applications,
        "total_interviews": Interview.objects.count(),
        "selected": selected,
        "rejected": rejected,
        "applied": applied,
        "interview": interview,
        "security_alerts": security_alerts,
        "recent_activity": list(recent_data) # This provides the 'map' property
    })
