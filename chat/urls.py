from django.urls import path
from .views import (
    ChatRoomListView,
    contacts_view,
    create_group_chat,
    login_view,
    me_view,
    register_view,
    start_private_chat,
    message_list_get,
    create_msg
)

urlpatterns = [
    path('auth/register/', register_view),
    path('auth/login/', login_view),
    path('auth/me/', me_view),
    path('contacts/', contacts_view),
    path('chats/', ChatRoomListView.as_view()),
    path('chats/private/start/', start_private_chat),
    path('chats/group/create/', create_group_chat),
    #path('chats/<int:room_id>/messages/', MessageListCreateView.as_view()),
    path('chats/<int:room_id>/messages/', message_list_get, name='get msg'),
    path('chats/msg/<int:id>/', create_msg, name = 'create msg'),
]
