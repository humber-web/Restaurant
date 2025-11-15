"""
e-Fatura CV Service

Generates individual invoice XML for real-time submission to DNRE e-Fatura platform.
Conforms to CV_EFatura_Invoice_v1.0.xsd schema.

IMPORTANT: Currently in SIMULATION mode.
When DNRE credentials are available, update DNRE_API_ENABLED to True.
"""
import os
from datetime import datetime
from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom
from django.conf import settings
from apps.common.models import CompanySettings
from apps.payments.models import Payment


# Configuration
DNRE_API_ENABLED = False  # Set to True when DNRE credentials available
EFATURA_STORAGE_DIR = os.path.join(settings.BASE_DIR, 'efatura_xml')


class EFaturaService:
    """
    Service to generate e-Fatura CV compliant XML for individual invoices.
    """

    # Document type codes (DNRE official)
    DOCUMENT_TYPE_CODES = {
        'FT': '1',   # Fatura (Invoice)
        'FR': '2',   # Fatura Recibo (Invoice Receipt)
        'TV': '3',   # Talão de Venda (Sales Receipt)
        'NC': '5',   # Nota de Crédito (Credit Note)
    }

    def __init__(self, payment: Payment):
        """
        Initialize e-Fatura service for a payment/invoice.

        Args:
            payment: Payment instance (must be signed)
        """
        if not payment.is_signed:
            raise ValueError("Payment must be signed before generating e-Fatura XML")

        self.payment = payment
        self.order = payment.order
        self.company = CompanySettings.get_instance()

        # Ensure storage directory exists
        os.makedirs(EFATURA_STORAGE_DIR, exist_ok=True)

    def generate_iud(self) -> str:
        """
        Generate IUD (Identificador Único do Documento) - 45 characters.
        Format: CV + DocumentTypeCode + IssueDate + TaxId + Serie + Number

        Returns:
            str: IUD (45 characters)
        """
        # If already exists, use it
        if self.payment.iud:
            return self.payment.iud

        # Components
        country = 'CV'
        doc_type_code = self.DOCUMENT_TYPE_CODES.get(self.payment.invoice_type, '1')
        issue_date = self.payment.invoice_date.strftime('%Y%m%d')
        tax_id = self.company.tax_registration_number.zfill(9)[:9]

        # Series and number from invoice_no (e.g., "FT A/2025/00001")
        if self.payment.invoice_no:
            parts = self.payment.invoice_no.replace(' ', '').split('/')
            if len(parts) >= 3:
                serie = parts[0]  # "FTA"
                number = parts[2].zfill(9)[:9]  # "000000001"
            else:
                serie = 'FTA'
                number = '000000001'
        else:
            serie = 'FTA'
            number = '000000001'

        # Combine to form IUD (exactly 45 characters)
        # Format: CV + TypeCode(1) + Date(8) + TaxId(9) + Serie(max 10) + Number(9)
        iud = f"{country}{doc_type_code}{issue_date}{tax_id}{serie}{number}"

        # Pad or truncate to exactly 45 characters
        iud = iud[:45].ljust(45, '0')

        return iud

    def generate_xml(self) -> str:
        """
        Generate e-Fatura XML conforming to CV_EFatura_Invoice_v1.0.xsd.

        Returns:
            str: XML string (UTF-8)
        """
        # Root element
        dfe = Element('Dfe')
        dfe.set('xmlns', 'urn:cv:efatura:xsd:v1.0')
        dfe.set('Version', '1.0')
        dfe.set('Id', self.generate_iud())
        dfe.set('DocumentTypeCode', self.DOCUMENT_TYPE_CODES.get(self.payment.invoice_type, '1'))
        dfe.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        dfe.set('xsi:schemaLocation', 'urn:cv:efatura:xsd:v1.0 common/CV_EFatura_Invoice_v1.0.xsd')

        # Specimen mode (test mode)
        SubElement(dfe, 'IsSpecimen').text = 'true' if not DNRE_API_ENABLED else 'false'

        # Invoice element
        invoice = SubElement(dfe, 'Invoice')

        # Document identification
        SubElement(invoice, 'LedCode').text = '1'  # Ledger code (1 = normal)

        # Extract serie from invoice_no
        if self.payment.invoice_no:
            parts = self.payment.invoice_no.split('/')
            serie = parts[0].strip() if len(parts) >= 1 else 'FT A'
            doc_number = parts[2].strip() if len(parts) >= 3 else '00001'
        else:
            serie = 'FT A'
            doc_number = '00001'

        SubElement(invoice, 'Serie').text = serie
        SubElement(invoice, 'DocumentNumber').text = doc_number

        # Dates
        issue_date = self.payment.invoice_date or datetime.now().date()
        SubElement(invoice, 'IssueDate').text = issue_date.strftime('%Y-%m-%d')
        SubElement(invoice, 'IssueTime').text = self.payment.created_at.strftime('%H:%M:%S')

        # Due date (same as issue for immediate payment)
        SubElement(invoice, 'DueDate').text = issue_date.strftime('%Y-%m-%d')

        # Tax point date
        SubElement(invoice, 'TaxPointDate').text = issue_date.strftime('%Y-%m-%d')

        # Emitter (Company)
        self._add_emitter_party(invoice)

        # Receiver (Customer)
        self._add_receiver_party(invoice)

        # Lines (Order items)
        self._add_lines(invoice)

        # Totals
        self._add_totals(invoice)

        # Payments
        self._add_payments(invoice)

        # Software info
        self._add_software(invoice)

        # Convert to pretty XML string
        return self._prettify_xml(dfe)

    def _add_emitter_party(self, parent: Element):
        """Add EmitterParty (company info)"""
        emitter = SubElement(parent, 'EmitterParty')

        # Tax ID
        tax_id = SubElement(emitter, 'TaxId')
        tax_id.set('CountryCode', 'CV')
        tax_id.text = self.company.tax_registration_number

        # Name
        SubElement(emitter, 'Name').text = self.company.company_name

        # Address
        address = SubElement(emitter, 'Address')
        address.set('CountryCode', 'CV')

        # Address detail (concatenate street and number)
        address_detail = f"{self.company.street_name}"
        if self.company.building_number:
            address_detail += f", {self.company.building_number}"
        address_detail += f", {self.company.city}, {self.company.postal_code}"

        SubElement(address, 'AddressDetail').text = address_detail
        SubElement(address, 'AddressCode').text = f"CV{self.company.postal_code.replace('-', '')}"

        # Contacts
        contacts = SubElement(emitter, 'Contacts')
        SubElement(contacts, 'Telephone').text = self.company.telephone
        if self.company.email:
            SubElement(contacts, 'Email').text = self.company.email
        if self.company.website:
            SubElement(contacts, 'Website').text = self.company.website

    def _add_receiver_party(self, parent: Element):
        """Add ReceiverParty (customer info)"""
        receiver = SubElement(parent, 'ReceiverParty')

        # Customer info
        if self.payment.customer_tax_id and self.payment.customer_name:
            # Real customer
            tax_id = SubElement(receiver, 'TaxId')
            tax_id.set('CountryCode', 'CV')
            tax_id.text = self.payment.customer_tax_id
            SubElement(receiver, 'Name').text = self.payment.customer_name
        else:
            # Consumidor Final
            tax_id = SubElement(receiver, 'TaxId')
            tax_id.set('CountryCode', 'CV')
            tax_id.text = '999999999'
            SubElement(receiver, 'Name').text = 'Consumidor Final'

        # Address (minimal for consumer)
        address = SubElement(receiver, 'Address')
        address.set('CountryCode', 'CV')
        SubElement(address, 'AddressDetail').text = 'N/A'
        SubElement(address, 'AddressCode').text = 'CV0000000000'

        # Contacts (minimal)
        contacts = SubElement(receiver, 'Contacts')
        SubElement(contacts, 'Telephone').text = 'N/A'

    def _add_lines(self, parent: Element):
        """Add Lines (order items)"""
        lines = SubElement(parent, 'Lines')

        for idx, item in enumerate(self.order.items.all(), start=1):
            line = SubElement(lines, 'Line')
            line.set('LineTypeCode', 'N')  # N = Normal line

            # Line ID
            SubElement(line, 'Id').text = str(idx)

            # Quantity
            quantity = SubElement(line, 'Quantity')
            quantity.set('UnitCode', 'UN')  # UN = Unit
            quantity.set('IsStandardUnitCode', 'true')
            quantity.text = str(item.quantity)

            # Price (unit price)
            SubElement(line, 'Price').text = f"{float(item.price):.2f}"

            # Price Extension (quantity * price) - Keep as Decimal for calculations
            price_extension = item.price * item.quantity
            SubElement(line, 'PriceExtension').text = f"{float(price_extension):.2f}"

            # Net Total (same as price extension for simple case)
            SubElement(line, 'NetTotal').text = f"{float(price_extension):.2f}"

            # Tax (IVA 15%)
            tax = SubElement(line, 'Tax')
            tax.set('TaxTypeCode', 'IVA')
            SubElement(tax, 'TaxPercentage').text = '15.00'

            # Calculate tax amount (keep as Decimal)
            tax_amount = price_extension * Decimal('0.15')
            SubElement(tax, 'TaxTotal').text = f"{float(tax_amount):.2f}"

            # Item description
            item_elem = SubElement(line, 'Item')
            SubElement(item_elem, 'Description').text = item.menu_item.name
            SubElement(item_elem, 'EmitterIdentification').text = str(item.menu_item.itemID)

    def _add_totals(self, parent: Element):
        """Add Totals section"""
        totals = SubElement(parent, 'Totals')

        # Tax Total (IVA)
        SubElement(totals, 'TaxTotal').text = f"{float(self.order.totalIva):.2f}"

        # Net Total (without tax)
        SubElement(totals, 'NetTotal').text = f"{float(self.order.totalAmount):.2f}"

        # Grand Total (with tax)
        SubElement(totals, 'GrandTotal').text = f"{float(self.order.grandTotal):.2f}"

    def _add_payments(self, parent: Element):
        """Add Payments section"""
        payments = SubElement(parent, 'Payments')

        payment_elem = SubElement(payments, 'Payment')

        # Payment means code
        payment_means_map = {
            'CASH': '10',          # Cash
            'CREDIT_CARD': '48',   # Credit card
            'DEBIT_CARD': '49',    # Debit card
            'ONLINE': '30',        # Credit transfer
        }
        means_code = payment_means_map.get(self.payment.payment_method, '10')
        SubElement(payment_elem, 'PaymentMeansCode').text = means_code

        # Payment amount
        SubElement(payment_elem, 'PaymentAmount').text = f"{float(self.payment.amount):.2f}"

        # Is paid
        is_paid = 'true' if self.payment.payment_status == 'COMPLETED' else 'false'
        SubElement(payment_elem, 'IsPaid').text = is_paid

    def _add_software(self, parent: Element):
        """Add Software information"""
        software = SubElement(parent, 'Software')
        SubElement(software, 'Code').text = self.company.software_certificate_number
        SubElement(software, 'Name').text = 'Restaurant ERP'
        SubElement(software, 'Version').text = self.company.software_version

    def _prettify_xml(self, elem: Element) -> str:
        """Return a pretty-printed XML string"""
        rough_string = tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')

    def save_xml(self) -> str:
        """
        Save XML to local storage (simulation mode).

        Returns:
            str: File path where XML was saved
        """
        xml_content = self.generate_xml()

        # Generate filename
        filename = f"efatura_{self.payment.invoice_type}_{self.payment.invoice_no.replace('/', '_')}_{self.payment.invoice_date}.xml"
        file_path = os.path.join(EFATURA_STORAGE_DIR, filename)

        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        return file_path

    def submit_to_dnre(self) -> dict:
        """
        Submit invoice XML to DNRE e-Fatura platform.

        SIMULATION MODE: Currently saves locally instead of sending.
        When DNRE credentials are available, implement actual API call.

        Returns:
            dict: Response with status and details
        """
        if not DNRE_API_ENABLED:
            # Simulation mode - save locally
            file_path = self.save_xml()

            return {
                'success': True,
                'mode': 'simulation',
                'message': 'XML saved locally (simulation mode)',
                'file_path': file_path,
                'invoice_no': self.payment.invoice_no,
                'iud': self.generate_iud(),
            }
        else:
            # TODO: Implement actual DNRE API call
            # DNRE API endpoints:
            # - POST /v1/dfe/invoice/submit
            # - Headers: Authorization, Content-Type: application/xml
            # - Body: XML string

            raise NotImplementedError("DNRE API integration not yet implemented. Set credentials first.")

    @staticmethod
    def validate_xml(xml_string: str) -> bool:
        """
        Validate XML against XSD schema.

        TODO: Implement XSD validation using lxml

        Args:
            xml_string: XML to validate

        Returns:
            bool: True if valid
        """
        # TODO: Implement with lxml
        # from lxml import etree
        # schema = etree.XMLSchema(file='2024-05-27-XML-XSD/common/CV_EFatura_Invoice_v1.0.xsd')
        # doc = etree.fromstring(xml_string.encode('utf-8'))
        # return schema.validate(doc)

        return True  # Placeholder
