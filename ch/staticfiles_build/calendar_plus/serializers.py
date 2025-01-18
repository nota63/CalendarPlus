# serializers.py
from rest_framework import serializers
from .models import Availability

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'user', 'day_of_week', 'start_time', 'end_time', 'meeting_duration', 'buffer_time', 'is_recurring', 'is_booked']