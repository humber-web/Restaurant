from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, OrderDetails
from apps.menu.models import MenuItem
from apps.tables.models import Table
from apps.common.feature_flags import FeatureFlags, Modules


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'name', 'quantity', 'price', 'status', 'to_be_prepared_in']
        read_only_fields = ['price', 'name', 'to_be_prepared_in']

    def get_name(self, obj):
        return obj.menu_item.name


class OrderDetailsSerializer(serializers.ModelSerializer):
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), allow_null=True, required=False)

    class Meta:
        model = OrderDetails
        fields = ['table', 'online_order_info']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    details = OrderDetailsSerializer()

    class Meta:
        model = Order
        fields = ['orderID', 'customer', 'items', 'status', 'totalAmount', 'totalIva', 'grandTotal', 
                  'paymentStatus', 'orderType', 'created_at', 'updated_at', 'last_updated_by', 'details']
        read_only_fields = ['totalAmount', 'totalIva', 'created_at', 'updated_at', 'last_updated_by', 'grandTotal']

    def validate(self, data):
        # Check if the table already has a pending order
        table = data.get('details', {}).get('table')
        if table and Order.objects.filter(details__table=table, paymentStatus='PENDING').exists():
            raise serializers.ValidationError(f"Table {table.tableid} already has a pending order.")
        return data

    def create(self, validated_data):
        order_items_data = validated_data.pop('items')
        order_details_data = validated_data.pop('details')
        total_amount = sum(item['menu_item'].price * item['quantity'] for item in order_items_data)
        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage
        grand_total = total_amount + total_iva
        order = Order.objects.create(**validated_data, totalAmount=total_amount, totalIva=total_iva, grandTotal=grand_total)

        for item_data in order_items_data:
            menu_item = item_data['menu_item']

            # Only manage inventory if the inventory module is enabled (Premium feature)
            if FeatureFlags.is_module_enabled(Modules.INVENTORY):
                if menu_item.is_quantifiable:
                    inventory_item = menu_item.inventory_items.first()

                    if inventory_item:
                        if inventory_item.quantity < item_data['quantity']:
                            oversell_qty = item_data['quantity'] - inventory_item.quantity
                            inventory_item.oversell_quantity += oversell_qty
                            inventory_item.quantity = 0
                        else:
                            inventory_item.quantity -= item_data['quantity']

                        inventory_item.reserved_quantity += item_data['quantity']
                        inventory_item.save()

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=item_data['quantity'],
                price=menu_item.price,
            )

        OrderDetails.objects.create(order=order, **order_details_data)

        table = order_details_data.get('table')
        if table:
            table.status = 'OC'
            table.save()

        order.totalAmount = total_amount
        order.totalIva = total_iva
        order.grandTotal = grand_total

        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('items', None)
        if order_items_data:
            for item_data in order_items_data:
                menu_item = item_data.get('menu_item')
                menu_item_id = menu_item.itemID
                quantity = item_data.get('quantity', 0)
                if quantity > 0:
                    # Add or update item
                    order_item, created = OrderItem.objects.get_or_create(
                        order=instance,
                        menu_item_id=menu_item_id,
                        defaults={'quantity': quantity, 'price': MenuItem.objects.get(pk=menu_item_id).price}
                    )
                    if created:
                        self.update_inventory(menu_item, quantity)
                    else:
                        old_quantity = order_item.quantity
                        order_item.quantity = quantity
                        quantity_changed = quantity - old_quantity
                        order_item.price = order_item.menu_item.price
                        self.update_inventory(menu_item, quantity_changed)
                        order_item.save()
                else:
                    # Remove item
                    order_item = OrderItem.objects.filter(order=instance, menu_item_id=menu_item_id).first()
                    if order_item:
                        self.update_inventory(menu_item, -order_item.quantity)
                        order_item.delete()

        total_amount = sum(item.menu_item.price * item.quantity for item in instance.items.all())
        iva_percentage = Decimal('0.15')  # 15% IVA
        total_iva = total_amount * iva_percentage
        grand_total = total_amount + total_iva

        instance.totalAmount = total_amount
        instance.totalIva = total_iva
        instance.grandTotal = grand_total
        if instance.totalAmount == 0:
            instance.status = 'CANCELED'

        instance.save()
        return instance

    def update_inventory(self, menu_item, quantity_change):
        """Update inventory only if inventory module is enabled."""
        # Only manage inventory if the inventory module is enabled (Premium feature)
        if not FeatureFlags.is_module_enabled(Modules.INVENTORY):
            return

        if menu_item.is_quantifiable:
            inventory_item = menu_item.inventory_items.first()
            if inventory_item:
                inventory_item.reserved_quantity += quantity_change
                inventory_item.quantity -= quantity_change
                inventory_item.save()
