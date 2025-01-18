import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name= self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        self.room_group_name= f'chat_{self.room_name}'

        # join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # notify the group that a user has joined
        await self.channel_layer.group_send(self.room_group_name,{
            'type':'user_joined',
            'email':self.user.username
        })

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # notify the user     
        await self.channel_layer.group_send(
            self.room_group_name,{
                'type':'user_left',
                'email':self.user.username,
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if 'message' in data:
            message=data['message']
            email = self.user.username

            # send message to room group 
            await self.channel_layer.group_send(self.room_group_name,{
                'type':'chat_message',
                'message':message,
                'email':email
            }

                                                )    
        elif 'typing' in data:
            # send typing indicator 
            await self.channel_layer.group_send(self.room_group_name,{
                'type':'typing_indicator',
                'email':self.user.username
            })

    # handle user joined event 
    async def user_joined(self, event):
        email = event['email']

        await self.send(text_data=json.dumps({
            'user_joined': f"{email} has joined the room.",
            'email': email,  # Pass the email to the frontend
        })) 

    # handle user left event 
    async def user_left(self, event):
        email = event['email']
        await self.send(text_data=json.dumps({
            'user_left':f'{email} has left the room.',
            'email':email
        }))

    # handle chat message event 

    async def chat_message(self,  event):
        message = event['message']
        email =event['email']

        await self.send(text_data=json.dumps({
            'message':message,
            'email':email,
        })) 

    # handle typing indicator 

    async def typing_indicator(self, event):
        email = event['email']
        await self.send(text_data=json.dumps({
            'typing':f'{email} is typing...',
            'email':email
        }))                      

