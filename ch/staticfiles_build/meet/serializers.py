
from rest_framework import serializers
from .models import Meeting


# serializer class
class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id','title', 'date', 'time', 'meeting_link', 'meeting_type','user']

    def create(self,validated_data):
        # set admin to the request.user
        validated_data['admin']= self.context['request'].user
        return super().create(validated_data)
    

