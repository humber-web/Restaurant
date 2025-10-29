"""
Order Management Views
"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from apps.common.permissions import IsManager
from apps.menu.models import MenuItem
from apps.audit.models import OperationLog


class ListOrdersView(APIView):
    """
    List all orders.
    Requires: authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get all orders ordered by ID."""
        orders = Order.objects.all().order_by('orderID')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    """
    Get order detail by ID or search orders.
    Requires: orders module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk=None):
        """
        Get order by ID or search orders by filters.

        Query parameters:
        - customer: Filter by customer username
        - status: Filter by order status
        - payment_status: Filter by payment status
        - order_type: Filter by order type
        - table: Filter by table ID (excludes PAID orders)
        - data: Filter by creation date
        """
        if pk:
            # Get specific order by ID
            try:
                order = Order.objects.get(pk=pk)
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            except Order.DoesNotExist:
                raise Http404("Order not found")
        else:
            # Search orders by filters
            customer = request.query_params.get('customer')
            order_status = request.query_params.get('status')
            payment_status = request.query_params.get('payment_status')
            order_type = request.query_params.get('order_type')
            table = request.query_params.get('table')
            data = request.query_params.get('data')

            queryset = Order.objects.all()

            if customer:
                queryset = queryset.filter(customer__username__icontains=customer)
            if order_status:
                queryset = queryset.filter(status__icontains=order_status)
            if payment_status:
                queryset = queryset.filter(paymentStatus__icontains=payment_status)
            if order_type:
                queryset = queryset.filter(orderType__icontains=order_type)
            if table:
                queryset = queryset.filter(details__table__tableid=table)
                queryset = queryset.exclude(paymentStatus='PAID')  # Exclude PAID orders when searching by table
            if data:
                queryset = queryset.filter(created_at__icontains=data)

            if not queryset.exists():
                raise Http404("No orders found matching the criteria")

            serializer = OrderSerializer(queryset, many=True)
            return Response(serializer.data)


class CreateOrderView(APIView):
    """
    Create a new order.
    Requires: orders module + authentication
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Create a new order.

        Request body:
        {
            "customer": user_id (optional),
            "orderType": "RESTAURANT" or "ONLINE",
            "items": [
                {"menu_item": item_id, "quantity": 2},
                ...
            ],
            "details": {
                "table": table_id (optional),
                "online_order_info": "..." (optional)
            }
        }
        """
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(last_updated_by=request.user)

            # Log operation for audit trail
            if hasattr(request, 'body_data'):
                request.body_data['object_id'] = order.orderID

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateOrderItemsView(APIView):
    """
    Update order items.
    Requires: orders module + authentication
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        """
        Replace entire order with new data.
        """
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            order = serializer.save(last_updated_by=request.user)
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        """
        Partially update order items.
        Add, update, or remove items without replacing entire order.

        Request body:
        {
            "items": [
                {"menu_item": item_id, "quantity": 2},  # Add or update
                {"menu_item": item_id, "quantity": 0},  # Remove
                ...
            ]
        }
        """
        order = get_object_or_404(Order, pk=pk)
        order_items_data = request.data.get('items', [])

        for item_data in order_items_data:
            menu_item_id = item_data.get('menu_item')
            quantity = item_data.get('quantity', 0)

            if quantity > 0:
                # Add or update item
                order_item, created = OrderItem.objects.get_or_create(
                    order=order,
                    menu_item_id=menu_item_id,
                    defaults={'quantity': quantity, 'price': MenuItem.objects.get(pk=menu_item_id).price}
                )
                if not created:
                    order_item.quantity = quantity
                    order_item.price = order_item.menu_item.price
                    order_item.save()
            else:
                # Remove item
                OrderItem.objects.filter(order=order, menu_item_id=menu_item_id).delete()

        # Recalculate totals
        total_amount = sum(item.menu_item.price * item.quantity for item in order.items.all())
        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage
        grand_total = total_amount + total_iva

        order.totalAmount = total_amount
        order.totalIva = total_iva
        order.grandTotal = grand_total

        # Cancel order if no items remain
        if order.totalAmount == 0:
            order.status = 'CANCELLED'

        order.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class TransferOrderItemsView(APIView):
    """
    Transfer items from one order to another.
    Useful for splitting bills or moving items between tables.
    Requires: orders module + authentication
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Transfer all items from source order to target order.
        Source order is deleted after transfer.

        Request body:
        {
            "source_order_id": 123,
            "target_order_id": 456
        }
        """
        source_order_id = request.data.get('source_order_id')
        target_order_id = request.data.get('target_order_id')

        if not source_order_id or not target_order_id:
            return Response({
                'detail': 'source_order_id and target_order_id are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            source_order = Order.objects.get(pk=source_order_id)
            target_order = Order.objects.get(pk=target_order_id)
        except Order.DoesNotExist:
            return Response({
                'detail': 'One or both orders do not exist.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Transfer items and merge quantities
        for item in source_order.items.all():
            existing_item = target_order.items.filter(menu_item=item.menu_item).first()
            if existing_item:
                # Merge quantities if item already exists in target
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                # Move item to target order
                item.order = target_order
                item.save()

        # Delete source order
        source_order.delete()

        # Recalculate totals for target order
        total_amount = sum(item.menu_item.price * item.quantity for item in target_order.items.all())
        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage
        grand_total = total_amount + total_iva

        target_order.totalAmount = total_amount
        target_order.totalIva = total_iva
        target_order.grandTotal = grand_total
        target_order.save()

        serializer = OrderSerializer(target_order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteOrderView(APIView):
    """
    Delete an order.
    Requires: orders module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk, *args, **kwargs):
        """Delete order by ID."""
        order = get_object_or_404(Order, pk=pk)

        # Log deletion for audit trail
        content_type = ContentType.objects.get_for_model(Order)
        OperationLog.objects.create(
            user=request.user,
            action='DELETE',
            content_type=content_type,
            object_id=order.orderID,
            object_repr=f"User {request.user} performed DELETE on order {order.orderID}",
        )

        order.delete()
        return Response({
            'detail': 'Order deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)
