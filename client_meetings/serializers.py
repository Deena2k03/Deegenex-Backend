from rest_framework import serializers
from .models import ClientMeeting


class ClientMeetingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientMeeting
        fields = "__all__"