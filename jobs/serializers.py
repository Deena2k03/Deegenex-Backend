from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = "__all__"

    def get_image(self, obj):
        request = self.context.get('request')

        if obj.image:
            return obj.image.url

        return None
