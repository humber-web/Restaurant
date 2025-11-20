"""
Purchase Order and Supplier Invoice Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from apps.suppliers.models import Supplier
from apps.inventory.models import InventoryItem
from decimal import Decimal


class PurchaseOrder(models.Model):
    """
    Purchase Order (Ordem de Compra) to suppliers.
    Tracks what we order from suppliers before goods arrive.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Rascunho'),
        ('SUBMITTED', 'Enviado ao Fornecedor'),
        ('PARTIALLY_RECEIVED', 'Parcialmente Recebido'),
        ('RECEIVED', 'Recebido'),
        ('INVOICED', 'Faturado'),
        ('PAID', 'Pago'),
        ('CANCELLED', 'Cancelado'),
    ]

    purchaseOrderID = models.AutoField(primary_key=True)
    po_number = models.CharField(
        max_length=60,
        unique=True,
        verbose_name="Número da OC",
        help_text="Formato: OC/AAAA/NNNN (ex: OC/2025/00001)"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        verbose_name="Fornecedor"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name="Estado"
    )
    order_date = models.DateField(
        verbose_name="Data do Pedido"
    )
    expected_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Entrega Prevista"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Total"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_purchase_orders',
        verbose_name="Criado Por"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_purchase_order'
        verbose_name = 'Ordem de Compra'
        verbose_name_plural = 'Ordens de Compra'
        ordering = ['-order_date', '-purchaseOrderID']

    def __str__(self):
        return f"{self.po_number} - {self.supplier.company_name}"

    def calculate_total(self):
        """Calculate total from line items."""
        total = sum(
            item.quantity_ordered * item.unit_price
            for item in self.items.all()
        )
        self.total_amount = total
        return total

    def update_status(self):
        """Auto-update status based on received quantities."""
        items = self.items.all()
        if not items.exists():
            return

        all_received = all(
            item.received_quantity >= item.quantity_ordered
            for item in items
        )
        any_received = any(
            item.received_quantity > 0
            for item in items
        )

        if all_received:
            self.status = 'RECEIVED'
        elif any_received:
            self.status = 'PARTIALLY_RECEIVED'

        self.save()


class PurchaseOrderItem(models.Model):
    """
    Line items in a Purchase Order.
    Links inventory items to purchase orders with quantities and prices.
    """
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Ordem de Compra"
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name='purchase_order_items',
        verbose_name="Item de Inventário"
    )
    quantity_ordered = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade Pedida"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Unitário",
        help_text="Preço de custo do fornecedor"
    )
    received_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Quantidade Recebida"
    )
    received_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Receção"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações"
    )

    class Meta:
        db_table = 'apps_purchase_order_item'
        verbose_name = 'Item de Ordem de Compra'
        verbose_name_plural = 'Itens de Ordem de Compra'

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.inventory_item.itemName}"

    @property
    def line_total(self):
        """Calculate total for this line item."""
        return self.quantity_ordered * self.unit_price

    @property
    def remaining_quantity(self):
        """Calculate quantity still to be received."""
        return self.quantity_ordered - self.received_quantity

    def receive_goods(self, quantity, date=None):
        """
        Mark goods as received and update inventory.

        Args:
            quantity: Quantity received
            date: Receipt date (defaults to today)
        """
        from django.utils import timezone

        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        if self.received_quantity + quantity > self.quantity_ordered:
            raise ValidationError(
                f"Cannot receive more than ordered. "
                f"Ordered: {self.quantity_ordered}, "
                f"Already received: {self.received_quantity}, "
                f"Attempting to receive: {quantity}"
            )

        # Update received quantity
        self.received_quantity += quantity
        self.received_date = date or timezone.now().date()
        self.save()

        # Update inventory quantity
        self.inventory_item.quantity += quantity
        self.inventory_item.save()

        # Update purchase order status
        self.purchase_order.update_status()


class SupplierInvoice(models.Model):
    """
    Invoices received from suppliers.
    Can be linked to a purchase order or standalone.
    """
    STATUS_CHOICES = [
        ('RECEIVED', 'Recebida'),
        ('APPROVED', 'Aprovada'),
        ('SCHEDULED_PAYMENT', 'Pagamento Agendado'),
        ('PAID', 'Paga'),
        ('CANCELLED', 'Cancelada'),
    ]

    supplierInvoiceID = models.AutoField(primary_key=True)
    invoice_number = models.CharField(
        max_length=100,
        verbose_name="Número da Fatura",
        help_text="Número da fatura do fornecedor"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name="Fornecedor"
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplier_invoices',
        verbose_name="Ordem de Compra",
        help_text="Opcional - vincular a uma OC"
    )
    invoice_date = models.DateField(
        verbose_name="Data da Fatura"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Vencimento"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor"
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor do IVA"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (com IVA)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RECEIVED',
        verbose_name="Estado"
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Pagamento"
    )
    payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Método de Pagamento"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_supplier_invoices',
        verbose_name="Criado Por"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_supplier_invoice'
        verbose_name = 'Fatura de Fornecedor'
        verbose_name_plural = 'Faturas de Fornecedores'
        ordering = ['-invoice_date', '-supplierInvoiceID']
        unique_together = [['supplier', 'invoice_number']]

    def __str__(self):
        return f"{self.invoice_number} - {self.supplier.company_name}"

    def mark_as_paid(self, payment_date=None, payment_method=None):
        """
        Mark invoice as paid.

        If linked to a purchase order, automatically receive any unreceived goods
        and update inventory.
        """
        from django.utils import timezone

        self.status = 'PAID'
        self.payment_date = payment_date or timezone.now().date()
        self.payment_method = payment_method
        self.save()

        # Update related purchase order and receive goods
        if self.purchase_order:
            # Automatically receive all unreceived goods from the purchase order
            for po_item in self.purchase_order.items.all():
                remaining_qty = po_item.quantity_ordered - po_item.received_quantity
                if remaining_qty > 0:
                    # Receive the remaining quantity
                    po_item.receive_goods(
                        quantity=remaining_qty,
                        date=self.payment_date
                    )

            # Update purchase order status
            self.purchase_order.status = 'PAID'
            self.purchase_order.save()
