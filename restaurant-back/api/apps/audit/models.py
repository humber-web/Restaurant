"""
Audit and Operation Logging Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


class OperationLog(models.Model):
    """
    Audit log for tracking all CREATE/UPDATE/DELETE operations.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(max_length=200)
    change_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} performed {self.action} on {self.object_repr}"

    class Meta:
        db_table = 'apps_operationlog'  # Use existing table
        verbose_name = 'Operation Log'
        verbose_name_plural = 'Operation Logs'
        ordering = ['-timestamp']
