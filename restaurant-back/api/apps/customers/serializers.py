"""
Customer Serializers
"""
from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model with full address and name properties
    """
    full_name = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'customerID', 'customer_type', 'tax_id',
            'company_name', 'first_name', 'last_name',
            'street_name', 'building_number', 'city', 'postal_code',
            'region', 'country', 'address_detail',
            'telephone', 'mobile_phone', 'fax', 'email', 'website',
            'is_active', 'notes',
            'created_at', 'updated_at',
            # Computed fields
            'full_name', 'full_address'
        ]
        read_only_fields = ['customerID', 'created_at', 'updated_at', 'full_name', 'full_address']

    def validate_tax_id(self, value):
        """
        Validate NIF format (9 digits for CV)
        """
        if not value.isdigit() or len(value) != 9:
            raise serializers.ValidationError("NIF deve ter exatamente 9 dígitos numéricos")
        return value

    def validate(self, attrs):
        """
        Validate customer data based on type
        """
        customer_type = attrs.get('customer_type')

        if customer_type == 'COMPANY':
            # Company must have company_name
            if not attrs.get('company_name'):
                raise serializers.ValidationError({
                    'company_name': 'Nome da empresa é obrigatório para tipo COMPANY'
                })
        elif customer_type == 'INDIVIDUAL':
            # Individual should have at least first name or last name
            if not attrs.get('first_name') and not attrs.get('last_name'):
                raise serializers.ValidationError({
                    'first_name': 'Primeiro nome ou apelido é obrigatório para tipo INDIVIDUAL'
                })

        return attrs


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for customer lists
    """
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'customerID', 'customer_type', 'tax_id',
            'full_name', 'city', 'telephone', 'email',
            'is_active'
        ]
