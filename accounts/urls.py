from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from .views import RegisterView,LoginView

router = DefaultRouter()
router.register("register", RegisterView, basename="register")

urlpatterns = [
    # JWT Auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('login/', LoginView.as_view(), name='login'),

    path("", include(router.urls)),
]



