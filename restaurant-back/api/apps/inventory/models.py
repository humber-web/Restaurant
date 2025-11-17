"""
Inventory Management Models
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class InventoryItem(models.Model):
    """
    Inventory items linked to menu items for stock management.
    Now properly linked to suppliers for purchase tracking.
    """
    itemID = models.AutoField(primary_key=True)
    itemName = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default='',
        verbose_name="Nome do Item",
        help_text="Nome do item de inventário"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Quantidade em Stock"
    )
    reserved_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Quantidade Reservada",
        help_text="Quantidade reservada em pedidos pendentes"
    )

    # Link to supplier (proper ForeignKey now!)
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='inventory_items',
        verbose_name="Fornecedor",
        help_text="Fornecedor principal deste item"
    )

    # Cost tracking
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Custo Unitário",
        help_text="Último preço de custo do fornecedor"
    )

    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='inventory_items',
        verbose_name="Item do Menu"
    )

    oversell_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Quantidade Vendida sem Stock"
    )

    # Additional fields for better inventory management
    reorder_level = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Nível de Reposição",
        help_text="Quando o stock atingir este nível, fazer nova encomenda"
    )
    reorder_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Quantidade de Reposição",
        help_text="Quantidade a encomendar quando atingir nível de reposição"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        supplier_name = self.supplier.company_name if self.supplier else "Sem Fornecedor"
        return f"{self.itemName} - {supplier_name}"

    @property
    def available_quantity(self):
        """Quantity available for sale (total - reserved)."""
        return self.quantity - self.reserved_quantity

    @property
    def needs_reorder(self):
        """Check if stock level requires reordering."""
        if self.reorder_level:
            return self.available_quantity <= self.reorder_level
        return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.menu_item:
            self.update_menu_item_availability()

    def update_menu_item_availability(self):
        """Update menu item availability based on stock quantity."""
        if self.menu_item:
            if self.available_quantity > 0:
                self.menu_item.availability = True
            else:
                self.menu_item.availability = False
            self.menu_item.save()

    class Meta:
        db_table = 'apps_inventoryitem'  # Use existing table
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
        ordering = ['itemName']
