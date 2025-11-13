from rest_framework import serializers
from .models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    model_name = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = OperationLog
        fields = [
            'id',
            'user',
            'username',
            'user_email',
            'action',
            'content_type',
            'model_name',
            'object_id',
            'object_repr',
            'change_message',
            'timestamp'
        ]
        read_only_fields = fields
