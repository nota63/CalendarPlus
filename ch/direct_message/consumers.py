import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import Conversation, Message
from accounts.models import Organization, Profile

# Logger for debugging
logger = logging.getLogger(__name__)

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Establish WebSocket connection """
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.user = self.scope["user"]

        logger.info(f"User {self.user} is trying to connect to conversation {self.conversation_id}")

        self.conversation = await self.get_conversation()
        
        if self.conversation:
            if self.user not in [self.conversation.user_1, self.conversation.user_2]:
                logger.warning(f"Unauthorized user {self.user} tried to access conversation {self.conversation_id}")
                await self.close()
                return

            self.room_group_name = f'conversation_{self.conversation_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"User {self.user} connected successfully to {self.room_group_name}")

        else:
            logger.error(f"Conversation {self.conversation_id} not found")
            await self.close()

    async def disconnect(self, close_code):
        """ Handle WebSocket disconnection """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"User {self.user} disconnected from {self.room_group_name}")

    async def receive(self, text_data):
        """ Receive message from WebSocket """
        try:
            data = json.loads(text_data)
            message_content = data.get('message', '').strip()

            if not message_content:
                logger.warning("Received an empty message. Ignoring.")
                return

            sender = self.user
            receiver = await self.get_receiver(sender)
            
            if not receiver:
                logger.error(f"Could not determine receiver for conversation {self.conversation_id}")
                return

            logger.info(f"Saving message: '{message_content}' from {sender} to {receiver}")
            new_message = await self.save_message(sender, receiver, message_content)

            # Send message to WebSocket group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': new_message.content,
                    'sender': sender.username
                }
            )

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error in receive method: {e}")

    async def chat_message(self, event):
        """ Send the received message to WebSocket """
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

    @sync_to_async
    def get_conversation(self):
        """ Fetch conversation from the database """
        try:
            return Conversation.objects.get(id=self.conversation_id)
        except Conversation.DoesNotExist:
            return None

    @sync_to_async
    def get_receiver(self, sender):
        """ Get the receiver of the message """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.user_2 if sender == conversation.user_1 else conversation.user_1
        except Conversation.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, sender, receiver, message_content):
        """ Save the message to the database """
        conversation = Conversation.objects.get(id=self.conversation_id)
        new_message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            conversation=conversation,
            content=message_content,
            organization=conversation.organization,
        )
        return new_message
