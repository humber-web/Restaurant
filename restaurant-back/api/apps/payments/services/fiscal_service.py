"""
Fiscal Service for SAF-T CV / e-Fatura Compliance

This service handles:
- Invoice numbering (sequential)
- Hash generation (SHA-256 chain)
- IUD generation (Unique Document Identifier)
- Digital signature
"""
import hashlib
from datetime import date, datetime
from django.db import transaction
from apps.common.models import CompanySettings


class FiscalService:
    """
    Service for fiscal compliance operations.
    """

    @staticmethod
    def generate_invoice_number(invoice_type='FT'):
        """
        Generate sequential invoice number in format: SÉRIE/ANO/NÚMERO
        Example: FT A/2025/00001

        Args:
            invoice_type: Type of invoice ('FT', 'NC', 'TV', 'FR')

        Returns:
            str: Invoice number like "FT A/2025/00001"
        """
        from apps.payments.models import Payment

        company_settings = CompanySettings.get_instance()

        # Get series based on invoice type
        series_map = {
            'FT': company_settings.invoice_series,
            'NC': company_settings.credit_note_series,
            'TV': company_settings.receipt_series,
            'FR': company_settings.invoice_series,  # Same as FT
        }
        series = series_map.get(invoice_type, 'FT A')

        # Get current year
        current_year = date.today().year

        # Find last invoice number for this series/year
        last_payment = Payment.objects.filter(
            invoice_no__startswith=f"{series}/{current_year}/",
            invoice_type=invoice_type
        ).order_by('-invoice_no').first()

        if last_payment and last_payment.invoice_no:
            # Extract number from last invoice (e.g., "FT A/2025/00123" -> 123)
            parts = last_payment.invoice_no.split('/')
            if len(parts) == 3:
                try:
                    last_number = int(parts[2])
                    next_number = last_number + 1
                except ValueError:
                    next_number = 1
            else:
                next_number = 1
        else:
            next_number = 1

        # Format: SÉRIE/ANO/NÚMERO (5 digits, zero-padded)
        invoice_no = f"{series}/{current_year}/{next_number:05d}"

        return invoice_no

    @staticmethod
    def calculate_invoice_hash(payment):
        """
        Calculate SHA-256 hash for invoice integrity.
        Hash is calculated from: invoice_date + invoice_no + grand_total + previous_hash

        For the first invoice, previous_hash is empty string ''.

        Args:
            payment: Payment instance

        Returns:
            str: SHA-256 hash (64 characters)
        """
        # Get data for hash calculation
        invoice_date_str = payment.invoice_date.strftime('%Y-%m-%d') if payment.invoice_date else ''
        invoice_no = payment.invoice_no or ''
        grand_total_str = f"{float(payment.order.grandTotal):.2f}"
        previous_hash = payment.previous_invoice_hash if payment.previous_invoice_hash else ''

        # Concatenate for hash (first invoice will have empty previous_hash)
        hash_string = f"{invoice_date_str}{invoice_no}{grand_total_str}{previous_hash}"

        # Calculate SHA-256
        hash_object = hashlib.sha256(hash_string.encode('utf-8'))
        invoice_hash = hash_object.hexdigest()

        return invoice_hash

    @staticmethod
    def get_previous_invoice_hash(invoice_type='FT'):
        """
        Get the hash of the previous invoice (for hash chaining).

        For the FIRST invoice, returns empty string '' which is the standard
        for starting a hash chain in SAF-T CV.

        Args:
            invoice_type: Type of invoice

        Returns:
            str: Previous invoice hash, or empty string for first invoice
        """
        from apps.payments.models import Payment

        # Find last signed invoice of this type
        last_payment = Payment.objects.filter(
            invoice_type=invoice_type,
            is_signed=True,
            invoice_hash__isnull=False
        ).order_by('-invoice_date', '-paymentID').first()

        if last_payment:
            return last_payment.invoice_hash

        # First invoice: use empty string as previous hash
        return ''

    @staticmethod
    def generate_iud(payment):
        """
        Generate IUD (Identificador Único do Documento) - 45 characters
        Format: País + Data + NIF + Tipo + Série/Número

        Args:
            payment: Payment instance

        Returns:
            str: IUD (45 characters)
        """
        company_settings = CompanySettings.get_instance()

        # Components
        country = 'CV'  # Cabo Verde
        date_str = payment.invoice_date.strftime('%Y%m%d') if payment.invoice_date else datetime.now().strftime('%Y%m%d')
        nif = company_settings.tax_registration_number.zfill(9)[:9]  # 9 digits
        doc_type = payment.invoice_type  # FT, NC, TV, FR
        invoice_no_clean = payment.invoice_no.replace('/', '').replace(' ', '') if payment.invoice_no else ''

        # Combine and hash to ensure fixed length
        iud_string = f"{country}{date_str}{nif}{doc_type}{invoice_no_clean}"
        iud_hash = hashlib.sha256(iud_string.encode('utf-8')).hexdigest()

        # Take first 45 characters (standard for IUD)
        iud = iud_hash[:45].upper()

        return iud

    @staticmethod
    @transaction.atomic
    def sign_invoice(payment):
        """
        Sign an invoice (generate all fiscal fields and mark as signed).
        This makes the invoice legally valid and immutable.

        Args:
            payment: Payment instance

        Returns:
            Payment: Updated payment with fiscal fields
        """
        company_settings = CompanySettings.get_instance()

        # 1. Generate invoice number
        if not payment.invoice_no:
            payment.invoice_no = FiscalService.generate_invoice_number(payment.invoice_type)

        # 2. Set invoice date
        if not payment.invoice_date:
            payment.invoice_date = date.today()

        # 3. Get previous invoice hash (for chain)
        payment.previous_invoice_hash = FiscalService.get_previous_invoice_hash(payment.invoice_type)

        # 4. Calculate invoice hash
        payment.invoice_hash = FiscalService.calculate_invoice_hash(payment)

        # 5. Set hash algorithm
        payment.hash_algorithm = 'SHA256'

        # 6. Generate IUD
        payment.iud = FiscalService.generate_iud(payment)

        # 7. Set software certificate number
        payment.software_certificate_number = company_settings.software_certificate_number

        # 8. Mark as signed
        payment.is_signed = True
        payment.signed_at = datetime.now()

        # 9. Save payment
        payment.save()

        return payment

    @staticmethod
    def validate_hash_chain(payment):
        """
        Validate that the invoice hash chain is intact.

        Args:
            payment: Payment instance

        Returns:
            bool: True if hash chain is valid
        """
        # Recalculate hash
        calculated_hash = FiscalService.calculate_invoice_hash(payment)

        # Compare with stored hash
        return calculated_hash == payment.invoice_hash
