import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Channel
from channels.db import database_sync_to_async

class ChatConsumerNew(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = f'channel_{self.channel_id}'

        try:
          
            channel = await database_sync_to_async(Channel.objects.get)(id=self.channel_id)

          
            if channel.visibility == 'PRIVATE' and self.scope['user'] not in channel.allowed_members.all():
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
     
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
     
        data = json.loads(text_data)
        message = data['message']
        username = self.scope['user'].username

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
    
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))

    @database_sync_to_async
    def get_channel(self, channel_id):
       
        return Channel.objects.get(id=channel_id)
