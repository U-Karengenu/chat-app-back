from django.contrib.auth.models import User
from rest_framework import serializers
from .models import ChatRoom, Message


class UserSerializer(serializers.ModelSerializer):
    """Controls what user information is sent to React."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    """Used when a new user creates an account."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        # create_user hashes the password safely.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender','message_type','file','status','text', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read', 'created_at', 'status', 'room']


class ChatRoomSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'room_type', 'members', 'last_message', 'unread_count', 'created_at']

    def get_last_message(self, room):
        message = room.messages.last()
        if not message:
            return None
        return MessageSerializer(message).data

    def get_unread_count(self, room):
        request = self.context.get('request')
        if not request:
            return 0
        return room.messages.exclude(sender=request.user).filter(is_read=False).count()
