from django.db import models

class Job(models.Model):

    slug = models.SlugField(unique=True)

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300)

    image = models.ImageField(upload_to="jobs/")

    overview = models.TextField()
    description = models.TextField()

    responsibilities = models.JSONField(default=list)
    qualifications = models.JSONField(default=list)
    technical = models.JSONField(default=list)
    experience = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title