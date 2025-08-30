from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .models import Room, RoomInvitation, RoomMember
from .serializers import RoomSerializer, InvitationSerializer
from django.db import models

User = get_user_model()

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Rooms where the user is the creator or a member
        return Room.objects.filter(
            models.Q(created_by=user) | 
            models.Q(roommember__user=user)
        ).distinct()

class InvitationDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, token):
        try:
            invitation = RoomInvitation.objects.get(token=token, status='pending')
            serializer = InvitationSerializer(invitation)
            return Response(serializer.data)
        except RoomInvitation.DoesNotExist:
            return Response({'error': 'Invalid invitation'}, status=404)

class AcceptInvitationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, token):
        try:
            invitation = RoomInvitation.objects.get(token=token, status='pending')
            
            if invitation.email != request.user.email:
                return Response({'error': 'Email mismatch'}, status=400)
            
            RoomMember.objects.get_or_create(room=invitation.room, user=request.user)
            invitation.status = 'accepted'
            invitation.save()
            
            return Response({'message': 'Invitation accepted', 'room_id': invitation.room.id})
        except RoomInvitation.DoesNotExist:
            return Response({'error': 'Invalid invitation'}, status=404)

class RejectInvitationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, token):
        try:
            invitation = RoomInvitation.objects.get(token=token, status='pending')
            invitation.status = 'rejected'
            invitation.save()
            return Response({'message': 'Invitation rejected'})
        except RoomInvitation.DoesNotExist:
            return Response({'error': 'Invalid invitation'}, status=404)