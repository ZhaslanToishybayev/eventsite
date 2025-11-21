from django.contrib import admin
from .models import AgentLog, AgentTask

@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = ('agent_name', 'action', 'created_at')
    list_filter = ('agent_name', 'created_at')
    search_fields = ('action', 'details')
    readonly_fields = ('created_at',)

@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ('agent_name', 'task_type', 'status', 'created_at')
    list_filter = ('status', 'agent_name')
    search_fields = ('task_type', 'result')
