from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, InvitationDetailView, AcceptInvitationView, RejectInvitationView

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),
    path('invitations/<uuid:token>/', InvitationDetailView.as_view(), name='invitation-detail'),
    path('invitations/<uuid:token>/accept/', AcceptInvitationView.as_view(), name='accept-invitation'),
    path('invitations/<uuid:token>/reject/', RejectInvitationView.as_view(), name='reject-invitation'),
]