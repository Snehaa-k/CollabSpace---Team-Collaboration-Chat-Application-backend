from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
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
            models.Q(roommember__user=user) | 
            models.Q(roominvitation__email=user.email, roominvitation__status='pending')
        ).distinct()
    
    def update(self, request, *args, **kwargs):
        room = self.get_object()
        # Only room owner can update
        if room.created_by != request.user:
            return Response({'error': 'Only room owner can update'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        room = self.get_object()
        if room.created_by != request.user:
            return Response({'error': 'Only room owner can invite members'}, status=status.HTTP_403_FORBIDDEN)
        
        emails = request.data.get('emails', [])
        invited_count = 0
        
        for email in emails:
            if email.strip():
                invitation, created = RoomInvitation.objects.get_or_create(
                    room=room,
                    email=email.strip(),
                    defaults={'invited_by': request.user, 'status': 'pending'}
                )
                if created:
                    invited_count += 1
        
        return Response({
            'message': f'{invited_count} invitations sent',
            'room_id': room.id
        })



class AcceptInvitationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
            invitation = RoomInvitation.objects.get(email=request.user.email, room=room)
            
            # Delete the invitation object
            invitation.delete()
            
            return Response({'message': 'Invitation accepted and deleted', 'room_id': room.id})
        except RoomInvitation.DoesNotExist:
            return Response({'error': 'Invalid invitation'}, status=404)

class RejectInvitationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
            invitation = RoomInvitation.objects.get(email=request.user.email, room=room)
            invitation.status = 'rejected'
            invitation.save()
            return Response({'message': 'Invitation rejected'})
        except RoomInvitation.DoesNotExist:
            return Response({'error': 'Invalid invitation'}, status=404)