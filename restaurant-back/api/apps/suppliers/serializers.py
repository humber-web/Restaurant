"""
Supplier Serializers
"""
from rest_framework import serializers
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer for Supplier model with full address property
    """
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Supplier
        fields = [
            'supplierID', 'tax_id', 'company_name', 'contact_person',
            'street_name', 'building_number', 'city', 'postal_code',
            'region', 'country', 'address_detail',
            'telephone', 'mobile_phone', 'fax', 'email', 'website',
            'bank_name', 'bank_account', 'iban', 'payment_terms',
            'is_active', 'notes',
            'created_at', 'updated_at',
            # Computed fields
            'full_address'
        ]
        read_only_fields = ['supplierID', 'created_at', 'updated_at', 'full_address']

    def validate_tax_id(self, value):
        """
        Validate NIF format (9 digits for CV)
        """
        if not value.isdigit() or len(value) != 9:
            raise serializers.ValidationError("NIF deve ter exatamente 9 dígitos numéricos")
        return value


class SupplierListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for supplier lists
    """
    class Meta:
        model = Supplier
        fields = [
            'supplierID', 'tax_id', 'company_name',
            'city', 'telephone', 'email', 'is_active'
        ]
