from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OperationLog
from .serializers import OperationLogSerializer


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for audit logs.
    Lists all operation logs with filtering capabilities.
    """
    queryset = OperationLog.objects.all().select_related('user', 'content_type')
    serializer_class = OperationLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action', 'user', 'content_type']
    search_fields = ['object_repr', 'change_message']
    ordering_fields = ['timestamp', 'action', 'user']
    ordering = ['-timestamp']
