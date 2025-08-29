from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# Create your views here.
User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            response = Response({
                "user": {
                    "id": user.id,
                    "name": user.username,
                    "email": user.email,
                },
                "message": "Login successful"
            }, status=status.HTTP_200_OK)
            
            # Return tokens in response for localStorage
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            response.data.update({
                "access_token": access_token,
                "refresh_token": refresh_token
            })
            return response
        else:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token not found'}, status=401)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            return Response({
                'access_token': access_token,
                'message': 'Token refreshed'
            }, status=200)
        except Exception:
            return Response({'error': 'Invalid refresh token'}, status=401)
