"""
Payment Processing Models
"""
from django.db import models
from django.contrib.auth.models import User


class Payment(models.Model):
    """
    Payment records for orders.
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

    def __str__(self):
        return f"Payment {self.paymentID} for Order {self.order.orderID}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.update_payment_status()

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

