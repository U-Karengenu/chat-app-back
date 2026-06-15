from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    """A room can be a private chat or a group chat."""

    ROOM_TYPES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    name = models.CharField(max_length=100, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='private')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        return f'{self.room_type} chat #{self.id}'


class Message(models.Model):
    """A single message sent inside a chat room."""
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    )

    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
    )
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length = 30, choices = MESSAGE_TYPES, default = 'text')
    text = models.TextField(blank = True, null = True)
    file = models.FileField(upload_to = "chatFiles/",blank = True, null = True)
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.text[:30]}'
