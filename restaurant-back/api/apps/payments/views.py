"""
Payment Processing Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from decimal import Decimal

from .models import Payment
from .serializers import PaymentSerializer
from apps.common.permissions import IsManager
from apps.common.feature_flags import FeatureFlags, Modules
from apps.orders.models import Order
from apps.cash_register.models import CashRegister


class ListPaymentsView(APIView):
    """
    List all payments.
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get all payments ordered by most recent."""
        payments = Payment.objects.all().order_by('-created_at')
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentDetailView(APIView):
    """
    Get payment detail by ID or search payments.
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk=None):
        """
        Get payment by ID or search payments by filters.

        Query parameters:
        - order: Filter by order ID
        - payment_method: Filter by payment method
        - payment_status: Filter by payment status
        - processed_by: Filter by user who processed the payment
        """
        if pk:
            # Get specific payment by ID
            payment = get_object_or_404(Payment, pk=pk)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        else:
            # Search payments by filters
            order_id = request.query_params.get('order')
            payment_method = request.query_params.get('payment_method')
            payment_status = request.query_params.get('payment_status')
            processed_by = request.query_params.get('processed_by')

            queryset = Payment.objects.all()

            if order_id:
                queryset = queryset.filter(order__orderID=order_id)
            if payment_method:
                queryset = queryset.filter(payment_method__icontains=payment_method)
            if payment_status:
                queryset = queryset.filter(payment_status__icontains=payment_status)
            if processed_by:
                queryset = queryset.filter(processed_by__username__icontains=processed_by)

            serializer = PaymentSerializer(queryset, many=True)
            return Response(serializer.data)


class ProcessPaymentView(APIView):
    """
    Process a payment for an order.
    Requires: payments module + authentication
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Process payment for an order.

        Request body:
        {
            "orderID": 123,
            "amount": 150.00,
            "payment_method": "CASH" | "CREDIT_CARD" | "DEBIT_CARD" | "ONLINE",
            "selected_item_ids": [1, 2, 3]  // Optional: specific order item IDs being paid
        }

        Returns:
        {
            "detail": "Payment processed successfully.",
            "change_due": 0.00,
            "payment": {...}
        }
        """
        # Validate authentication
        user = request.user
        if isinstance(user, AnonymousUser):
            return Response({
                "error": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Extract payment data
        order_id = request.data.get('orderID')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        selected_item_ids = request.data.get('selected_item_ids', [])  # Optional

        # Validate required fields
        if not all([order_id, amount, payment_method]):
            return Response({
                'error': 'orderID, amount, and payment_method are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get order
        order = get_object_or_404(Order, pk=order_id)

        # Convert to Decimal for accurate calculations
        try:
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid amount format.'
            }, status=status.HTTP_400_BAD_REQUEST)

        grand_total = Decimal(order.grandTotal)

        # Validate payment amount (allow partial payments)
        if amount <= 0:
            return Response({
                'error': 'Invalid payment amount.',
                'hint': 'Amount must be greater than zero.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check how much is still owed (prevent overpayment)
        remaining = order.remaining_amount()
        if amount > remaining:
            return Response({
                'error': 'Payment amount exceeds remaining balance.',
                'remaining': str(remaining),
                'attempted': str(amount),
                'hint': f'This order only needs €{remaining}. Please adjust the payment amount.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify user has an open cash register
        cash_register = CashRegister.objects.filter(
            user=request.user,
            is_open=True
        ).first()

        if not cash_register:
            return Response({
                'error': 'No open cash register found for this user.',
                'hint': 'Please open a cash register before processing payments.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create payment record
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            payment_method=payment_method,
            payment_status='COMPLETED',
            processed_by=request.user,
            cash_register=cash_register
        )

        # Track which items were paid (if specified)
        if selected_item_ids:
            from .models import PaymentItem

            for item in order.items.all():
                # Check if this item's menu_item ID is in the selected list
                if item.menu_item.itemID in selected_item_ids:
                    # Calculate amount for this specific item (with IVA)
                    item_subtotal = item.price * item.quantity
                    item_with_iva = item_subtotal * Decimal('1.15')  # Add 15% IVA

                    PaymentItem.objects.create(
                        payment=payment,
                        order_item=item,
                        quantity_paid=item.quantity,
                        amount_paid=item_with_iva
                    )

        # Add transaction to cash register
        cash_register.add_transaction(amount, payment_method)

        # Update order payment status based on remaining amount AFTER this payment
        new_remaining = order.remaining_amount() - amount
        if new_remaining <= Decimal('0.01'):  # Account for rounding errors
            order.paymentStatus = 'PAID'
            # Release reserved inventory after successful payment
            self._release_inventory(order)
        else:
            order.paymentStatus = 'PARTIALLY_PAID'
        order.save()

        # Update table status if order has a table
        if hasattr(order, 'details') and order.details.table:
            table = order.details.table
            if order.paymentStatus == 'PAID':
                table.status = 'AV'  # Available
            else:
                table.status = 'OC'  # Occupied
            table.save()

        # Calculate change due
        change_due = max(Decimal('0.00'), amount - order.grandTotal)

        return Response({
            'detail': 'Payment processed successfully.',
            'change_due': str(change_due),
            'payment': PaymentSerializer(payment).data
        }, status=status.HTTP_201_CREATED)

    def _release_inventory(self, order):
        """
        Release reserved inventory after successful payment.
        Only works if inventory module is enabled (Premium feature).
        """
        # Only manage inventory if the inventory module is enabled (Premium feature)
        if not FeatureFlags.is_module_enabled(Modules.INVENTORY):
            return

        # Import here to avoid circular imports
        from apps.inventory.services import InventoryService

        for order_item in order.items.all():
            menu_item = order_item.menu_item
            if menu_item.is_quantifiable:
                try:
                    InventoryService.release_reserved_stock(
                        menu_item,
                        order_item.quantity
                    )
                except Exception as e:
                    # Log error but don't fail the payment
                    print(f"Warning: Failed to release inventory for {menu_item.name}: {e}")


class DeletePaymentView(APIView):
    """
    Delete a payment (admin only).
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, pk):
        """
        Delete payment by ID.
        Note: This will also update the order's payment status.
        """
        payment = get_object_or_404(Payment, pk=pk)
        order = payment.order

        # Delete payment
        payment.delete()

        # Recalculate order payment status
        order.update_payment_status()

        return Response({
            'detail': 'Payment deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)
