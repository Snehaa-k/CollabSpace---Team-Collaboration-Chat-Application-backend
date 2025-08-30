"""
URL configuration for collabspace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_room_endpoint(request):
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    if request.method == 'POST':
        try:
            from rooms.models import Room, RoomInvitation
            from rooms.serializers import RoomSerializer
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            data = json.loads(request.body)
            
            # Create room
            room_data = {'name': data.get('name'), 'description': data.get('description')}
            serializer = RoomSerializer(data=room_data)
            
            if serializer.is_valid():
                room = serializer.save(created_by=request.user if request.user.is_authenticated else None)
                
                # Handle email invitations - only store invitations, don't create users
                emails = data.get('emails', [])
                for email in emails:
                    RoomInvitation.objects.create(
                        room=room,
                        email=email,
                        invited_by=request.user if request.user.is_authenticated else None
                    )
                
                return JsonResponse(RoomSerializer(room).data)
            else:
                return JsonResponse({"errors": serializer.errors}, status=400)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('rooms.urls')),
    path('api/rooms/create/', create_room_endpoint, name='create-room'),
]
