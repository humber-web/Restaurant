from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    # Nested serializer for referenced document (read-only)
    referenced_document_info = serializers.SerializerMethodField()
    # QR Code (generated on-demand from IUD)
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'paymentID', 'order', 'amount', 'payment_method', 'payment_status',
            'transaction_id', 'created_at', 'updated_at', 'processed_by',
            # Fiscal/e-Fatura fields
            'invoice_no', 'invoice_date', 'invoice_type', 'invoice_hash',
            'previous_invoice_hash', 'iud', 'is_signed', 'customer_name',
            'customer_tax_id', 'hash_algorithm', 'software_certificate_number',
            # Credit Note fields
            'referenced_document', 'credit_note_reason', 'referenced_document_info',
            # QR Code
            'qr_code'
        ]
        read_only_fields = [
            'payment_status', 'created_at', 'updated_at', 'processed_by',
            'invoice_hash', 'previous_invoice_hash', 'iud', 'is_signed',
            'referenced_document_info', 'qr_code'
        ]

    def get_referenced_document_info(self, obj):
        """Return basic info about referenced document for Credit Notes."""
        if obj.referenced_document:
            return {
                'paymentID': obj.referenced_document.paymentID,
                'invoice_no': obj.referenced_document.invoice_no,
                'invoice_type': obj.referenced_document.invoice_type,
                'amount': str(obj.referenced_document.amount),
                'invoice_date': obj.referenced_document.invoice_date,
            }
        return None

    def get_qr_code(self, obj):
        """Generate QR Code from IUD (base64 data URL)."""
        if not obj.iud:
            return None

        try:
            from .services.qrcode_service import QRCodeService
            return QRCodeService.generate_qr_code_for_payment(obj)
        except Exception:
            # Return None if QR code generation fails
            return None

    def validate(self, attrs):
        order = attrs.get('order')
        amount = attrs.get('amount')

        if amount != order.totalAmount:
            raise serializers.ValidationError("The payment amount does not match the total amount of the order.")

        return attrs

    def create(self, validated_data):
        validated_data['payment_status'] = 'COMPLETED'
        payment = super().create(validated_data)
        order = payment.order
        order.paymentStatus = 'PAID'
        order.save()
        return payment


class IssueCreditNoteSerializer(serializers.Serializer):
    """
    Serializer for issuing a Credit Note against an existing invoice.
    """
    original_invoice_id = serializers.IntegerField(
        help_text="Payment ID of the original invoice to credit"
    )
    credit_note_reason = serializers.ChoiceField(
        choices=Payment.CREDIT_NOTE_REASON_CHOICES,
        help_text="Reason code for issuing the credit note (M01-M05, M99)"
    )
    partial_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        help_text="Optional: partial amount to credit (leave empty for full credit)"
    )

    def validate_original_invoice_id(self, value):
        """Validate that the original invoice exists and is signed."""
        try:
            invoice = Payment.objects.get(paymentID=value)
        except Payment.DoesNotExist:
            raise serializers.ValidationError(f"Invoice with ID {value} not found")

        if not invoice.is_signed:
            raise serializers.ValidationError(
                "Can only issue credit notes for signed invoices"
            )

        if invoice.invoice_type == 'NC':
            raise serializers.ValidationError(
                "Cannot issue a credit note against another credit note"
            )

        return value

    def validate(self, attrs):
        """Validate partial amount if provided."""
        partial_amount = attrs.get('partial_amount')
        if partial_amount is not None:
            original_invoice = Payment.objects.get(
                paymentID=attrs['original_invoice_id']
            )
            if partial_amount <= 0:
                raise serializers.ValidationError({
                    'partial_amount': 'Partial amount must be positive'
                })
            if partial_amount > original_invoice.amount:
                raise serializers.ValidationError({
                    'partial_amount': f'Partial amount cannot exceed original invoice amount ({original_invoice.amount})'
                })

        return attrs
