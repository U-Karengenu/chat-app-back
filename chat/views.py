from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer, RegisterSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """Create a new user account and return a token."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Check username/password and return a token if correct."""
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if not user:
        return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })


@api_view(['GET'])
def me_view(request):
    """Return the currently logged-in user."""
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
def contacts_view(request):
    """Return all users except the logged-in user."""
    users = User.objects.exclude(id=request.user.id)
    return Response(UserSerializer(users, many=True).data)

#-------------------------chat room serializer-----------------------

class ChatRoomListView(generics.ListAPIView):
    """List all rooms where the current user is a member."""
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        return ChatRoom.objects.filter(members=self.request.user).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}


@api_view(['POST'])
def start_private_chat(request):
    """Start or return an existing private chat with another user."""
    friend_id = request.data.get('friend_id')

    try:
        friend = User.objects.get(id=friend_id)
    except User.DoesNotExist:
        return Response({'detail': 'Friend not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Search for a private room that already contains both users.
    rooms = ChatRoom.objects.filter(room_type='private', members=request.user).filter(members=friend)
    if rooms.exists():
        room = rooms.first()
    else:
        room = ChatRoom.objects.create(room_type='private')
        room.members.add(request.user, friend)

    return Response(ChatRoomSerializer(room, context={'request': request}).data)


@api_view(['POST'])
def create_group_chat(request):
    """Create a simple group chat with selected members."""
    name = request.data.get('name')
    member_ids = request.data.get('member_ids', [])

    room = ChatRoom.objects.create(name=name, room_type='group')
    room.members.add(request.user)

    users = User.objects.filter(id__in=member_ids)
    for user in users:
        room.members.add(user)

    return Response(ChatRoomSerializer(room, context={'request': request}).data, status=status.HTTP_201_CREATED)

#------------------messages------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_list_get(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, members=request.user)

    if request.method == "GET":
        msgs = Message.objects.filter(room_id = room_id, room__members=request.user)
        msgs.exclude(sender=request.user).update(is_read=True)
    
        serializer = MessageSerializer(msgs, many=True)
       

        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_msg(request, id):

    room = get_object_or_404(ChatRoom, id=id)
    if not room:
        return Response(
            {'error': 'room not found'},
            status = status.HTTP_404_NOT_FOUND
        )

    serializer = MessageSerializer(data = request.data)

    if serializer.is_valid():
        serializer.save(sender = request.user, room=room)
        return Response({'msg': 'msg created'})
    
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)