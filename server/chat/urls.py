from django.urls import path
from .views import ChatListCreateView, ChatRetrieveDestroyView, ChatMessagesView

urlpatterns = [
    path('chats/', ChatListCreateView.as_view(), name='chat-list-create'),
    path('chats/<str:thread_id>/', ChatRetrieveDestroyView.as_view(), name='chat-retrieve-destroy'),
    path('chats/<str:thread_id>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
]