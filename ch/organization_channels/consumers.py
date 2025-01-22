import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import (Channel, Message, Link, Mention, ActivityChannel)
from django.utils import timezone
from channels.db import database_sync_to_async
from datetime import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Channel, Message, Link
from channels.db import database_sync_to_async
from datetime import datetime
import base64
from io import BytesIO
from django.core.files.base import ContentFile

class ChatConsumerNew(AsyncWebsocketConsumer):
   
    async def connect(self):
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = f'channel_{self.channel_id}'
        user = self.scope['user']

        try:
            channel = await database_sync_to_async(Channel.objects.get)(id=self.channel_id)

         
            if channel.visibility == 'PRIVATE' and user not in channel.allowed_members.all():
                await self.close()
                return
        except Channel.DoesNotExist:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope['user']
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        link_text = data.get('linkText', '')
        link_url = data.get('linkUrl', '')
        file_data = data.get('fileData', None)  
        file_type = data.get('fileType', None)  
        typing_status = data.get('typing', None)  

        username = self.scope['user'].username
        channel_id = self.channel_id
        user = self.scope['user']

        if typing_status is not None:
            # Handle typing status
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'username': username,
                    'is_typing': typing_status
                }
            )
            return

        if link_text and link_url:
            await self.save_link(channel_id, user, link_text, link_url)
        elif message:
            await self.save_message(channel_id, user, message)
        elif file_data and file_type:
            await self.save_audio_video_file(channel_id, user, file_data, file_type)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message or link_text,
                'username': username,
                'time': str(datetime.now().strftime('%H:%M')),
                'link': link_url if link_text else None,
                'file_url': file_data if file_data else None,
                'file_type': file_type if file_type else None,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'time': event['time'],
            'link': event.get('link', None),
            'file_url': event.get('file_url', None),
            'file_type': event.get('file_type', None),
        }))

    async def update_online_users(self, event):
       
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'online_users': event['online_users'],
        }))

    async def user_typing(self, event):
        """
        Handle typing status updates
        """
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def save_message(self, channel_id, user, message):
        channel = Channel.objects.get(id=channel_id)
        organization = channel.organization

        Message.objects.create(
            channel=channel,
            user=user,
            content=message,
            organization=organization
        )

        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        # Log the activity
        activity = ActivityChannel.objects.create(
           user=user,
           channel=channel,
           organization=organization,
           action_type='MESSAGE',
           content = f"{user.username}  dropped a message: {message} at {current_time} "

        )


    @database_sync_to_async
    def save_link(self, channel_id, user, link_text, link_url):
        channel = Channel.objects.get(id=channel_id)
        organization = channel.organization

        Link.objects.create(
            user=user,
            channel=channel,
            organization=organization,
            text=link_text,
            link=link_url
        )

        # Log the activity
        activity = ActivityChannel.objects.create(
           user=user,
           channel=channel,
           organization=organization,
           action_type='LINK',
           content=f'{user.username} shared a link {link_url} with wrapped text {link_text}'
        )
        

    @database_sync_to_async
    def save_audio_video_file(self, channel_id, user, file_data, file_type):
       
        file_name = f"{user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        file_data = base64.b64decode(file_data)

     
        file = ContentFile(file_data, name=file_name)

      
        channel = Channel.objects.get(id=channel_id)
        organization = channel.organization

 
        if file_type == 'audio':
            Message.objects.create(
                channel=channel,
                user=user,
                content=f"{user.username} uploaded an audio file.",
                organization=organization,
                audio=file
            )

            # Log the activity
            activity = ActivityChannel.objects.create(
               user=user,
               channel=channel,
               organization=organization,
               action_type='FILE_UPLOAD',
               content=f"{user.username} uploaded a file {file_type} - {file_data}"
             )
        elif file_type == 'video':
            Message.objects.create(
                channel=channel,
                user=user,
                content=f"{user.username} uploaded a video file.",
                organization=organization,
                video=file
            )
             # Log the activity
            activity = ActivityChannel.objects.create(
               user=user,
               channel=channel,
               organization=organization,
               action_type='FILE_UPLOAD',
               content=f"{user.username} uploaded a file {file_type} - {file_data}"
             )

        return f'/media/{file_name}'