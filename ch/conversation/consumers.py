import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from conversation.models import Conversation, Message


User = get_user_model()
logger = logging.getLogger("channels")



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = self.room_name

       


        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Broadcast that the user went offline
       

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender_id = self.user.id
        message_text = data.get("message", "").strip()
        file_url = data.get("file_url", None)
        code_snippet = data.get("code_snippet", None)

        print(f"📩 Received Data: {data}")  


        user1_id, user2_id = map(int, self.room_name.split("_")[1:])
        receiver_id = user2_id if sender_id == user1_id else user1_id

        conversation = await self.get_or_create_conversation(user1_id, user2_id)

        if message_text:
            message = await self.save_message(conversation, sender_id, message_text, None, None)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message.text,
                    "sender_id": sender_id,
                    "timestamp": message.timestamp.strftime("%H:%M"),
                }
            )

        if file_url:
            message = await self.save_message(conversation, sender_id, None, file_url, None)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_file",
                    "file_url": file_url,
                    "sender_id": sender_id,
                    "timestamp": message.timestamp.strftime("%H:%M"),
                }
            )

        if code_snippet:
            message = await self.save_message(conversation, sender_id, None, None, code_snippet)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_code",
                    "code_snippet": code_snippet,
                    "sender_id": sender_id,
                    "timestamp": message.timestamp.strftime("%H:%M"),
                }
            )

        # **Send read receipt**
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_read",
                    "message_id": message.id,
                    "receiver_id": message.receiver.id if message.receiver else None,
                },
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "timestamp": event["timestamp"],
        }))

    async def chat_file(self, event):
        await self.send(text_data=json.dumps({
            "file_url": event["file_url"],
            "sender_id": event["sender_id"],
            "timestamp": event["timestamp"],
        }))

    async def chat_code(self, event):
     print("📌 chat_code event triggered:", event)  # Debugging line
     await self.send(text_data=json.dumps({
        "code_snippet": event["code_snippet"],
        "sender_id": event["sender_id"],
        "timestamp": event["timestamp"],
    }))
     
    #  send read reciepts
    async def message_read(self, event):
        """Handle read receipts"""
        message_id = event["message_id"]
        receiver_id = event.get("receiver_id")

        if receiver_id and receiver_id == self.user.id:
            await self.mark_message_as_read(message_id)
            await self.send(text_data=json.dumps({"type": "message_read", "message_id": message_id}))

    # BROADCAST THE USER STATUS
    async def broadcast_user_status(self, user_id, status):
        """Broadcast user status to all users in the chat room"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "user_id": user_id,
                "status": status,
            },
        )      

    async def user_status(self, event):
        """Send user status update to frontend"""
        await self.send(text_data=json.dumps(event))  

    
 



    @database_sync_to_async
    def get_or_create_conversation(self, user1_id, user2_id):
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)
        conversation, created = Conversation.objects.get_or_create(
            user1=min(user1, user2, key=lambda x: x.id),
            user2=max(user1, user2, key=lambda x: x.id)
        )
        return conversation

    @database_sync_to_async
    def save_message(self, conversation, sender_id, text, file_url, code_snippet):
        sender = User.objects.get(id=sender_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            text=text or "",
            file=file_url or None,
            is_read=True,
            code_snippet=code_snippet or None,
        )
        return message
