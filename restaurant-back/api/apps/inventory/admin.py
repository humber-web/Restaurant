"""
Django Admin configuration for Inventory app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import InventoryItem


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """
    Admin interface for Inventory Items with stock warnings.
    """
    list_display = ['itemID', 'menu_item_link', 'supplier', 'quantity', 'reserved_quantity', 
                    'available_quantity', 'oversell_quantity', 'stock_status']
    list_filter = ['supplier', 'menu_item__categoryID']
    search_fields = ['menu_item__name', 'supplier']
    list_editable = ['quantity']
    ordering = ['itemID']
    actions = ['reset_oversell', 'release_reserved']
    raw_id_fields = ['menu_item']
    
    fieldsets = (
        ('Menu Item', {
            'fields': ('menu_item',)
        }),
        ('Stock Information', {
            'fields': ('quantity', 'reserved_quantity', 'oversell_quantity')
        }),
        ('Supplier', {
            'fields': ('supplier',)
        }),
    )
    
    def menu_item_link(self, obj):
        """Display menu item with link."""
        return obj.menu_item.name
    menu_item_link.short_description = 'Menu Item'
    
    def available_quantity(self, obj):
        """Calculate available quantity (not reserved)."""
        available = obj.quantity - obj.reserved_quantity
        if available < 0:
            return format_html('<span style="color: red;">{}</span>', available)
        return available
    available_quantity.short_description = 'Available'
    
    def stock_status(self, obj):
        """Display stock status with colors."""
        if obj.quantity == 0:
            return format_html('<span style="color: red; font-weight: bold;">🔴 Out of Stock</span>')
        elif obj.quantity <= 5:
            return format_html('<span style="color: orange; font-weight: bold;">🟠 Low Stock</span>')
        elif obj.oversell_quantity > 0:
            return format_html('<span style="color: red;">⚠️ Oversold</span>')
        else:
            return format_html('<span style="color: green;">🟢 In Stock</span>')
    stock_status.short_description = 'Status'
    
    def reset_oversell(self, request, queryset):
        """Reset oversell quantity to zero."""
        count = queryset.update(oversell_quantity=0)
        self.message_user(request, f'{count} item(s) oversell quantity reset.')
    reset_oversell.short_description = "Reset oversell quantity"
    
    def release_reserved(self, request, queryset):
        """Release all reserved quantity back to available."""
        for item in queryset:
            item.quantity += item.reserved_quantity
            item.reserved_quantity = 0
            item.save()
        self.message_user(request, f'{queryset.count()} item(s) reserved quantity released.')
    release_reserved.short_description = "Release reserved stock"
