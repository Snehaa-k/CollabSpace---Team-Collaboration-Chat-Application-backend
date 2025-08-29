from django.db import models
from django.conf import settings
# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)

class RoomMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('member', 'Member')])
    joined_at = models.DateTimeField(auto_now_add=True)

class RoomInvitation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    email = models.EmailField()
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted')])
    created_at = models.DateTimeField(auto_now_add=True)
