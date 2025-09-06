from django.urls import path
from . import views

urlpatterns = [
    path('<int:room_id>/messages/', views.room_messages, name='room_messages'),
]