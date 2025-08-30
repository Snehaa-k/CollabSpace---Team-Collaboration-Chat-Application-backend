from rest_framework import serializers
from .models import Room, RoomInvitation,RoomMember
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class RoomMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = RoomMember
        fields = ["id", "email", "joined_at"]


class RoomSerializer(serializers.ModelSerializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False
    )
    members = RoomMemberSerializer(source="roommember_set", many=True, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "created_by",
            "emails",      
            "members"      
        ]

    def create(self, validated_data):
        emails = validated_data.pop("emails", [])
        request = self.context.get("request")

        room = Room.objects.create(
            created_by=request.user,
            **validated_data
        )

        # Add creator as a member
        RoomMember.objects.create(room=room, user=request.user)

        # Handle invitations
        for email in emails:
            try:
                user = User.objects.get(email=email)
                RoomMember.objects.get_or_create(room=room, user=user)
            except User.DoesNotExist:
                # Send invitation if user doesn't exist
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