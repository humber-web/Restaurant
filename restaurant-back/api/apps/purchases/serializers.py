"""
Serializers for Purchase Order and Supplier Invoice models
"""
from rest_framework import serializers
from .models import PurchaseOrder, PurchaseOrderItem, SupplierInvoice
from apps.suppliers.serializers import SupplierSerializer
from apps.inventory.serializers import InventoryItemSerializer
from decimal import Decimal


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for Purchase Order line items."""
    inventory_item_name = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()
    remaining_quantity = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'inventory_item', 'inventory_item_name',
            'quantity_ordered', 'unit_price', 'line_total',
            'received_quantity', 'remaining_quantity', 'received_date', 'notes'
        ]
        read_only_fields = ['id', 'inventory_item_name', 'line_total', 'remaining_quantity']

    def get_inventory_item_name(self, obj):
        return obj.inventory_item.itemName if obj.inventory_item else None

    def get_line_total(self, obj):
        return str(obj.line_total)

    def get_remaining_quantity(self, obj):
        return str(obj.remaining_quantity)


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for PO list views."""
    supplier_name = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            'purchaseOrderID', 'po_number', 'supplier', 'supplier_name',
            'status', 'order_date', 'expected_delivery_date',
            'total_amount', 'items_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['purchaseOrderID', 'created_at', 'updated_at']

    def get_supplier_name(self, obj):
        return obj.supplier.company_name if obj.supplier else None

    def get_items_count(self, obj):
        return obj.items.count()


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for PO with nested items and supplier info."""
    supplier_info = SupplierSerializer(source='supplier', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            'purchaseOrderID', 'po_number', 'supplier', 'supplier_info',
            'status', 'order_date', 'expected_delivery_date',
            'total_amount', 'notes', 'items',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'purchaseOrderID', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'items', 'supplier_info'
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None


class CreatePurchaseOrderSerializer(serializers.Serializer):
    """Serializer for creating a new Purchase Order with items."""
    supplier = serializers.IntegerField(help_text="Supplier ID")
    order_date = serializers.DateField()
    expected_delivery_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of items: [{inventory_item: id, quantity_ordered: num, unit_price: num}]"
    )

    def validate_items(self, value):
        """Validate that items list is not empty and has required fields."""
        if not value:
            raise serializers.ValidationError("At least one item is required")

        for item in value:
            if 'inventory_item' not in item:
                raise serializers.ValidationError("Each item must have 'inventory_item' field")
            if 'quantity_ordered' not in item:
                raise serializers.ValidationError("Each item must have 'quantity_ordered' field")
            if 'unit_price' not in item:
                raise serializers.ValidationError("Each item must have 'unit_price' field")

            # Validate positive values
            if Decimal(str(item['quantity_ordered'])) <= 0:
                raise serializers.ValidationError("quantity_ordered must be positive")
            if Decimal(str(item['unit_price'])) < 0:
                raise serializers.ValidationError("unit_price cannot be negative")

        return value


class ReceiveGoodsSerializer(serializers.Serializer):
    """Serializer for receiving goods against a PO item."""
    purchase_order_item_id = serializers.IntegerField()
    quantity_received = serializers.DecimalField(max_digits=10, decimal_places=2)
    received_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_quantity_received(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        return value


class SupplierInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Supplier Invoices."""
    supplier_name = serializers.SerializerMethodField()
    po_number = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()

    class Meta:
        model = SupplierInvoice
        fields = [
            'supplierInvoiceID', 'invoice_number', 'supplier', 'supplier_name',
            'purchase_order', 'po_number', 'invoice_date', 'due_date',
            'amount', 'tax_amount', 'total_amount', 'status',
            'payment_date', 'payment_method', 'notes',
            'days_until_due', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'supplierInvoiceID', 'supplier_name', 'po_number',
            'created_by', 'created_by_name', 'days_until_due',
            'created_at', 'updated_at'
        ]

    def get_supplier_name(self, obj):
        return obj.supplier.company_name if obj.supplier else None

    def get_po_number(self, obj):
        return obj.purchase_order.po_number if obj.purchase_order else None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None

    def get_days_until_due(self, obj):
        """Calculate days until due date."""
        if obj.due_date and obj.status not in ['PAID', 'CANCELLED']:
            from django.utils import timezone
            today = timezone.now().date()
            delta = (obj.due_date - today).days
            return delta
        return None


class MarkInvoiceAsPaidSerializer(serializers.Serializer):
    """Serializer for marking an invoice as paid."""
    payment_date = serializers.DateField(required=False, allow_null=True)
    payment_method = serializers.CharField(required=False, allow_blank=True, max_length=50)
