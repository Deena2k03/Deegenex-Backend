from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):

    job_title = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = "__all__"

    def get_job_title(self, obj):

        if obj.job:
            return obj.job.title

        return None


    def validate_resume(self, value):

        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF files are allowed."
            )

        max_size = 5 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "File size must be under 5MB."
            )

        return value




