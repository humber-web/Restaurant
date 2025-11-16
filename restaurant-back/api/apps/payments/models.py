"""
Payment Processing Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Payment(models.Model):
    """
    Payment records for orders with fiscal compliance (SAF-T CV / e-Fatura).
    """
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('ONLINE', 'Online Payment'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    INVOICE_TYPE_CHOICES = [
        ('FT', 'Fatura'),           # Invoice
        ('NC', 'Nota de Crédito'),  # Credit Note
        ('TV', 'Talão de Venda'),   # Sales Receipt (Consumidor Final)
        ('FR', 'Fatura Recibo'),    # Invoice Receipt
    ]

    # Original fields
    paymentID = models.AutoField(primary_key=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cash_register = models.ForeignKey(
        'cash_register.CashRegister',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments'
    )

    # ===== FISCAL FIELDS (SAF-T CV / e-Fatura Compliance) =====

    # Invoice Information
    invoice_no = models.CharField(
        max_length=60,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Número da Fatura",
        help_text="Formato: SÉRIE/ANO/NÚMERO (ex: FT A/2025/00001)"
    )
    invoice_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Fatura"
    )
    invoice_type = models.CharField(
        max_length=10,
        choices=INVOICE_TYPE_CHOICES,
        default='FT',
        verbose_name="Tipo de Documento"
    )

    # Digital Signature (Hash Chain)
    invoice_hash = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name="Hash da Fatura",
        help_text="SHA-256 hash for invoice integrity"
    )
    previous_invoice_hash = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name="Hash da Fatura Anterior",
        help_text="Links invoices in a chain"
    )
    hash_algorithm = models.CharField(
        max_length=10,
        default='SHA256',
        verbose_name="Algoritmo de Hash"
    )

    # Certification
    software_certificate_number = models.CharField(
        max_length=20,
        default='0',
        verbose_name="Número de Certificado do Software"
    )

    # IUD (Identificador Único do Documento)
    iud = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
        verbose_name="IUD",
        help_text="Identificador Único do Documento (45 caracteres)"
    )

    # Fiscal Status
    is_signed = models.BooleanField(
        default=False,
        verbose_name="Assinado",
        help_text="Se True, o documento não pode ser editado"
    )
    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Assinatura"
    )

    # Customer Info (for SAF-T Customer table)
    customer_tax_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="NIF do Cliente"
    )
    customer_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Nome do Cliente"
    )

    def __str__(self):
        return f"Payment {self.paymentID} for Order {self.order.orderID}"

    def save(self, *args, **kwargs):
        """
        Custom save with immutability check.
        Once a payment is signed (is_signed=True), it cannot be modified.
        This ensures fiscal compliance - signed invoices must be immutable.
        """
        # Check if this is an update to an existing signed payment
        if self.pk:  # If this is an update (not a new record)
            try:
                old_instance = Payment.objects.get(pk=self.pk)
                if old_instance.is_signed:
                    # Signed payments cannot be modified
                    raise ValidationError(
                        "Cannot modify a signed payment/invoice. "
                        "Signed fiscal documents are immutable. "
                        "To correct, issue a Credit Note (NC)."
                    )
            except Payment.DoesNotExist:
                # New payment, allow save
                pass

        super().save(*args, **kwargs)
        self.order.update_payment_status()

    def delete(self, *args, **kwargs):
        """
        Custom delete with immutability check.
        Signed payments cannot be deleted - issue a Credit Note instead.
        """
        if self.is_signed:
            raise ValidationError(
                "Cannot delete a signed payment/invoice. "
                "Signed fiscal documents are immutable. "
                "To cancel, issue a Credit Note (NC)."
            )
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'apps_payment'  # Use existing table
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']


class PaymentItem(models.Model):
    """
    Tracks which specific order items were paid for in each payment.
    Allows for partial payments of specific items.
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='paid_items')
    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE, related_name='payments')
    quantity_paid = models.PositiveIntegerField(default=1, help_text="How many of this item were paid in this payment")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount paid for this item in this payment")

    def __str__(self):
        return f"Payment {self.payment.paymentID} - {self.quantity_paid}x {self.order_item.menu_item.name}"

    class Meta:
        db_table = 'apps_payment_item'
        verbose_name = 'Payment Item'
        verbose_name_plural = 'Payment Items'

