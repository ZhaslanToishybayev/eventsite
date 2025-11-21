from rest_framework import serializers
from ai_consultant.models import ChatSession, ChatMessage, AIContext


class ChatMessageSerializer(serializers.ModelSerializer):
    """Сериализатор для сообщений чата"""

    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'tokens_used', 'created_at']
        read_only_fields = ['id', 'tokens_used', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Сериализатор для сессий чата"""
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'created_at', 'updated_at', 'is_active', 'message_count', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'role': last_message.role,
                'created_at': last_message.created_at
            }
        return None


class ChatRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса к чату"""
    message = serializers.CharField(max_length=2000, required=True)
    session_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Сообщение не может быть пустым")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа от ИИ"""
    success = serializers.BooleanField()
    message = serializers.CharField(max_length=2000, required=False, allow_null=True)
    session_id = serializers.UUIDField()
    message_id = serializers.UUIDField()
    tokens_used = serializers.IntegerField(min_value=0)
    error = serializers.CharField(max_length=500, required=False, allow_null=True)


class AIContextSerializer(serializers.ModelSerializer):
    """Сериализатор для контекста ИИ"""

    class Meta:
        model = AIContext
        fields = ['id', 'key', 'content', 'category', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatAnalyticsSerializer(serializers.Serializer):
    """Сериализатор для аналитики чата"""
    total_sessions = serializers.IntegerField(min_value=0)
    total_messages = serializers.IntegerField(min_value=0)
    total_tokens_used = serializers.IntegerField(min_value=0)
    average_messages_per_session = serializers.FloatField(min_value=0)