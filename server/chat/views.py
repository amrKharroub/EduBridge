import json
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from langchain_core.messages import HumanMessage, AIMessage
from .models import Chat
from .serializers import ChatSerializer, MessageSerializer, SendMessageSerializer
from .agent import create_graph, get_checkpointer, DB_URI
import psycopg

User = get_user_model()

class ChatListCreateView(generics.ListCreateAPIView):
    """
    GET: list all chats for the authenticated user.
    POST: create a new chat (generates a thread_id).
    """
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        import uuid
        thread_id = str(uuid.uuid4())
        serializer.save(user=self.request.user, thread_id=thread_id)

class ChatRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    GET: retrieve chat metadata.
    DELETE: delete the chat and its associated checkpoints.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        thread_id = instance.thread_id
        conn = psycopg.connect(DB_URI, autocommit=True)
        with conn.cursor() as cur:
            cur.execute("DELETE FROM checkpoints WHERE thread_id = %s", (thread_id,))
        conn.close()
        instance.delete()

class ChatMessagesView(APIView):
    """
    GET: retrieve all messages for a given chat thread.
    POST: send a new message to the agent and get response.
    """
    permission_classes = [IsAuthenticated]

    def get_chat(self, user, thread_id):
        return get_object_or_404(Chat, user=user, thread_id=thread_id)

    def get(self, request, thread_id):
        chat = self.get_chat(request.user, thread_id)
        checkpointer = get_checkpointer()
        config = {"configurable": {"thread_id": thread_id}}
        checkpoints = list(checkpointer.list(config))
        if not checkpoints:
            return Response({"messages": []})
        checkpoint_tuple = checkpoints[-1]
        state = checkpoint_tuple[0]  
        messages = []
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            else:
                continue 
            messages.append({
                "role": role,
                "content": msg.content,
                "timestamp": msg.additional_kwargs.get("timestamp")
            })
        return Response(messages)

    def post(self, request, thread_id):
        chat = self.get_chat(request.user, thread_id)
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data['message']

        checkpointer = get_checkpointer()
        graph = create_graph(checkpointer)
        config = {"configurable": {"thread_id": thread_id}}

        input_message = HumanMessage(content=user_message)

        final_state = None
        for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
            final_state = chunk

        if final_state and "messages" in final_state:
            last_message = final_state["messages"][-1]
            if isinstance(last_message, AIMessage):
                response_content = last_message.content
            else:
                response_content = "No response from assistant."
        else:
            response_content = "No response."

        chat.save(update_fields=['updated_at'])

        return Response({"response": response_content}, status=status.HTTP_200_OK)



class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        agent_type = self.request.data.get('agent_type', 'rag')
        import uuid
        thread_id = str(uuid.uuid4())
        serializer.save(user=self.request.user, thread_id=thread_id, agent_type=agent_type)