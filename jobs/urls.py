from django.urls import path
from .views import get_jobs, get_job, create_job, delete_job, update_job

urlpatterns = [

    path("jobs/", get_jobs),

    path("jobs/create/", create_job),

    path("jobs/update/<int:id>/", update_job),

    path("jobs/delete/<int:id>/", delete_job),

    # job by ID
    path("jobs/<int:id>/", get_job),

    # job by SLUG
    path("jobs/<slug:slug>/", get_job),

]