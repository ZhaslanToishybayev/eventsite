import uuid
from django.db import models
from django.conf import settings

class AgentLog(models.Model):
    """
    Logs actions taken by agents for auditing and debugging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=100, verbose_name="Agent Name")
    action = models.CharField(max_length=255, verbose_name="Action Taken")
    details = models.TextField(verbose_name="Details", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agent_name} - {self.action} at {self.created_at}"

class AgentTask(models.Model):
    """
    Represents a task assigned to an agent, potentially for background processing.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=100, verbose_name="Target Agent")
    task_type = models.CharField(max_length=100, verbose_name="Task Type")
    payload = models.JSONField(default=dict, verbose_name="Task Data")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    result = models.TextField(blank=True, null=True, verbose_name="Task Result")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent_name} - {self.task_type} ({self.status})"
