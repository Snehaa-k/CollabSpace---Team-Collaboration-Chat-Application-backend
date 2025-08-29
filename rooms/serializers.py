from rest_framework import serializers
from .models import Room,RoomMember,RoomInvitation

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'is_private']
        read_only_fields = ['id', 'created_by', 'created_at']

class RommMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room', 'user', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']

class RoomMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = RoomMember
        fields = ['id', 'user', 'user_name', 'user_email', 'role', 'joined_at']

class InvitationSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    inviter_name = serializers.CharField(source='invited_by.name', read_only=True)
    
    class Meta:
        model = RoomInvitation
        fields = ['email', 'room_name', 'inviter_name', 'status', 'created_at']

class InviteEmailsSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField())

class AcceptInvitationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    password = serializers.CharField(write_only=True, required=False)