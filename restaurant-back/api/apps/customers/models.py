"""
Customer Management Models for SAF-T CV compliance
"""
from django.db import models
from django.core.validators import RegexValidator


class Customer(models.Model):
    """
    Customer (Cliente) model for SAF-T CV compliance.

    SAF-T Requirements:
    - CustomerID (unique)
    - CompanyName (required for companies) or individual name
    - TaxRegistrationNumber (NIF - required)
    - BillingAddress (required)
    - Contact (telephone/email)
    """

    CUSTOMER_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Consumidor Final / Individual'),
        ('COMPANY', 'Empresa'),
    ]

    # Primary Key
    customerID = models.AutoField(primary_key=True)

    # Identification
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='INDIVIDUAL',
        verbose_name="Tipo de Cliente"
    )

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

    # Company Info (for COMPANY type)
    company_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Nome da Empresa"
    )

    # Individual Info (for INDIVIDUAL type)
    first_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Primeiro Nome"
    )
    last_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Apelido"
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
        db_table = 'apps_customer'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['company_name', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['tax_id']),
            models.Index(fields=['company_name']),
            models.Index(fields=['last_name', 'first_name']),
        ]

    def __str__(self):
        if self.customer_type == 'COMPANY' and self.company_name:
            return f"{self.company_name} (NIF: {self.tax_id})"
        elif self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name} (NIF: {self.tax_id})"
        else:
            return f"Cliente {self.customerID} (NIF: {self.tax_id})"

    @property
    def full_name(self):
        """Return full name for display"""
        if self.customer_type == 'COMPANY':
            return self.company_name or f"Cliente {self.customerID}"
        else:
            if self.first_name or self.last_name:
                return f"{self.first_name or ''} {self.last_name or ''}".strip()
            return f"Cliente {self.customerID}"

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
