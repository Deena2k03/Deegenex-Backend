from django.db import models
from careers.models import Application

class Interview(models.Model):

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews"
    )

    interview_date = models.DateTimeField()

    meet_link = models.URLField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("scheduled","Scheduled"),
            ("completed","Completed"),
            ("cancelled","Cancelled")
        ],
        default="scheduled"
    )

    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview - {self.application.name}"