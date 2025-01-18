import json
from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import MeetingRoom, MeetingNotes
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import MeetingRoom, MeetingNotes
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from django.db import IntegrityError
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import MeetingRoom, MeetingNotes
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class MeetingNotesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.org_id = self.scope['url_route']['kwargs']['org_id']
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        self.room_name = f"{self.org_id}-{self.meeting_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        # Accept WebSocket connection
        await self.accept()

        # Send the initial participants list after accepting connection
        participants = await self.get_participants_in_room()
        await self.send(text_data=json.dumps({
            'type': 'participants_list',
            'participants': participants
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json.get('type')

        if event_type == 'typing':
            # Handle typing event
            user_id = text_data_json['user_id']
            is_typing = text_data_json['is_typing']
            user_name = await self.get_user_name(user_id)

            # Broadcast typing event to group
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'typing_event',
                    'user_name': user_name,
                    'is_typing': is_typing
                }
            )

            # Log typing activity
            await self.broadcast_change_log(f"{user_name} is typing...")

       
        elif event_type == 'note_update':
        # Handle note update
         content = text_data_json['content']
         user_id = text_data_json['user_id']

        # Debug: Log user_id to confirm it's being sent
         print(f"Debug: Received user_id = {user_id}")

         user_name = await self.get_user_name(user_id)
        
         if not user_name:
            print(f"Warning: User with id {user_id} not found!")  # Debug warning
        
         await self.save_notes(user_id, content)

        # Broadcast note update
         await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'note_update',
                'content': content,
                'user_name':user_name,
            }
        )

        # Log note update
         change_log_message = f"{user_name} updated the notes." if user_name else "An unknown user updated the notes."
         print('Notes updated by:', change_log_message)
         await self.broadcast_change_log(change_log_message)


        elif event_type == 'emoji_inserted':
           
            emoji = text_data_json['emoji']
            user_id = text_data_json['user_id']
            user_name = await self.get_user_name(user_id)

    
            await self.insert_emoji(user_id, emoji)

          
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'emoji_inserted',
                    'emoji': emoji,
                    'user_name': user_name
                }
            )

     
            await self.broadcast_change_log(f"{user_name} inserted emoji: {emoji}")

        elif event_type == 'mention':
       
            mentioned_user = text_data_json['mentioned_user']
            user_id = text_data_json['user_id']
            user_name = await self.get_user_name(user_id)

      
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'mention_event',
                    'user_name': user_name,
                    'mentioned_user': mentioned_user
                }
            )

        
            await self.broadcast_change_log(f"{user_name} mentioned {mentioned_user}.")   

        # screen share 
        elif event_type == 'offer':
            
            offer = text_data_json['offer']
            await self.handle_offer(offer)

        elif event_type == 'screen-share-start':
          
            user_id = text_data_json['user_id']
            user_name = await self.get_user_name(user_id)

            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'screen_share_started',
                    'user_id': user_id,
                    'user_name': user_name
                }
            )

            print("SCREEN SHARE STARTED BY:",user_name)

          
            await self.broadcast_change_log(f"{user_name} started screen sharing.")

        elif event_type == 'screen-share-stop':
          
            user_id = text_data_json['user_id']
            user_name = await self.get_user_name(user_id)

            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'screen_share_stopped',
                    'user_id': user_id,
                    'user_name': user_name
                }
            )

            
            await self.broadcast_change_log(f"{user_name} stopped screen sharing.")



    @database_sync_to_async
    def get_user_name(self, user_id):
        user = User.objects.get(id=user_id)
        return user.username

    @database_sync_to_async
    def save_notes(self, user_id, content):
        user = User.objects.get(id=user_id)
        meeting_room = MeetingRoom.objects.get(room_name=self.room_name)
        meeting = meeting_room.meeting
        organization = meeting_room.organization

        meeting_notes, created = MeetingNotes.objects.get_or_create(
            meeting=meeting,
            organization=organization,
            defaults={'content': content}
        )

        if not created:
            meeting_notes.content = content
            meeting_notes.save()

    @database_sync_to_async
    def get_participants_in_room(self):
        meeting_room = MeetingRoom.objects.get(room_name=self.room_name)
        participants = meeting_room.participants.all()
        return [user.username for user in participants]

    @database_sync_to_async
    def insert_emoji(self, user_id, emoji):
        user = User.objects.get(id=user_id)
        meeting_room = MeetingRoom.objects.get(room_name=self.room_name)
        meeting = meeting_room.meeting
        organization = meeting_room.organization

        meeting_notes, created = MeetingNotes.objects.get_or_create(
            meeting=meeting,
            organization=organization
        )

        if meeting_notes.content:
            meeting_notes.content += f" {emoji}"
        else:
            meeting_notes.content = emoji
        meeting_notes.save()

    async def broadcast_change_log(self, message):
        """
        Broadcast a change log entry to all participants in the room.
        """
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'change_log',
                'message': message
            }
        )

    # Event handlers
    async def note_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'note_update',
            'content': event['content'],
            'user_name': event.get('user_name', 'undefined')  
        }))

    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing_event',
            'user_name': event['user_name'],
            'is_typing': event['is_typing']
        }))

    async def emoji_inserted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'emoji_inserted',
            'emoji': event['emoji'],
            'user_name': event['user_name']
        }))

    async def change_log(self, event):
        """
        Handle change log events.
        """
        await self.send(text_data=json.dumps({
            'type': 'change_log',
            'message': event['message']
        }))


#    Mentioned event handler
    async def mention_event(self, event):
        """
        Handle mention events.
        """
        await self.send(text_data=json.dumps({
            'type': 'mention_event',
            'user_name': event['user_name'],
            'mentioned_user': event['mentioned_user']
        }))

    # screen share event handlers
   # Event handlers
    async def screen_share_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'screen_share_started',
            'user_id': event['user_id'],
            'user_name': event['user_name']
        }))

    async def screen_share_stopped(self, event):
        await self.send(text_data=json.dumps({
            'type': 'screen_share_stopped',
            'user_id': event['user_id'],
            'user_name': event['user_name']
        }))