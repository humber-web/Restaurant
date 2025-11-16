"""
Supplier Management Models for SAF-T CV compliance
"""
from django.db import models
from django.core.validators import RegexValidator


class Supplier(models.Model):
    """
    Supplier (Fornecedor) model for SAF-T CV compliance.

    SAF-T Requirements:
    - SupplierID (unique)
    - CompanyName (required)
    - TaxRegistrationNumber (NIF - required)
    - BillingAddress (required)
    - Contact (telephone/email)
    """

    # Primary Key
    supplierID = models.AutoField(primary_key=True)

    # Tax Registration (NIF - Número de Identificação Fiscal)
    tax_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{9}$',
                message='NIF deve ter 9 dígitos'
            )
        ],
        verbose_name="NIF",
        help_text="Número de Identificação Fiscal (9 dígitos)"
    )

    # Company Info (required for suppliers)
    company_name = models.CharField(
        max_length=200,
        verbose_name="Nome da Empresa"
    )

    # Contact Person
    contact_person = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Pessoa de Contacto"
    )

    # Billing Address (Required for SAF-T)
    street_name = models.CharField(
        max_length=200,
        verbose_name="Rua"
    )
    building_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Número"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Cidade"
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name="Código Postal",
        help_text="Formato: 7600-000"
    )
    region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Região"
    )
    country = models.CharField(
        max_length=2,
        default='CV',
        verbose_name="País (Código ISO)",
        help_text="Código ISO 3166-1 alpha-2 (ex: CV, PT)"
    )

    # Additional Address Info
    address_detail = models.TextField(
        null=True,
        blank=True,
        verbose_name="Detalhes de Morada",
        help_text="Informações adicionais (apartamento, andar, etc.)"
    )

    # Contact Information
    telephone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Telefone"
    )
    mobile_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Telemóvel"
    )
    fax = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Fax"
    )
    email = models.EmailField(
        max_length=254,
        null=True,
        blank=True,
        verbose_name="Email"
    )
    website = models.URLField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Website"
    )

    # Bank Information (for payments)
    bank_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Banco"
    )
    bank_account = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Conta Bancária"
    )
    iban = models.CharField(
        max_length=34,
        null=True,
        blank=True,
        verbose_name="IBAN"
    )

    # Payment Terms
    payment_terms = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Condições de Pagamento",
        help_text="ex: 30 dias, Pronto pagamento"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notes
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas"
    )

    class Meta:
        db_table = 'apps_supplier'
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['tax_id']),
            models.Index(fields=['company_name']),
        ]

    def __str__(self):
        return f"{self.company_name} (NIF: {self.tax_id})"

    @property
    def full_address(self):
        """Return formatted full address"""
        parts = []
        if self.street_name:
            parts.append(self.street_name)
        if self.building_number:
            parts.append(f"Nº {self.building_number}")
        if self.city:
            parts.append(self.city)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.region:
            parts.append(self.region)
        return ", ".join(parts)
