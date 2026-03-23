from django.urls import path
from .views import (
    apply_job,
    application_list,
    update_application_status,
    application_detail,
    delete_application,
    dashboard_stats
)

urlpatterns = [
    path("apply-job/", apply_job),
    path("applications/", application_list),
    path("applications/<int:id>/", application_detail),
    path("applications/<int:id>/delete/", delete_application),

    # CHANGE THIS LINE to match your frontend fetch call:
    path("update-application-status/<int:id>/", update_application_status),

    path("dashboard-stats/", dashboard_stats),
]