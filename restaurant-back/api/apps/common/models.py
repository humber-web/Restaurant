"""
Common models for cross-cutting concerns.
"""
from django.db import models
from django.core.exceptions import ValidationError


class ModuleSubscription(models.Model):
    """
    Track which modules are enabled for the organization.
    This allows per-organization module licensing.
    """
    module_name = models.CharField(max_length=50, unique=True, db_index=True)
    is_enabled = models.BooleanField(default=True)
    enabled_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave blank for no expiration")

    # Billing information
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Metadata
    notes = models.TextField(blank=True, help_text="Internal notes about this subscription")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_common_module_subscription'
        ordering = ['module_name']
        verbose_name = 'Module Subscription'
        verbose_name_plural = 'Module Subscriptions'

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"{self.module_name} - {status}"

    def clean(self):
        """Validate module dependencies before enabling."""
        from apps.common.feature_flags import FeatureFlags, PREMIUM_MODULES, FREE_MODULES

        if self.is_enabled and self.module_name in PREMIUM_MODULES:
            # Check if required modules are enabled
            satisfied, missing = FeatureFlags.check_dependencies(self.module_name)
            if not satisfied:
                raise ValidationError(
                    f"Cannot enable {self.module_name}. Missing required modules: {', '.join(missing)}"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CompanySettings(models.Model):
    """
    Singleton model to store company fiscal information required for SAF-T CV export.
    Only one instance should exist.
    """
    # Identification
    tax_registration_number = models.CharField(
        max_length=20,
        verbose_name="NIF",
        help_text="Número de Identificação Fiscal da empresa"
    )
    company_name = models.CharField(
        max_length=200,
        verbose_name="Nome da Empresa"
    )

    # Address
    street_name = models.CharField(max_length=200, verbose_name="Rua")
    building_number = models.CharField(max_length=10, verbose_name="Número", blank=True)
    city = models.CharField(max_length=50, verbose_name="Cidade")
    postal_code = models.CharField(max_length=20, verbose_name="Código Postal")
    country = models.CharField(max_length=2, default='CV', verbose_name="País")

    # Contact
    telephone = models.CharField(max_length=20, verbose_name="Telefone")
    fax = models.CharField(max_length=20, blank=True, verbose_name="Fax")
    email = models.EmailField(verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Website")

    # Fiscal Information
    fiscal_year_start_month = models.IntegerField(
        default=1,
        verbose_name="Mês de início do ano fiscal",
        help_text="1=Janeiro, 2=Fevereiro, etc."
    )

    # Invoice Series Configuration
    invoice_series = models.CharField(
        max_length=10,
        default='FT A',
        verbose_name="Série de Faturas",
        help_text="Ex: 'FT A', 'FT B', etc."
    )
    credit_note_series = models.CharField(
        max_length=10,
        default='NC A',
        verbose_name="Série de Notas de Crédito"
    )
    receipt_series = models.CharField(
        max_length=10,
        default='TV A',
        verbose_name="Série de Talões de Venda"
    )

    # Software Certification
    software_certificate_number = models.CharField(
        max_length=20,
        default='0',
        verbose_name="Número de Certificado do Software",
        help_text="Use '0' até obter a certificação oficial"
    )
    software_version = models.CharField(
        max_length=50,
        default='1.0.0',
        verbose_name="Versão do Software"
    )

    # Tax Configuration
    default_tax_code = models.CharField(
        max_length=10,
        default='NOR',
        choices=[
            ('NOR', 'Normal - 15%'),
            ('ISE', 'Isento'),
            ('RED', 'Reduzida'),
            ('OUT', 'Outro'),
        ],
        verbose_name="Código de IVA Padrão"
    )
    default_tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00,
        verbose_name="Percentagem de IVA Padrão"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_common_company_settings'
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'

    def save(self, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)"""
        if not self.pk and CompanySettings.objects.exists():
            raise ValidationError('Só pode existir uma configuração de empresa.')
        return super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'tax_registration_number': '000000000',
                'company_name': 'Empresa (Configurar)',
                'street_name': 'Rua (Configurar)',
                'city': 'Praia',
                'postal_code': '7600',
                'telephone': '+238',
                'email': 'fiscal@empresa.cv',
            }
        )
        return obj

    def __str__(self):
        return f"{self.company_name} (NIF: {self.tax_registration_number})"
