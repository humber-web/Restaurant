from rest_framework import serializers
from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = InventoryItem
        fields = '__all__'

    def get_product_name(self, obj):
        """Get the name of the related menu item (product)."""
        if obj.menu_item:
            return obj.menu_item.name
        return None
