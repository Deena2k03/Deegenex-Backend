from django.urls import path
from .views import (
    schedule_client_meeting,
    reschedule_meeting,
    meeting_stats,
    meetings_list,
    meeting_detail,
    cancel_meeting,
    admin_reschedule_meeting,
    meetings_line_chart
)

urlpatterns = [

    path("schedule/", schedule_client_meeting),

    path("<int:meeting_id>/reschedule/", reschedule_meeting),

    path("stats/", meeting_stats),

    path("list/", meetings_list),

    path("meetings-chart/", meetings_line_chart),   # <-- chart API

    path("<int:meeting_id>/", meeting_detail),

    path("<int:meeting_id>/cancel/", cancel_meeting),

    path("<int:meeting_id>/admin-reschedule/", admin_reschedule_meeting)

]