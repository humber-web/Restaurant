"""
User Management Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.permissions import IsManager
from apps.audit.models import OperationLog
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer, GroupSerializer


class CreateUserView(APIView):
    """
    Create a new staff user (manager only).
    POST /api/register/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            group_name = request.data.get('group', 'customers')
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            
            # Create profile
            profile_data = {'user': user.id}
            profile_serializer = ProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
            
            refresh = RefreshToken.for_user(user)
            
            # Update request body to include the new object's ID for operation log
            if hasattr(request, 'body_data'):
                request.body_data['object_id'] = user.id
            
            return Response({
                'id': user.id,
                'user': serializer.data,
                'profile': profile_serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateCustomerView(APIView):
    """
    Public customer registration.
    POST /api/register/customer/
    """
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            group, created = Group.objects.get_or_create(name='customers')
            user.groups.add(group)
            
            # Create profile
            Profile.objects.create(user=user)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    User login with JWT tokens.
    POST /api/login/
    """
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(
            {"detail": "Invalid credentials"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserListView(APIView):
    """
    List all users.
    GET /api/user/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, format=None):
        users = User.objects.all().order_by('id')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """
    Get user details.
    GET /api/user/<pk>/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserUpdateView(APIView):
    """
    Update user.
    PUT /api/user/<pk>/update/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk, format=None):
        # Set metadata for operation logging
        if hasattr(request, 'body_data'):
            request.body_data['model'] = 'user'
            request.body_data['operation'] = 'UPDATE'
        
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'id': user.id,
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    """
    Delete user.
    DELETE /api/user/<pk>/delete/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        content_type = ContentType.objects.get(model='user')
        
        # Log the delete operation before deleting the user
        OperationLog.objects.create(
            user=request.user,
            action="DELETE",
            content_type=content_type,
            object_id=user.id,
            object_repr=f"user {user.id}",
            change_message=f"User {request.user} performed DELETE on user {user.id}"
        )
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    """
    List all profiles.
    GET /api/profile/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, format=None):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)


class GroupListView(APIView):
    """
    List all groups.
    GET /api/groups/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, format=None):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)
