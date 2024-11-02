
from rest_framework import serializers
from .models import Meeting


# serializer class
class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'title', 'date', 'time', 'meeting_link', 'meeting_type', 'user']
