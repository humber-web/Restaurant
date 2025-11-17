"""
API Views for Purchase Orders and Supplier Invoices
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal

from .models import PurchaseOrder, PurchaseOrderItem, SupplierInvoice
from apps.suppliers.models import Supplier
from apps.inventory.models import InventoryItem
from .serializers import (
    PurchaseOrderListSerializer,
    PurchaseOrderDetailSerializer,
    PurchaseOrderItemSerializer,
    CreatePurchaseOrderSerializer,
    ReceiveGoodsSerializer,
    SupplierInvoiceSerializer,
    MarkInvoiceAsPaidSerializer
)
from apps.common.permissions import IsManager


class PurchaseOrderListView(APIView):
    """List all purchase orders or create a new one."""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """
        List purchase orders with optional filtering.

        Query params:
        - status: Filter by status
        - supplier: Filter by supplier ID
        - from_date, to_date: Filter by order date range
        """
        purchase_orders = PurchaseOrder.objects.all()

        # Filters
        status_filter = request.query_params.get('status')
        if status_filter:
            purchase_orders = purchase_orders.filter(status=status_filter)

        supplier_filter = request.query_params.get('supplier')
        if supplier_filter:
            purchase_orders = purchase_orders.filter(supplier_id=supplier_filter)

        from_date = request.query_params.get('from_date')
        if from_date:
            purchase_orders = purchase_orders.filter(order_date__gte=from_date)

        to_date = request.query_params.get('to_date')
        if to_date:
            purchase_orders = purchase_orders.filter(order_date__lte=to_date)

        serializer = PurchaseOrderListSerializer(purchase_orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new purchase order with items.

        Request body:
        {
            "supplier": 1,
            "order_date": "2025-01-15",
            "expected_delivery_date": "2025-01-20",
            "notes": "Urgent order",
            "items": [
                {
                    "inventory_item": 5,
                    "quantity_ordered": 100,
                    "unit_price": 5.50
                }
            ]
        }
        """
        serializer = CreatePurchaseOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Get supplier
        supplier = get_object_or_404(Supplier, supplierID=data['supplier'])

        # Generate PO number
        year = timezone.now().year
        last_po = PurchaseOrder.objects.filter(
            po_number__startswith=f'OC/{year}/'
        ).order_by('-po_number').first()

        if last_po:
            last_num = int(last_po.po_number.split('/')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        po_number = f"OC/{year}/{new_num:05d}"

        # Create purchase order
        purchase_order = PurchaseOrder.objects.create(
            po_number=po_number,
            supplier=supplier,
            order_date=data['order_date'],
            expected_delivery_date=data.get('expected_delivery_date'),
            notes=data.get('notes', ''),
            created_by=request.user
        )

        # Create line items
        total_amount = Decimal('0.00')
        for item_data in data['items']:
            inventory_item = get_object_or_404(
                InventoryItem,
                itemID=item_data['inventory_item']
            )

            quantity = Decimal(str(item_data['quantity_ordered']))
            price = Decimal(str(item_data['unit_price']))

            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order,
                inventory_item=inventory_item,
                quantity_ordered=quantity,
                unit_price=price
            )

            total_amount += quantity * price

        # Update total
        purchase_order.total_amount = total_amount
        purchase_order.save()

        # Return created PO
        response_serializer = PurchaseOrderDetailSerializer(purchase_order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PurchaseOrderDetailView(APIView):
    """Get, update, or delete a specific purchase order."""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        """Get purchase order details."""
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
        serializer = PurchaseOrderDetailSerializer(purchase_order)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Update purchase order (only if not RECEIVED or PAID)."""
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

        # Don't allow editing if goods already received or paid
        if purchase_order.status in ['RECEIVED', 'PAID']:
            return Response({
                'error': 'Cannot edit purchase order that is already received or paid'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Allow updating status, notes, expected delivery date
        allowed_fields = ['status', 'notes', 'expected_delivery_date']
        for field in allowed_fields:
            if field in request.data:
                setattr(purchase_order, field, request.data[field])

        purchase_order.save()

        serializer = PurchaseOrderDetailSerializer(purchase_order)
        return Response(serializer.data)

    def delete(self, request, pk):
        """Cancel a purchase order (soft delete via status)."""
        purchase_order = get_object_or_404(PurchaseOrder, pk=pk)

        if purchase_order.status in ['RECEIVED', 'PAID']:
            return Response({
                'error': 'Cannot cancel purchase order that is already received or paid'
            }, status=status.HTTP_400_BAD_REQUEST)

        purchase_order.status = 'CANCELLED'
        purchase_order.save()

        return Response({
            'detail': 'Purchase order cancelled successfully'
        }, status=status.HTTP_200_OK)


class ReceiveGoodsView(APIView):
    """Mark goods as received against a purchase order item."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """
        Receive goods and update inventory.

        Request body:
        {
            "purchase_order_item_id": 5,
            "quantity_received": 50,
            "received_date": "2025-01-16",
            "notes": "Partial delivery"
        }
        """
        serializer = ReceiveGoodsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        po_item = get_object_or_404(
            PurchaseOrderItem,
            id=data['purchase_order_item_id']
        )

        try:
            # Use the model's receive_goods method
            received_date = data.get('received_date') or timezone.now().date()
            po_item.receive_goods(
                quantity=data['quantity_received'],
                date=received_date
            )

            # Update notes if provided
            if 'notes' in data and data['notes']:
                po_item.notes = data['notes']
                po_item.save()

            return Response({
                'detail': 'Goods received successfully',
                'purchase_order_item': PurchaseOrderItemSerializer(po_item).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class SupplierInvoiceListView(APIView):
    """List all supplier invoices or create a new one."""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """
        List supplier invoices with optional filtering.

        Query params:
        - status: Filter by status
        - supplier: Filter by supplier ID
        - overdue: Show only overdue invoices (true/false)
        """
        invoices = SupplierInvoice.objects.all()

        # Filters
        status_filter = request.query_params.get('status')
        if status_filter:
            invoices = invoices.filter(status=status_filter)

        supplier_filter = request.query_params.get('supplier')
        if supplier_filter:
            invoices = invoices.filter(supplier_id=supplier_filter)

        # Overdue filter
        overdue = request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            today = timezone.now().date()
            invoices = invoices.filter(
                due_date__lt=today,
                status__in=['RECEIVED', 'APPROVED', 'SCHEDULED_PAYMENT']
            )

        serializer = SupplierInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new supplier invoice."""
        serializer = SupplierInvoiceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        invoice = serializer.save(created_by=request.user)

        return Response(
            SupplierInvoiceSerializer(invoice).data,
            status=status.HTTP_201_CREATED
        )


class SupplierInvoiceDetailView(APIView):
    """Get, update, or delete a specific supplier invoice."""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        """Get supplier invoice details."""
        invoice = get_object_or_404(SupplierInvoice, pk=pk)
        serializer = SupplierInvoiceSerializer(invoice)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Update supplier invoice."""
        invoice = get_object_or_404(SupplierInvoice, pk=pk)

        # Don't allow editing if already paid
        if invoice.status == 'PAID':
            return Response({
                'error': 'Cannot edit invoice that is already paid'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = SupplierInvoiceSerializer(
            invoice,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        """Cancel a supplier invoice."""
        invoice = get_object_or_404(SupplierInvoice, pk=pk)

        if invoice.status == 'PAID':
            return Response({
                'error': 'Cannot cancel invoice that is already paid'
            }, status=status.HTTP_400_BAD_REQUEST)

        invoice.status = 'CANCELLED'
        invoice.save()

        return Response({
            'detail': 'Invoice cancelled successfully'
        }, status=status.HTTP_200_OK)


class MarkInvoiceAsPaidView(APIView):
    """Mark a supplier invoice as paid."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, pk):
        """
        Mark invoice as paid.

        Request body (optional):
        {
            "payment_date": "2025-01-16",
            "payment_method": "BANK_TRANSFER"
        }
        """
        invoice = get_object_or_404(SupplierInvoice, pk=pk)

        if invoice.status == 'PAID':
            return Response({
                'error': 'Invoice is already marked as paid'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = MarkInvoiceAsPaidSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        invoice.mark_as_paid(
            payment_date=data.get('payment_date'),
            payment_method=data.get('payment_method')
        )

        return Response({
            'detail': 'Invoice marked as paid successfully',
            'invoice': SupplierInvoiceSerializer(invoice).data
        }, status=status.HTTP_200_OK)
