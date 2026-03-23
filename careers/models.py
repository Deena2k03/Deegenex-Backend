from django.db import models
from jobs.models import Job

from django.db import models
from jobs.models import Job
from utils.validators import validate_file_extension, validate_file_size # Import your security logic




class Application(models.Model):

    name = models.CharField(max_length=200)

    email = models.EmailField()

    phone = models.CharField(max_length=20)

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    resume = models.FileField(
        upload_to="resumes/", 
        validators=[validate_file_extension, validate_file_size]
    )

    dob = models.DateField(null=True, blank=True)

    gender = models.CharField(max_length=10, null=True, blank=True)
    
    experience = models.CharField(max_length=50, null=True, blank=True) # ADD THIS FIELD

    location = models.CharField(max_length=200, null=True, blank=True)

    qualification = models.CharField(max_length=200, null=True, blank=True)

    institution = models.CharField(max_length=200, null=True, blank=True)

    year = models.CharField(max_length=10, null=True, blank=True)

    cgpa = models.CharField(max_length=10, null=True, blank=True)

    skills = models.TextField(blank=True, null=True)
    
    ai_extracted_skills = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("applied", "Applied"),
            ("review", "Under Review"),
            ("interview", "Interview"),
            ("rejected", "Rejected"),
            ("selected", "Selected"),
        ],
        default="applied"
    )

    

    score = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"



