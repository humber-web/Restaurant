"""
Table Management Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from apps.common.permissions import IsManager
from apps.audit.models import OperationLog
from .models import Table
from .serializers import TableSerializer


class CreateTableView(APIView):
    """
    Create a new table.
    POST /api/table/register/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            table = serializer.save()
            # Update request body for operation logging
            if hasattr(request, 'body_data'):
                request.body_data['object_id'] = table.tableid
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableListView(APIView):
    """
    List all tables.
    GET /api/table/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tables = Table.objects.all().order_by('tableid')
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)


class TableDetailView(APIView):
    """
    Get table details or search by status/capacity.
    GET /api/table/<pk>/ - Get by ID
    GET /api/table/search/?status=...&capacity=... - Search
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        # If a primary key is provided, fetch by ID
        if pk:
            try:
                table = Table.objects.get(pk=pk)
                serializer = TableSerializer(table)
                return Response(serializer.data)
            except Table.DoesNotExist:
                raise Http404
        
        # Otherwise, search by query parameters
        table_status = request.query_params.get('status')
        capacity = request.query_params.get('capacity')
        
        queryset = Table.objects.all()
        
        if table_status:
            queryset = queryset.filter(status__icontains=table_status)
        if capacity:
            queryset = queryset.filter(capacity=capacity)
        
        if not queryset.exists():
            raise Http404
        
        serializer = TableSerializer(queryset, many=True)
        return Response(serializer.data)


class TableUpdateView(APIView):
    """
    Update a table.
    PUT /api/table/<pk>/update/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk):
        table = get_object_or_404(Table, pk=pk)
        serializer = TableSerializer(table, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableDeleteView(APIView):
    """
    Delete a table.
    DELETE /api/table/<pk>/delete/
    """
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk):
        table = get_object_or_404(Table, pk=pk)
        content_type = ContentType.objects.get_for_model(table)
        
        # Log delete operation
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=table.tableid,
            object_repr=f"table {table.tableid}",
            change_message=f"User {request.user} performed DELETE on table {table.tableid}"
        )
        
        table.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
