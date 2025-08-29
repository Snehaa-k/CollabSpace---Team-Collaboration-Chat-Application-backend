from rest_framework import serializers
from .models import Room, RoomInvitation
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class RoomSerializer(serializers.ModelSerializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'created_at', 'emails']

    def create(self, validated_data):
        emails = validated_data.pop("emails", [])
        request = self.context.get("request")

        room = Room.objects.create(
            created_by=request.user,
            **validated_data
        )

        # Send invitation emails
        for email in emails:
            invite_link = f"http://localhost:5173/signup?email={email}&room_id={room.id}"
            send_mail(
                subject=f"Invitation to join room {room.name}",
                message=f"You are invited to join {room.name}. Click here: {invite_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True,
            )

        return room

class InvitationSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    inviter_name = serializers.CharField(source='invited_by.username', read_only=True)
    
    class Meta:
        model = RoomInvitation
        fields = ['id', 'room_name', 'inviter_name', 'email', 'status', 'created_at']