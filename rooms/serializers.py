from rest_framework import serializers
from .models import Room, RoomInvitation,RoomMember
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class RoomMemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    id = serializers.IntegerField(source="user.id", read_only=True)
    invite_email = serializers.SerializerMethodField()

    class Meta:
        model = RoomMember
        fields = ["id", "email", "joined_at", "invite_email"]

    def get_invite_email(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_email = request.user.email
            invitation = RoomInvitation.objects.filter(room=obj.room, email=user_email).first()
            return invitation.email if invitation else None
        return None


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

        RoomMember.objects.create(room=room, user=request.user)
        # Handle invitations
        for email in emails:
            try:
                user = User.objects.get(email=email)
                # If user exists, add them directly
                RoomMember.objects.get_or_create(room=room, user=user)
            except User.DoesNotExist:
                RoomInvitation.objects.create(
                    room=room,
                    email=email,
                    invited_by=request.user
                )
                signup_link = f"{settings.FRONTEND_URL}"
                send_mail(
                    subject=f"Invitation to join room {room.name}",
                    message=f"You are invited to join {room.name}. "
                            f"Please register here: {signup_link}",
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