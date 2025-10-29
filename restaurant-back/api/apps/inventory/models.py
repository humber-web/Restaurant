"""
Inventory Management Models
"""
from django.db import models


class InventoryItem(models.Model):
    """
    Inventory items linked to menu items for stock management.
    """
    itemID = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    reserved_quantity = models.IntegerField(default=0)
    supplier = models.CharField(max_length=255)
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )
    oversell_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.menu_item.name} - {self.supplier}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_menu_item_availability()

    def update_menu_item_availability(self):
        """Update menu item availability based on stock quantity."""
        if self.quantity > 0:
            self.menu_item.availability = True
        else:
            self.menu_item.availability = False
        self.menu_item.save()

    class Meta:
        db_table = 'apps_inventoryitem'  # Use existing table
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
