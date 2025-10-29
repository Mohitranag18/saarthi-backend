from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserProfileUpdateSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to get and update user profile
    GET/PUT /api/users/profile/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserProfileUpdateSerializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(UserSerializer(instance).data)


class UserDetailView(generics.RetrieveAPIView):
    """
    API endpoint to get specific user details
    GET /api/users/<id>/
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


class VolunteerToggleActiveView(APIView):
    """
    API endpoint to toggle volunteer active status
    POST /api/users/volunteer/toggle-active/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if user.user_type != 'volunteer':
            return Response(
                {'error': 'Only volunteers can toggle active status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_volunteer_active = not user.is_volunteer_active
        user.save()
        
        return Response({
            'is_volunteer_active': user.is_volunteer_active,
            'message': f"Volunteer status: {'Active' if user.is_volunteer_active else 'Inactive'}"
        })