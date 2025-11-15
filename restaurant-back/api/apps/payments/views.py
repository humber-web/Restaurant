"""
Payment Processing Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from decimal import Decimal
from datetime import datetime, date

from .models import Payment
from .serializers import PaymentSerializer
from apps.common.permissions import IsManager
from apps.common.feature_flags import FeatureFlags, Modules
from apps.orders.models import Order
from apps.cash_register.models import CashRegister
from .services.fiscal_service import FiscalService
from .services.saft_export_service import SAFTExportService
from .services.efatura_service import EFaturaService


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
        selected_items = request.data.get('selected_items', [])  # Optional: [{"menu_item_id": 1, "quantity": 2}]

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
        if selected_items:
            from .models import PaymentItem

            # Build a map of menu_item_id -> quantity to pay
            items_to_pay = {
                item_data['menu_item_id']: item_data['quantity']
                for item_data in selected_items
            }

            for item in order.items.all():
                menu_item_id = item.menu_item.itemID

                # Check if this item should be paid
                if menu_item_id in items_to_pay:
                    quantity_to_pay = items_to_pay[menu_item_id]

                    # Validate quantity
                    if quantity_to_pay <= 0:
                        continue  # Skip invalid quantities

                    # Don't allow paying more than what's remaining
                    remaining_qty = item.remaining_quantity()
                    if quantity_to_pay > remaining_qty:
                        quantity_to_pay = remaining_qty

                    if quantity_to_pay > 0:
                        # Calculate amount for the specific quantity (with IVA)
                        item_unit_price = item.price  # Price per unit
                        item_subtotal = item_unit_price * quantity_to_pay
                        item_with_iva = item_subtotal * Decimal('1.15')  # Add 15% IVA

                        PaymentItem.objects.create(
                            payment=payment,
                            order_item=item,
                            quantity_paid=quantity_to_pay,
                            amount_paid=item_with_iva
                        )

        # Add transaction to cash register
        cash_register.add_transaction(amount, payment_method)

        # Update order payment status based on remaining amount AFTER this payment
        # Note: remaining_amount() already accounts for the payment we just created above
        new_remaining = order.remaining_amount()
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


# ===== FISCAL COMPLIANCE VIEWS (SAF-T CV / e-Fatura) =====

class SignInvoiceView(APIView):
    """
    Sign an invoice (generate fiscal fields and mark as legally valid).
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, pk):
        """
        Sign an invoice by payment ID.
        This generates: invoice_no, invoice_hash, IUD, and marks as signed.
        """
        payment = get_object_or_404(Payment, pk=pk)

        # Check if already signed
        if payment.is_signed:
            return Response({
                'error': 'Invoice is already signed and cannot be modified.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Sign the invoice
            signed_payment = FiscalService.sign_invoice(payment)

            serializer = PaymentSerializer(signed_payment)
            return Response({
                'detail': 'Invoice signed successfully.',
                'payment': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'Failed to sign invoice: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportSAFTView(APIView):
    """
    Export SAF-T CV (Standard Audit File for Tax - Cabo Verde).
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """
        Export SAF-T XML for a date range.

        Query parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)

        Returns:
            XML file download
        """
        # Get date parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        # Validate parameters
        if not start_date_str or not end_date_str:
            return Response({
                'error': 'Both start_date and end_date are required (format: YYYY-MM-DD)'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate date range
        if start_date > end_date:
            return Response({
                'error': 'start_date must be before or equal to end_date'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Generate SAF-T XML
            service = SAFTExportService(start_date, end_date)
            xml_content = service.generate_saft_xml()

            # Prepare HTTP response with XML file
            filename = f'SAFT-CV_{start_date}_{end_date}.xml'
            response = HttpResponse(xml_content, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            return Response({
                'error': f'Failed to generate SAF-T: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateInvoiceHashView(APIView):
    """
    Validate invoice hash chain integrity.
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        """
        Validate hash for a specific invoice.
        """
        payment = get_object_or_404(Payment, pk=pk)

        if not payment.is_signed:
            return Response({
                'error': 'Invoice is not signed yet.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            is_valid = FiscalService.validate_hash_chain(payment)

            return Response({
                'invoice_no': payment.invoice_no,
                'is_valid': is_valid,
                'invoice_hash': payment.invoice_hash,
                'message': 'Hash is valid' if is_valid else 'Hash validation failed - invoice may have been tampered with'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'Failed to validate hash: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===== E-FATURA CV VIEWS (Real-time Electronic Invoicing) =====

class GenerateEFaturaView(APIView):
    """
    Generate e-Fatura XML for individual invoice.
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, pk):
        """
        Generate and submit e-Fatura XML for a payment/invoice.

        SIMULATION MODE: Saves XML locally instead of sending to DNRE.
        When DNRE credentials available, will submit to real API.
        """
        payment = get_object_or_404(Payment, pk=pk)

        # Check if payment is signed
        if not payment.is_signed:
            return Response({
                'error': 'Payment must be signed before generating e-Fatura. Use /sign/ endpoint first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Generate and submit e-Fatura
            service = EFaturaService(payment)
            result = service.submit_to_dnre()

            return Response({
                'detail': 'e-Fatura XML generated successfully',
                'mode': result['mode'],
                'invoice_no': result['invoice_no'],
                'iud': result['iud'],
                'file_path': result.get('file_path'),
                'message': result['message']
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Failed to generate e-Fatura: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DownloadEFaturaXMLView(APIView):
    """
    Download e-Fatura XML for an invoice.
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, pk):
        """
        Download e-Fatura XML for a specific payment.
        """
        payment = get_object_or_404(Payment, pk=pk)

        if not payment.is_signed:
            return Response({
                'error': 'Payment must be signed first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Generate XML
            service = EFaturaService(payment)
            xml_content = service.generate_xml()

            # Prepare HTTP response with XML file
            filename = f'efatura_{payment.invoice_type}_{payment.invoice_no.replace("/", "_")}_{payment.invoice_date}.xml'
            response = HttpResponse(xml_content, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            return Response({
                'error': f'Failed to download e-Fatura XML: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignAndSubmitEFaturaView(APIView):
    """
    Sign invoice AND generate e-Fatura in one step (convenience endpoint).
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, pk):
        """
        1. Sign the invoice (if not already signed)
        2. Generate and submit e-Fatura XML

        This is the recommended endpoint for normal workflow.

        Optional request body:
        - customer_tax_id: NIF of the customer (defaults to "999999999" for Consumidor Final)
        - customer_name: Name of the customer (defaults to "Consumidor Final")
        """
        payment = get_object_or_404(Payment, pk=pk)

        try:
            # Update customer info if provided
            customer_tax_id = request.data.get('customer_tax_id', '').strip()
            customer_name = request.data.get('customer_name', '').strip()

            if customer_tax_id:
                payment.customer_tax_id = customer_tax_id
                payment.customer_name = customer_name or 'Cliente'
                payment.save(update_fields=['customer_tax_id', 'customer_name'])

            # Step 1: Sign if not signed
            if not payment.is_signed:
                payment = FiscalService.sign_invoice(payment)

            # Step 2: Generate and submit e-Fatura
            service = EFaturaService(payment)
            result = service.submit_to_dnre()

            return Response({
                'detail': 'Invoice signed and e-Fatura generated successfully',
                'payment': PaymentSerializer(payment).data,
                'efatura': {
                    'mode': result['mode'],
                    'invoice_no': result['invoice_no'],
                    'iud': result['iud'],
                    'file_path': result.get('file_path'),
                    'message': result['message']
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'Failed to sign and submit e-Fatura: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListInvoicesView(APIView):
    """
    List all invoices (signed payments) with advanced filtering.
    Requires: payments module + authentication + manager permission
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """
        List invoices with filters.

        Query parameters:
        - invoice_type: Filter by type (FT, FR, NC, TV)
        - is_signed: Filter by signed status (true/false)
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - search: Search in invoice_no or customer_name
        - page: Page number (default: 1)
        - page_size: Items per page (default: 50, max: 100)
        """
        # Base queryset - only signed payments with complete invoice data
        # Filter by is_signed=True AND invoice_no is not null/empty to ensure data integrity
        invoices = Payment.objects.filter(
            is_signed=True,
            invoice_no__isnull=False
        ).exclude(
            invoice_no=''
        ).select_related('order').order_by('-invoice_date', '-paymentID')

        # Filter by invoice type
        invoice_type = request.query_params.get('invoice_type')
        if invoice_type:
            invoices = invoices.filter(invoice_type=invoice_type)

        # Filter by date range
        start_date = request.query_params.get('start_date')
        if start_date:
            invoices = invoices.filter(invoice_date__gte=start_date)

        end_date = request.query_params.get('end_date')
        if end_date:
            invoices = invoices.filter(invoice_date__lte=end_date)

        # Search in invoice number or customer name
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            invoices = invoices.filter(
                Q(invoice_no__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_tax_id__icontains=search)
            )

        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 50)), 100)

        start = (page - 1) * page_size
        end = start + page_size

        total_count = invoices.count()
        invoices_page = invoices[start:end]

        # Serialize
        serializer = PaymentSerializer(invoices_page, many=True)

        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
