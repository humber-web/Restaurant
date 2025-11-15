"""
Serializers for common app models.
"""
from rest_framework import serializers
from .models import CompanySettings, TaxRate


class CompanySettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for CompanySettings (singleton configuration).
    """
    class Meta:
        model = CompanySettings
        fields = [
            'id',
            'tax_registration_number',
            'company_name',
            'street_name',
            'building_number',
            'city',
            'postal_code',
            'country',
            'telephone',
            'fax',
            'email',
            'website',
            'fiscal_year_start_month',
            'invoice_series',
            'credit_note_series',
            'receipt_series',
            'software_certificate_number',
            'software_version',
            'default_tax_code',
            'default_tax_percentage',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_tax_registration_number(self, value):
        """Validate NIF format (basic validation)"""
        if not value.isdigit() or len(value) != 9:
            raise serializers.ValidationError(
                "NIF deve ter exatamente 9 digitos numericos."
            )
        return value

    def validate_fiscal_year_start_month(self, value):
        """Validate fiscal year start month is between 1 and 12"""
        if not 1 <= value <= 12:
            raise serializers.ValidationError(
                "Mes deve estar entre 1 (Janeiro) e 12 (Dezembro)."
            )
        return value


class TaxRateSerializer(serializers.ModelSerializer):
    """
    Serializer for TaxRate (IVA configuration).
    """
    tax_code_display = serializers.CharField(source='get_tax_code_display', read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = TaxRate
        fields = [
            'id',
            'tax_code',
            'tax_code_display',
            'description',
            'percentage',
            'valid_from',
            'valid_to',
            'is_active',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_status(self, obj):
        """Get human-readable status"""
        if obj.is_active:
            if obj.valid_to:
                return f"Ativa ate {obj.valid_to.strftime('%d/%m/%Y')}"
            return "Ativa"
        return "Inativa"

    def validate_percentage(self, value):
        """Validate percentage is between 0 and 100"""
        if not 0 <= value <= 100:
            raise serializers.ValidationError(
                "Percentagem deve estar entre 0 e 100."
            )
        return value

    def validate(self, data):
        """Cross-field validation"""
        valid_from = data.get('valid_from')
        valid_to = data.get('valid_to')

        if valid_from and valid_to and valid_to < valid_from:
            raise serializers.ValidationError({
                'valid_to': "Data final nao pode ser anterior a data inicial."
            })

        return data
