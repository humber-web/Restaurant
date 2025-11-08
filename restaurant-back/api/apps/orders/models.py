"""
Order Management Models
"""
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


CHOICES_STATUS = (
    ('1', 'Pending'),
    ('2', 'Preparing'),
    ('3', 'Ready'),
    ('4', 'CANCELED'),
)


class Order(models.Model):
    """
    Main order model tracking customer orders.
    """
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'In Preparation'),
        ('READY', 'Ready'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]

    ORDER_TYPE_CHOICES = [
        ('RESTAURANT', 'Restaurant'),
        ('ONLINE', 'Online'),
    ]

    orderID = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='customer_orders'
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='PENDING'
    )
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2)
    totalIva = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grandTotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paymentStatus = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )
    orderType = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.orderID} ({self.orderType})"

    def calculate_totals(self):
        """Calculate totalAmount, totalIva, and grandTotal from order items."""
        from decimal import Decimal

        total_amount = sum(
            item.price * item.quantity
            for item in self.items.all()
        )

        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage
        grand_total = total_amount + total_iva

        self.totalAmount = total_amount
        self.totalIva = total_iva
        self.grandTotal = grand_total

    def save(self, *args, **kwargs):
        """Override save to ensure totals are set."""
        # If creating new order without totals, set them to 0
        if self.totalAmount is None:
            self.totalAmount = Decimal('0.00')
        if self.totalIva is None:
            self.totalIva = Decimal('0.00')
        if self.grandTotal is None:
            self.grandTotal = Decimal('0.00')

        super().save(*args, **kwargs)

    def update_payment_status(self):
        """Update payment status based on completed payments."""
        if self.payments.filter(payment_status='COMPLETED').exists():
            self.paymentStatus = 'PAID'
        else:
            self.paymentStatus = 'PENDING'
        self.save()

    class Meta:
        db_table = 'apps_order'  # Use existing table
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']


class OrderItem(models.Model):
    """
    Individual items within an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    to_be_prepared_in = models.CharField(max_length=1, default='3')
    status = models.CharField(max_length=1, choices=CHOICES_STATUS, default='1')

    def save(self, *args, **kwargs):
        """Auto-set price, preparation location from menu item category and update order totals."""
        # Auto-set price from menu item if not provided
        if self.menu_item and not self.price:
            self.price = self.menu_item.price

        # Auto-set preparation location from menu item category
        if self.menu_item and self.menu_item.categoryID:
            self.to_be_prepared_in = self.menu_item.categoryID.prepared_in

        super().save(*args, **kwargs)

        # Recalculate order totals after saving item
        if self.order:
            self.order.calculate_totals()
            self.order.save()

    def delete(self, *args, **kwargs):
        """Update order totals after deleting item."""
        order = self.order
        super().delete(*args, **kwargs)

        # Recalculate order totals after deletion
        if order:
            order.calculate_totals()
            order.save()

    def is_paid(self):
        """
        Check if this order item has been paid for.
        Returns True if the item appears in any completed payment.
        """
        # Check if this order item is linked to any payment items
        return self.payments.filter(payment__payment_status='COMPLETED').exists()

    def __str__(self):
        return f"Order {self.order.orderID} - Item {self.menu_item.name}"

    class Meta:
        db_table = 'apps_orderitem'  # Use existing table
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'


class OrderDetails(models.Model):
    """
    Additional details for orders including table assignment and online order info.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='details')
    table = models.ForeignKey(
        'tables.Table',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_details'
    )
    online_order_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Details for Order {self.order.orderID}"

    class Meta:
        db_table = 'apps_orderdetails'  # Use existing table
        verbose_name = 'Order Details'
        verbose_name_plural = 'Order Details'
