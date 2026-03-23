from django.urls import path
from .views import (
    schedule_interview, 
    available_slots, 
    candidate_interviews, 
    interview_list, 
    admin_reschedule_interview
)

urlpatterns = [
    path("schedule-interview/", schedule_interview),
    path("available-slots/", available_slots),
    path("candidate-interviews/<int:id>/", candidate_interviews, name='candidate_interviews'),
    
    # FIX: Removed 'api/' from the start of the path
    path("admin-reschedule-interview/<int:interview_id>/", admin_reschedule_interview),
    
    path('', interview_list, name='interview_list'),
]