"""
Inventory Management Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.http import Http404

from apps.common.permissions import IsManager, RequireModule
from apps.common.feature_flags import Modules
from apps.audit.models import OperationLog
from .models import InventoryItem
from .serializers import InventoryItemSerializer


class CreateInventoryItemView(APIView):
    """
    Create a new inventory item.
    POST /api/inventory_item/register/
    Requires: inventory module (Premium) + authentication + manager permission
    """
    required_module = Modules.INVENTORY
    permission_classes = [IsAuthenticated, IsManager, RequireModule]

    def post(self, request):
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            # Update request body for operation logging
            if hasattr(request, 'body_data'):
                request.body_data['object_id'] = item.itemID
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryItemListView(APIView):
    """
    List all inventory items.
    GET /api/inventory_item/
    """
    required_module = Modules.INVENTORY
    permission_classes = [IsAuthenticated, RequireModule]

    def get(self, request):
        items = InventoryItem.objects.all().order_by('itemID')
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)


class InventoryItemDetailView(APIView):
    required_module = Modules.INVENTORY
    """
    Get inventory item details or search.
    GET /api/inventory_item/<pk>/ - Get by ID
    GET /api/inventory_item/search/?supplier=...&menu_item=...&menu_item_name=... - Search
    """
    permission_classes = [IsAuthenticated, RequireModule]

    def get(self, request, pk=None):
        # If a primary key is provided, fetch by ID
        if pk:
            try:
                item = InventoryItem.objects.get(pk=pk)
                serializer = InventoryItemSerializer(item)
                return Response(serializer.data)
            except InventoryItem.DoesNotExist:
                raise Http404
        
        # Otherwise, search by query parameters
        supplier = request.query_params.get('supplier')
        menu_item = request.query_params.get('menu_item')
        menu_item_name = request.query_params.get('menu_item_name')
        
        queryset = InventoryItem.objects.all()
        
        if supplier:
            queryset = queryset.filter(supplier__icontains=supplier)
        if menu_item:
            queryset = queryset.filter(menu_item__itemID=menu_item)
        if menu_item_name:
            queryset = queryset.filter(menu_item__name__icontains=menu_item_name)
        
        if not queryset.exists():
            raise Http404
        
        serializer = InventoryItemSerializer(queryset, many=True)
        return Response(serializer.data)


class InventoryItemUpdateView(APIView):
    required_module = Modules.INVENTORY
    """
    Update an inventory item.
    PUT /api/inventory_item/<pk>/update/
    """
    permission_classes = [IsAuthenticated, IsManager, RequireModule]

    def put(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk)
        serializer = InventoryItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryItemDeleteView(APIView):
    required_module = Modules.INVENTORY
    """
    Delete an inventory item.
    DELETE /api/inventory_item/<pk>/delete/
    """
    permission_classes = [IsAuthenticated, IsManager, RequireModule]

    def delete(self, request, pk):
        item = get_object_or_404(InventoryItem, pk=pk)
        content_type = ContentType.objects.get_for_model(item)
        
        # Log delete operation
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=item.itemID,
            object_repr=f"inventoryitem {item.itemID}",
            change_message=f"User {request.user} performed DELETE on inventoryitem {item.itemID}"
        )
        
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
