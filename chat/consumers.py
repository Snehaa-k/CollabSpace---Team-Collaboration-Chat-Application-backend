import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message
from rooms.models import Room, RoomMember

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Get user from token
        self.user = await self.get_user_from_token()
        if not self.user:
            await self.close()
            return
            
        # Check if user is member of room
        if not await self.is_room_member():
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Send user list to all clients
        await self.send_user_list()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Send updated user list
        await self.send_user_list()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Save message to database
        message_obj = await self.save_message(message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message_obj.id,
                    'user': self.user.email,
                    'message': message,
                    'timestamp': message_obj.timestamp.isoformat()
                }
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def user_list(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': event['users']
        }))

    @database_sync_to_async
    def get_user_from_token(self):
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        from django.contrib.auth.models import AnonymousUser
        
        try:
            token = self.scope['query_string'].decode().split('token=')[1]
            UntypedToken(token)
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            return user
        except (InvalidToken, TokenError, IndexError):
            return AnonymousUser()

    @database_sync_to_async
    def is_room_member(self):
        try:
            room = Room.objects.get(id=self.room_id)
            return RoomMember.objects.filter(room=room, user=self.user).exists()
        except Room.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message):
        room = Room.objects.get(id=self.room_id)
        return Message.objects.create(
            room=room,
            user=self.user,
            message=message
        )

    async def send_user_list(self):
        users = await self.get_online_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_list',
                'users': users
            }
        )

    @database_sync_to_async
    def get_online_users(self):
        # This is simplified - in production, track active connections
        room = Room.objects.get(id=self.room_id)
        members = RoomMember.objects.filter(room=room).select_related('user')
        return [member.user.email for member in members]