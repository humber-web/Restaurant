"""
Inventory Service Layer
Handles business logic for stock management.
"""
from decimal import Decimal
from .models import InventoryItem


class InventoryService:
    """
    Service class for inventory operations.
    """
    
    @staticmethod
    def reserve_stock(menu_item, quantity):
        """
        Reserve stock for an order.
        
        Args:
            menu_item: MenuItem instance
            quantity: Amount to reserve
            
        Returns:
            bool: True if successful, False if not enough stock
        """
        if not menu_item.is_quantifiable:
            return True
            
        inventory_item = InventoryItem.objects.filter(menu_item=menu_item).first()
        
        if not inventory_item:
            return False
        
        # Check if we have enough stock
        if inventory_item.quantity >= quantity:
            inventory_item.quantity -= quantity
            inventory_item.reserved_quantity += quantity
        else:
            # Handle overselling
            oversell_qty = quantity - inventory_item.quantity
            inventory_item.oversell_quantity += oversell_qty
            inventory_item.reserved_quantity += quantity
            inventory_item.quantity = 0
        
        inventory_item.save()
        return True
    
    @staticmethod
    def release_reserved_stock(menu_item, quantity):
        """
        Release reserved stock (e.g., when payment is completed).
        
        Args:
            menu_item: MenuItem instance
            quantity: Amount to release from reserved
        """
        if not menu_item.is_quantifiable:
            return
            
        inventory_item = InventoryItem.objects.filter(menu_item=menu_item).first()
        
        if inventory_item and inventory_item.reserved_quantity >= quantity:
            inventory_item.reserved_quantity -= quantity
            inventory_item.save()
    
    @staticmethod
    def return_stock(menu_item, quantity):
        """
        Return stock back to inventory (e.g., when order is cancelled).
        
        Args:
            menu_item: MenuItem instance
            quantity: Amount to return
        """
        if not menu_item.is_quantifiable:
            return
            
        inventory_item = InventoryItem.objects.filter(menu_item=menu_item).first()
        
        if inventory_item:
            inventory_item.quantity += quantity
            if inventory_item.reserved_quantity >= quantity:
                inventory_item.reserved_quantity -= quantity
            inventory_item.save()
    
    @staticmethod
    def adjust_stock(menu_item, quantity_delta):
        """
        Adjust stock levels (e.g., for restocking or corrections).
        
        Args:
            menu_item: MenuItem instance
            quantity_delta: Amount to adjust (positive or negative)
        """
        inventory_item = InventoryItem.objects.filter(menu_item=menu_item).first()
        
        if inventory_item:
            inventory_item.quantity += quantity_delta
            if inventory_item.quantity < 0:
                inventory_item.quantity = 0
            inventory_item.save()
    
    @staticmethod
    def get_low_stock_items(threshold=5):
        """
        Get items with stock below threshold.
        
        Args:
            threshold: Minimum stock level
            
        Returns:
            QuerySet of InventoryItem
        """
        return InventoryItem.objects.filter(quantity__lte=threshold)
    
    @staticmethod
    def get_out_of_stock_items():
        """
        Get items that are out of stock.
        
        Returns:
            QuerySet of InventoryItem
        """
        return InventoryItem.objects.filter(quantity=0)
