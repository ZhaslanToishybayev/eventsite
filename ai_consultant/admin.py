from django.contrib import admin
from .models import ChatSession, ChatMessage, AIContext, ChatAnalytics


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'is_active', 'message_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__phone', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'message_count')
    ordering = ('-updated_at',)

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Кол-во сообщений'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'tokens_used', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session__user__phone')
    readonly_fields = ('id', 'created_at', 'tokens_used')
    ordering = ('-created_at',)

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Предпросмотр'


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('id', 'created_at', 'tokens_used')
    fields = ('role', 'content', 'tokens_used', 'created_at')


class ChatAnalyticsInline(admin.TabularInline):
    model = ChatAnalytics
    extra = 0
    readonly_fields = ('id', 'created_at')


@admin.register(AIContext)
class AIContextAdmin(admin.ModelAdmin):
    list_display = ('key', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('key', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('category', 'key')


@admin.register(ChatAnalytics)
class ChatAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('session', 'event_type', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('session__user__phone', 'event_type')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)


# Добавляем inline в ChatSessionAdmin
ChatSessionAdmin.inlines = [ChatMessageInline, ChatAnalyticsInline]