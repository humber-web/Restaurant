from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'paymentID', 'order', 'amount', 'payment_method', 'payment_status',
            'transaction_id', 'created_at', 'updated_at', 'processed_by',
            # Fiscal/e-Fatura fields
            'invoice_no', 'invoice_date', 'invoice_type', 'invoice_hash',
            'previous_invoice_hash', 'iud', 'is_signed', 'customer_name',
            'customer_tax_id', 'hash_algorithm', 'software_certificate_number'
        ]
        read_only_fields = [
            'payment_status', 'created_at', 'updated_at', 'processed_by',
            'invoice_hash', 'previous_invoice_hash', 'iud', 'is_signed'
        ]

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
