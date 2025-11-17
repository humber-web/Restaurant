"""
SAF-T CV Export Service

Generates XML file compliant with SAF-T CV (Standard Audit File for Tax - Cabo Verde)
According to Portaria n.º 47/2021 and Decreto-Lei n.º 79/2020
"""
from datetime import datetime, date
from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from django.contrib.auth.models import User
from apps.common.models import CompanySettings
from apps.payments.models import Payment
from apps.orders.models import Order
from apps.menu.models import MenuItem
from apps.inventory.models import InventoryItem

# Import new models (with try/except for backwards compatibility)
try:
    from apps.customers.models import Customer
except ImportError:
    Customer = None

try:
    from apps.suppliers.models import Supplier
except ImportError:
    Supplier = None


class SAFTExportService:
    """
    Service to export data in SAF-T CV format.
    """

    def __init__(self, start_date: date, end_date: date):
        """
        Initialize SAF-T export for a date range.

        Args:
            start_date: Start date for export
            end_date: End date for export
        """
        self.start_date = start_date
        self.end_date = end_date
        self.company_settings = CompanySettings.get_instance()

    def generate_saft_xml(self) -> str:
        """
        Generate complete SAF-T CV XML.

        Returns:
            str: XML string
        """
        # Create root element
        audit_file = Element('AuditFile')
        audit_file.set('xmlns', 'urn:OECD:Standard:AuditFile-CV:PT_1.04_01')

        # Add Header
        self._add_header(audit_file)

        # Add Master Files
        master_files = SubElement(audit_file, 'MasterFiles')
        self._add_customers(master_files)
        self._add_suppliers(master_files)
        self._add_products(master_files)
        self._add_tax_table(master_files)

        # Add Source Documents
        source_documents = SubElement(audit_file, 'SourceDocuments')
        self._add_sales_invoices(source_documents)

        # Convert to pretty XML string
        return self._prettify_xml(audit_file)

    def _add_header(self, parent: Element):
        """Add Header section"""
        header = SubElement(parent, 'Header')

        # Audit File Version
        SubElement(header, 'AuditFileVersion').text = '1.04_01'

        # Company Info
        SubElement(header, 'CompanyID').text = self.company_settings.tax_registration_number
        SubElement(header, 'TaxRegistrationNumber').text = self.company_settings.tax_registration_number
        SubElement(header, 'TaxAccountingBasis').text = 'F'  # F=Facturação, C=Caixa
        SubElement(header, 'CompanyName').text = self.company_settings.company_name

        # Address
        company_address = SubElement(header, 'CompanyAddress')
        SubElement(company_address, 'StreetName').text = self.company_settings.street_name
        if self.company_settings.building_number:
            SubElement(company_address, 'Number').text = self.company_settings.building_number
        SubElement(company_address, 'City').text = self.company_settings.city
        SubElement(company_address, 'PostalCode').text = self.company_settings.postal_code
        SubElement(company_address, 'Country').text = 'CV'

        # Fiscal Year
        SubElement(header, 'FiscalYear').text = str(self.start_date.year)

        # Date Range
        SubElement(header, 'StartDate').text = self.start_date.strftime('%Y-%m-%d')
        SubElement(header, 'EndDate').text = self.end_date.strftime('%Y-%m-%d')

        # Currency Code (always CVE for Cabo Verde)
        SubElement(header, 'CurrencyCode').text = 'CVE'

        # Date Created
        SubElement(header, 'DateCreated').text = datetime.now().strftime('%Y-%m-%d')

        # Software Certificate Number
        SubElement(header, 'SoftwareCertificateNumber').text = self.company_settings.software_certificate_number
        SubElement(header, 'ProductID').text = f'Restaurant ERP/{self.company_settings.software_version}'
        SubElement(header, 'ProductCompanyTaxID').text = self.company_settings.tax_registration_number

    def _add_customers(self, parent: Element):
        """Add Customer table (SAF-T CV compliant)"""
        # Use new Customer model if available, otherwise fallback to User profiles
        if Customer:
            customers_list = Customer.objects.filter(is_active=True)

            for cust in customers_list:
                customer = SubElement(parent, 'Customer')
                SubElement(customer, 'CustomerID').text = str(cust.customerID)
                SubElement(customer, 'AccountID').text = f'CLI-{cust.customerID}'
                SubElement(customer, 'CustomerTaxID').text = cust.tax_id
                SubElement(customer, 'CompanyName').text = cust.full_name

                # Billing Address
                billing_address = SubElement(customer, 'BillingAddress')
                if cust.street_name:
                    address_text = cust.street_name
                    if cust.building_number:
                        address_text += f", Nº {cust.building_number}"
                    SubElement(billing_address, 'AddressDetail').text = address_text
                if cust.city:
                    SubElement(billing_address, 'City').text = cust.city
                if cust.postal_code:
                    SubElement(billing_address, 'PostalCode').text = cust.postal_code
                SubElement(billing_address, 'Country').text = cust.country or 'CV'

                # Contact
                SubElement(customer, 'Telephone').text = cust.telephone or 'N/A'
                if cust.email:
                    SubElement(customer, 'Email').text = cust.email

                # Self-billing indicator
                SubElement(customer, 'SelfBillingIndicator').text = '0'
        else:
            # Fallback to old User profile method
            customers_list = User.objects.filter(profile__isnull=False).select_related('profile')

            for user in customers_list:
                customer = SubElement(parent, 'Customer')
                SubElement(customer, 'CustomerID').text = str(user.id)
                SubElement(customer, 'AccountID').text = f'CLI-{user.id}'

                if hasattr(user, 'profile') and user.profile.tax_id:
                    SubElement(customer, 'CustomerTaxID').text = user.profile.tax_id

                customer_name = f"{user.first_name} {user.last_name}".strip() or user.username
                SubElement(customer, 'CompanyName').text = customer_name
                SubElement(customer, 'Telephone').text = 'N/A'
                SubElement(customer, 'SelfBillingIndicator').text = '0'

        # Add "Consumidor Final" for anonymous sales (required by SAF-T CV)
        consumer_final = SubElement(parent, 'Customer')
        SubElement(consumer_final, 'CustomerID').text = 'FINAL'
        SubElement(consumer_final, 'AccountID').text = 'CLI-FINAL'
        SubElement(consumer_final, 'CustomerTaxID').text = '999999999'
        SubElement(consumer_final, 'CompanyName').text = 'Consumidor Final'

        # Minimal address for Consumidor Final
        billing_address = SubElement(consumer_final, 'BillingAddress')
        SubElement(billing_address, 'AddressDetail').text = 'N/A'
        SubElement(billing_address, 'City').text = 'N/A'
        SubElement(billing_address, 'PostalCode').text = '0000'
        SubElement(billing_address, 'Country').text = 'CV'

        SubElement(consumer_final, 'Telephone').text = 'N/A'
        SubElement(consumer_final, 'SelfBillingIndicator').text = '0'

    def _add_products(self, parent: Element):
        """Add Product table"""
        products = MenuItem.objects.all()

        for product in products:
            product_elem = SubElement(parent, 'Product')
            SubElement(product_elem, 'ProductType').text = 'P'  # P=Produto, S=Serviço
            SubElement(product_elem, 'ProductCode').text = str(product.itemID)
            SubElement(product_elem, 'ProductDescription').text = product.name
            SubElement(product_elem, 'ProductNumberCode').text = str(product.itemID)

    def _add_tax_table(self, parent: Element):
        """Add Tax Table (IVA rates)"""
        tax_table = SubElement(parent, 'TaxTable')

        # IVA Normal (15%)
        tax_entry = SubElement(tax_table, 'TaxTableEntry')
        SubElement(tax_entry, 'TaxType').text = 'IVA'
        SubElement(tax_entry, 'TaxCountryRegion').text = 'CV'
        SubElement(tax_entry, 'TaxCode').text = 'NOR'
        SubElement(tax_entry, 'Description').text = 'IVA Normal'
        SubElement(tax_entry, 'TaxPercentage').text = '15.00'

    def _add_sales_invoices(self, parent: Element):
        """Add Sales Invoices"""
        sales_invoices = SubElement(parent, 'SalesInvoices')

        # Get all signed payments (invoices) in the date range
        payments = Payment.objects.filter(
            is_signed=True,
            invoice_date__gte=self.start_date,
            invoice_date__lte=self.end_date
        ).select_related('order').order_by('invoice_date', 'invoice_no')

        # Number of entries
        SubElement(sales_invoices, 'NumberOfEntries').text = str(payments.count())

        # Total Debit and Credit
        total_debit = sum(p.order.grandTotal for p in payments)
        SubElement(sales_invoices, 'TotalDebit').text = f"{float(total_debit):.2f}"
        SubElement(sales_invoices, 'TotalCredit').text = '0.00'

        # Add each invoice
        for payment in payments:
            self._add_invoice(sales_invoices, payment)

    def _add_invoice(self, parent: Element, payment: Payment):
        """Add individual invoice (SAF-T CV compliant)"""
        invoice = SubElement(parent, 'Invoice')

        # Invoice Number
        SubElement(invoice, 'InvoiceNo').text = payment.invoice_no

        # Invoice Type
        invoice_type_map = {
            'FT': 'FT',  # Fatura
            'NC': 'NC',  # Nota de Crédito
            'TV': 'TV',  # Talão de Venda
            'FR': 'FR',  # Fatura Recibo
        }
        SubElement(invoice, 'InvoiceType').text = invoice_type_map.get(payment.invoice_type, 'FT')

        # Invoice Date
        SubElement(invoice, 'InvoiceDate').text = payment.invoice_date.strftime('%Y-%m-%d')

        # SystemEntryDate (data de entrada no sistema)
        SubElement(invoice, 'SystemEntryDate').text = payment.created_at.strftime('%Y-%m-%dT%H:%M:%S')

        # Customer ID
        customer_id = str(payment.order.customer.id) if payment.order.customer else 'FINAL'
        SubElement(invoice, 'CustomerID').text = customer_id

        # Credit Note specific fields: References to original document
        if payment.invoice_type == 'NC' and hasattr(payment, 'referenced_document') and payment.referenced_document:
            doc_ref = SubElement(invoice, 'DocumentReference')
            SubElement(doc_ref, 'InvoiceNo').text = payment.referenced_document.invoice_no
            if payment.referenced_document.invoice_date:
                SubElement(doc_ref, 'InvoiceDate').text = payment.referenced_document.invoice_date.strftime('%Y-%m-%d')

            # Issue Reason Code (M01-M05, M99)
            if hasattr(payment, 'credit_note_reason') and payment.credit_note_reason:
                SubElement(invoice, 'IssueReasonCode').text = payment.credit_note_reason

        # Lines (Order Items)
        order_items = payment.order.items.all()
        for idx, item in enumerate(order_items, start=1):
            line = SubElement(invoice, 'Line')
            SubElement(line, 'LineNumber').text = str(idx)
            SubElement(line, 'ProductCode').text = str(item.menu_item.itemID)
            SubElement(line, 'ProductDescription').text = item.menu_item.name
            SubElement(line, 'Quantity').text = str(item.quantity)
            SubElement(line, 'UnitOfMeasure').text = 'UN'
            SubElement(line, 'UnitPrice').text = f"{float(item.price):.2f}"
            SubElement(line, 'TaxPointDate').text = payment.invoice_date.strftime('%Y-%m-%d')

            # Tax (IVA)
            SubElement(line, 'TaxType').text = 'IVA'
            SubElement(line, 'TaxCountryRegion').text = 'CV'
            SubElement(line, 'TaxCode').text = 'NOR'
            SubElement(line, 'TaxPercentage').text = '15.00'

            # Amounts (always positive in SAF-T)
            line_total = abs(float(item.price * item.quantity))
            SubElement(line, 'CreditAmount').text = f"{line_total:.2f}"

        # Document Totals
        doc_totals = SubElement(invoice, 'DocumentTotals')
        SubElement(doc_totals, 'TaxPayable').text = f"{abs(float(payment.order.totalIva)):.2f}"
        SubElement(doc_totals, 'NetTotal').text = f"{abs(float(payment.order.totalAmount)):.2f}"
        SubElement(doc_totals, 'GrossTotal').text = f"{abs(float(payment.order.grandTotal)):.2f}"

        # Payment Methods (if applicable)
        if payment.payment_method:
            payment_mech = SubElement(invoice, 'PaymentMechanism')
            payment_method_map = {
                'CASH': 'NU',           # Numerário (Cash)
                'CREDIT_CARD': 'CC',    # Cartão de Crédito
                'DEBIT_CARD': 'CD',     # Cartão de Débito
                'ONLINE': 'TB',         # Transferência Bancária
            }
            SubElement(payment_mech, 'PaymentMechanismType').text = payment_method_map.get(payment.payment_method, 'OU')
            SubElement(payment_mech, 'PaymentAmount').text = f"{abs(float(payment.amount)):.2f}"
            if payment.payment_method in ['CREDIT_CARD', 'DEBIT_CARD'] and payment.transaction_id:
                SubElement(payment_mech, 'TransactionID').text = payment.transaction_id

        # Hash (fiscal signature)
        if payment.invoice_hash:
            SubElement(invoice, 'Hash').text = payment.invoice_hash
            SubElement(invoice, 'HashControl').text = payment.software_certificate_number or '0'

            # Previous Hash (hash chain integrity)
            if payment.previous_invoice_hash:
                SubElement(invoice, 'PreviousHash').text = payment.previous_invoice_hash

    def _prettify_xml(self, elem: Element) -> str:
        """Return a pretty-printed XML string"""
        rough_string = tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')

    @staticmethod
    def export_to_file(start_date: date, end_date: date, file_path: str):
        """
        Export SAF-T to file.

        Args:
            start_date: Start date
            end_date: End date
            file_path: Output file path

        Returns:
            str: File path
        """
        service = SAFTExportService(start_date, end_date)
        xml_content = service.generate_saft_xml()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        return file_path

    def _add_suppliers(self, parent: Element):
        """Add Supplier table (SAF-T CV compliant)"""
        if not Supplier:
            return  # Skip if Supplier model not available

        suppliers_list = Supplier.objects.filter(is_active=True)

        for supp in suppliers_list:
            supplier = SubElement(parent, 'Supplier')
            SubElement(supplier, 'SupplierID').text = str(supp.supplierID)
            SubElement(supplier, 'AccountID').text = f'FOR-{supp.supplierID}'
            SubElement(supplier, 'SupplierTaxID').text = supp.tax_id
            SubElement(supplier, 'CompanyName').text = supp.company_name

            # Billing Address
            billing_address = SubElement(supplier, 'BillingAddress')
            if supp.street_name:
                address_text = supp.street_name
                if supp.building_number:
                    address_text += f", Nº {supp.building_number}"
                SubElement(billing_address, 'AddressDetail').text = address_text
            if supp.city:
                SubElement(billing_address, 'City').text = supp.city
            if supp.postal_code:
                SubElement(billing_address, 'PostalCode').text = supp.postal_code
            SubElement(billing_address, 'Country').text = supp.country or 'CV'

            # Contact
            SubElement(supplier, 'Telephone').text = supp.telephone or 'N/A'
            if supp.email:
                SubElement(supplier, 'Email').text = supp.email

            # Contact Person (optional but useful)
            if supp.contact_person:
                SubElement(supplier, 'Contact').text = supp.contact_person

            # Self-billing indicator
            SubElement(supplier, 'SelfBillingIndicator').text = '0'
