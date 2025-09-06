from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet,AcceptInvitationView, RejectInvitationView

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),
    path('rooms/<int:room_id>/accept/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('rooms/<int:room_id>/reject/', RejectInvitationView.as_view(), name='reject-invitation'),
]