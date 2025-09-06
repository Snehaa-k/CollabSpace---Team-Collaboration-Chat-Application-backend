from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer
from rooms.models import Room, RoomMember

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def room_messages(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
        # Check if user is member
        if not RoomMember.objects.filter(room=room, user=request.user).exists():
            return Response({'error': 'Not a member of this room'}, status=status.HTTP_403_FORBIDDEN)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        messages = Message.objects.filter(room=room).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        message_text = request.data.get('message')
        if not message_text:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        message = Message.objects.create(
            room=room,
            user=request.user,
            message=message_text
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
