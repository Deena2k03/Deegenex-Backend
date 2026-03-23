from django.db import models


class ClientMeeting(models.Model):

    name = models.CharField(max_length=200)

    company = models.CharField(max_length=200, blank=True, null=True)

    phone = models.CharField(max_length=20)

    email = models.EmailField()

    meeting_date = models.DateField()

    meeting_time = models.TimeField()

    message = models.TextField(blank=True, null=True)

    meet_link = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name