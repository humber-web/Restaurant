"""
Menu Management Models
"""
from django.db import models

CHOICES_PREPARED_IN = (
    ('1', 'Kitchen'),
    ('2', 'Bar'),
    ('3', 'Both'),
)


class MenuCategory(models.Model):
    """
    Categories for menu items (e.g., Drinks, Appetizers, Main Course).
    """
    categoryID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    prepared_in = models.CharField(max_length=1, choices=CHOICES_PREPARED_IN, default='3')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'apps_menucategory'  # Use existing table
        verbose_name = 'Menu Category'
        verbose_name_plural = 'Menu Categories'


class MenuItem(models.Model):
    """
    Individual menu items with pricing and availability.
    """
    itemID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    ingredients = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)
    categoryID = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    is_quantifiable = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'apps_menuitem'  # Use existing table
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
