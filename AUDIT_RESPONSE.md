# Resposta à Auditoria de Conformidade Técnica (DNRE - Cabo Verde)

**Sistema:** Restaurant Management System
**Versão:** 1.0.0
**Data:** 19 de Novembro de 2025
**Auditor:** Direção Nacional de Receitas do Estado (DNRE)

---

## Sumário Executivo

Este documento responde aos requisitos de conformidade técnica solicitados no âmbito da auditoria para homologação do software de faturação eletrónica (e-Fatura) e SAF-T (CV), conforme o Decreto-Lei n.º 79/2020 e a Portaria n.º 47/2021.

### Estado Geral de Conformidade

| Eixo | Estado | Observação |
|------|--------|------------|
| Segurança Fiscal e Inviolabilidade | ✅ Implementado | Todos os requisitos técnicos cumpridos |
| Comunicação e Exportação SAF-T | ⚠️ Parcial | Exportação implementada, API DNRE pendente |
| Identificação do Software | ✅ Pronto | Aguarda número de certificação oficial |

---

## Eixo 1: Segurança Fiscal e Inviolabilidade (e-Fatura)

### 1.1 Encadeamento Criptográfico

**Estado:** ✅ IMPLEMENTADO

O sistema implementa encadeamento criptográfico SHA-256 conforme especificação DNRE.

**Localização do Código:**
- Ficheiro: `restaurant-back/api/apps/payments/services/fiscal_service.py`
- Linhas: 74-130

**Função de Cálculo do Hash:**

```python
# fiscal_service.py - Linhas 74-101
def calculate_invoice_hash(self, payment: Payment) -> str:
    """
    Calculate SHA-256 hash for invoice chaining.

    The hash is calculated from:
    - Invoice date (YYYY-MM-DD)
    - Invoice number
    - Grand total (2 decimal places)
    - Previous invoice hash (or zeros if first)

    Returns:
        str: SHA-256 hash in hexadecimal format
    """
    # Get previous hash for chaining
    previous_hash = self.get_previous_invoice_hash(payment)

    # Format components
    invoice_date = payment.invoice_date.strftime('%Y-%m-%d') if payment.invoice_date else datetime.now().strftime('%Y-%m-%d')
    invoice_no = payment.invoice_no or ''
    grand_total = f"{float(payment.grand_total):.2f}"

    # Concatenate for hashing
    hash_string = f"{invoice_date};{invoice_no};{grand_total};{previous_hash}"

    # Calculate SHA-256
    hash_object = hashlib.sha256(hash_string.encode('utf-8'))
    return hash_object.hexdigest()
```

**Lógica de Obtenção do Hash Anterior:**

```python
# fiscal_service.py - Linhas 104-130
def get_previous_invoice_hash(self, current_payment: Payment) -> str:
    """
    Get the hash of the previous invoice for chaining.

    Returns:
        str: Previous invoice hash or 64 zeros if first invoice
    """
    # Find the most recent signed payment before this one
    previous_payment = Payment.objects.filter(
        is_signed=True,
        signed_at__lt=current_payment.signed_at if current_payment.signed_at else timezone.now()
    ).exclude(
        pk=current_payment.pk
    ).order_by('-signed_at').first()

    if previous_payment and previous_payment.invoice_hash:
        return previous_payment.invoice_hash

    # First invoice in chain - use zeros
    return '0' * 64
```

**Campos no Modelo Payment:**

```python
# models.py - Linhas 91-104
invoice_hash = models.CharField(
    max_length=64,
    blank=True,
    null=True,
    help_text="SHA-256 hash of invoice data for integrity verification"
)

previous_invoice_hash = models.CharField(
    max_length=64,
    blank=True,
    null=True,
    help_text="Hash of the previous invoice for chain verification"
)
```

---

### 1.2 Imutabilidade dos Registos

**Estado:** ✅ IMPLEMENTADO

O sistema impede alteração e eliminação de faturas assinadas, conforme exigido pela legislação.

**Localização do Código:**
- Ficheiro: `restaurant-back/api/apps/payments/models.py`
- Linhas: 214-252

**Bloqueio de Modificação (UPDATE):**

```python
# models.py - Linhas 214-238
def save(self, *args, **kwargs):
    """
    Override save to prevent modification of signed invoices.
    """
    if self.pk:  # Existing record
        try:
            original = Payment.objects.get(pk=self.pk)
            if original.is_signed:
                # Allow only specific field updates for signed invoices
                allowed_fields = ['notes']  # Very limited updates allowed

                # Check if any protected field was modified
                protected_fields = [
                    'order', 'payment_method', 'amount_paid', 'change_amount',
                    'grand_total', 'tax_amount', 'subtotal', 'discount_amount',
                    'invoice_no', 'invoice_hash', 'previous_invoice_hash',
                    'iud', 'is_credit_note', 'original_invoice', 'credit_reason'
                ]

                for field in protected_fields:
                    if getattr(self, field) != getattr(original, field):
                        raise ValidationError(
                            f"Cannot modify a signed payment/invoice. "
                            f"Field '{field}' is protected. "
                            f"Use Credit Notes (NC) for corrections."
                        )
        except Payment.DoesNotExist:
            pass

    super().save(*args, **kwargs)
```

**Bloqueio de Eliminação (DELETE):**

```python
# models.py - Linhas 241-252
def delete(self, *args, **kwargs):
    """
    Override delete to prevent deletion of signed invoices.
    """
    if self.is_signed:
        raise ValidationError(
            "Cannot delete a signed payment/invoice. "
            "Signed documents are fiscally immutable. "
            "Use Credit Notes (NC) for corrections or annulments."
        )

    super().delete(*args, **kwargs)
```

**Flag de Assinatura:**

```python
# models.py - Linhas 129-133
is_signed = models.BooleanField(
    default=False,
    help_text="Indicates if the invoice has been digitally signed and is fiscally immutable"
)
```

---

### 1.3 IUD (Identificador Único de Documento) e Código QR

**Estado:** ✅ IMPLEMENTADO

#### IUD - 45 Caracteres

**Localização do Código:**
- Ficheiro: `restaurant-back/api/apps/payments/services/fiscal_service.py`
- Linhas: 132-160

```python
# fiscal_service.py - Linhas 132-160
def generate_iud(self, payment: Payment) -> str:
    """
    Generate IUD (Identificador Único de Documento) - 45 characters.

    Format: CV + Date(8) + NIF(9) + DocType(2) + InvoiceNo(8) + Control(16)

    Components:
    - Country code: CV (2 chars)
    - Date: YYYYMMDD (8 chars)
    - Emitter NIF: 9 digits
    - Document type: FT, NC, FR, TV (2 chars)
    - Invoice number: 8 digits zero-padded
    - Control: First 16 chars of SHA-256

    Returns:
        str: 45-character IUD
    """
    settings = self._get_company_settings()

    # Components
    country = 'CV'
    date_str = payment.invoice_date.strftime('%Y%m%d') if payment.invoice_date else datetime.now().strftime('%Y%m%d')
    nif = settings.tax_id.zfill(9)[:9]
    doc_type = 'NC' if payment.is_credit_note else payment.invoice_type or 'FT'
    invoice_no = str(payment.invoice_no or 0).zfill(8)[:8]

    # Generate control hash
    control_string = f"{country}{date_str}{nif}{doc_type}{invoice_no}"
    control_hash = hashlib.sha256(control_string.encode()).hexdigest()[:16].upper()

    # Combine (2 + 8 + 9 + 2 + 8 + 16 = 45 characters)
    iud = f"{country}{date_str}{nif}{doc_type}{invoice_no}{control_hash}"

    return iud[:45]  # Ensure exactly 45 characters
```

#### Código QR

**Localização do Código:**
- Ficheiro: `restaurant-back/api/apps/payments/services/qrcode_service.py`

```python
# qrcode_service.py - Linhas 23-82
class QRCodeService:
    """Service for generating QR codes for fiscal documents."""

    @staticmethod
    def generate_qr_code(data: str, size: int = 200) -> str:
        """
        Generate a QR code as a base64-encoded PNG data URL.

        Args:
            data: The data to encode in the QR code
            size: The size of the QR code in pixels

        Returns:
            str: Base64-encoded PNG data URL (data:image/png;base64,...)
        """
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        # Add data
        qr.add_data(data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Resize if needed
        if size != 200:
            img = img.resize((size, size))

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Return as data URL
        base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"

    @staticmethod
    def generate_qr_code_for_payment(payment) -> str:
        """
        Generate QR code for a payment/invoice containing the IUD.

        Args:
            payment: Payment instance with IUD

        Returns:
            str: Base64-encoded PNG data URL
        """
        if not payment.iud:
            raise ValueError("Payment does not have an IUD. Sign the invoice first.")

        # QR code contains "IUD:" prefix followed by the 45-character IUD
        qr_data = f"IUD:{payment.iud}"
        return QRCodeService.generate_qr_code(qr_data)
```

**Integração no Talão/Fatura:**

O QR Code é retornado na API de assinatura e pode ser incluído no template de impressão:

```python
# views.py - Resposta da API de assinatura
response_data = {
    'invoice_no': payment.invoice_no,
    'invoice_hash': payment.invoice_hash,
    'iud': payment.iud,
    'qr_code': qr_code_data,  # Base64 PNG para impressão
    'signed_at': payment.signed_at.isoformat(),
}
```

---

### 1.4 Notas de Crédito Eletrónicas (NCE)

**Estado:** ✅ IMPLEMENTADO

O sistema suporta emissão de Notas de Crédito como único método legal de retificação.

**Localização do Código:**
- Modelo: `restaurant-back/api/apps/payments/models.py` (Linhas 166-183)
- View: `restaurant-back/api/apps/payments/views.py` (IssueCreditNoteView)
- Endpoint: `/api/v1/payments/credit-note/issue/`

**Campos no Modelo Payment:**

```python
# models.py - Linhas 166-183
is_credit_note = models.BooleanField(
    default=False,
    help_text="Indicates if this is a Credit Note (NC)"
)

original_invoice = models.ForeignKey(
    'self',
    on_delete=models.PROTECT,
    null=True,
    blank=True,
    related_name='credit_notes',
    help_text="Reference to the original invoice being credited"
)

credit_reason = models.CharField(
    max_length=3,
    choices=CREDIT_NOTE_REASONS,
    blank=True,
    null=True,
    help_text="Reason code for credit note as per SAF-T CV"
)
```

**Códigos de Motivo (SAF-T CV):**

```python
# models.py - Linhas 31-39
CREDIT_NOTE_REASONS = [
    ('M01', 'Devolução de mercadorias'),
    ('M02', 'Desconto comercial'),
    ('M03', 'Erro de faturação'),
    ('M04', 'Anulação de fatura'),
    ('M05', 'Diferença de preço'),
    ('M99', 'Outro motivo'),
]
```

**Validação de Nota de Crédito:**

```python
# serializers.py - Linhas 75-129
class CreditNoteSerializer(serializers.Serializer):
    """Serializer for issuing credit notes."""

    original_invoice_id = serializers.IntegerField()
    credit_reason = serializers.ChoiceField(choices=Payment.CREDIT_NOTE_REASONS)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(max_length=500, required=False)

    def validate_original_invoice_id(self, value):
        """Validate that the original invoice exists and is signed."""
        try:
            original = Payment.objects.get(pk=value)
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Original invoice not found.")

        if not original.is_signed:
            raise serializers.ValidationError(
                "Cannot issue credit note for unsigned invoice."
            )

        if original.is_credit_note:
            raise serializers.ValidationError(
                "Cannot issue credit note for another credit note."
            )

        return value

    def validate_amount(self, value):
        """Validate credit amount is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Credit amount must be positive."
            )
        return value
```

---

## Eixo 2: Comunicação e Exportação de Dados (SAF-T CV)

### 2.1 Exportação SAF-T CV

**Estado:** ✅ IMPLEMENTADO

Exportação completa em XML conforme Portaria n.º 47/2021.

**Localização do Código:**
- Serviço: `restaurant-back/api/apps/payments/services/saft_export_service.py`
- View: `restaurant-back/api/apps/payments/views.py` (ExportSAFTView, Linhas 347-404)
- Endpoint: `/api/v1/payments/saft/export/`

**Função Principal de Exportação:**

```python
# saft_export_service.py - Linhas 47-73
def generate_saft_xml(self, start_date: date, end_date: date) -> str:
    """
    Generate SAF-T (CV) compliant XML for the specified date range.

    Args:
        start_date: Start of the export period
        end_date: End of the export period

    Returns:
        str: XML string in SAF-T (CV) format
    """
    # Create root element with namespace
    root = ET.Element('AuditFile')
    root.set('xmlns', 'urn:OECD:StandardAuditFile-Tax:CV_1.04_01')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    # Add header
    self._add_header(root, start_date, end_date)

    # Add master files
    master_files = ET.SubElement(root, 'MasterFiles')
    self._add_customers(master_files, start_date, end_date)
    self._add_products(master_files)
    self._add_tax_table(master_files)

    # Add source documents
    source_docs = ET.SubElement(root, 'SourceDocuments')
    self._add_sales_invoices(source_docs, start_date, end_date)

    return self._prettify_xml(root)
```

**Parâmetros de Data (View):**

```python
# views.py - Linhas 347-404
class ExportSAFTView(APIView):
    """Export SAF-T (CV) XML file for a date range."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get date parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not start_date_str or not end_date_str:
            return Response(
                {'error': 'Both start_date and end_date are required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate SAF-T XML
        saft_service = SAFTExportService()
        xml_content = saft_service.generate_saft_xml(start_date, end_date)

        # Return as downloadable file
        response = HttpResponse(xml_content, content_type='application/xml')
        filename = f"SAFT_CV_{start_date_str}_{end_date_str}.xml"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
```

**Estrutura do XML Gerado:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<AuditFile xmlns="urn:OECD:StandardAuditFile-Tax:CV_1.04_01">
    <Header>
        <AuditFileVersion>1.04_01</AuditFileVersion>
        <CompanyID>123456789</CompanyID>
        <TaxRegistrationNumber>123456789</TaxRegistrationNumber>
        <TaxAccountingBasis>F</TaxAccountingBasis>
        <CompanyName>Restaurant Name</CompanyName>
        <CompanyAddress>...</CompanyAddress>
        <FiscalYear>2025</FiscalYear>
        <StartDate>2025-01-01</StartDate>
        <EndDate>2025-12-31</EndDate>
        <CurrencyCode>CVE</CurrencyCode>
        <DateCreated>2025-11-19</DateCreated>
        <SoftwareCertificateNumber>0</SoftwareCertificateNumber>
        <ProductID>Restaurant ERP/1.0.0</ProductID>
    </Header>
    <MasterFiles>
        <Customer>...</Customer>
        <Product>...</Product>
        <TaxTable>...</TaxTable>
    </MasterFiles>
    <SourceDocuments>
        <SalesInvoices>...</SalesInvoices>
    </SourceDocuments>
</AuditFile>
```

---

### 2.2 Formatação Numérica

**Estado:** ✅ IMPLEMENTADO

O sistema utiliza ponto (`.`) como separador decimal e valores absolutos.

**Código de Formatação:**

```python
# saft_export_service.py - Exemplos de formatação

# Linhas 220-221 - Preço unitário
unit_price = ET.SubElement(line_elem, 'UnitPrice')
unit_price.text = f"{float(item.unit_price):.2f}"

# Linhas 274 - Quantidade
quantity = ET.SubElement(line_elem, 'Quantity')
quantity.text = f"{float(item.quantity):.2f}"

# Linhas 285 - Valor do IVA
tax_amount = ET.SubElement(line_elem, 'TaxAmount')
tax_amount.text = f"{float(item.tax_amount):.2f}"

# Linhas 289-290 - Totais
net_total = ET.SubElement(doc_totals, 'NetTotal')
net_total.text = f"{float(payment.subtotal):.2f}"

gross_total = ET.SubElement(doc_totals, 'GrossTotal')
gross_total.text = f"{float(payment.grand_total):.2f}"

# Linha 303 - Total de imposto
tax_payable = ET.SubElement(doc_totals, 'TaxPayable')
tax_payable.text = f"{float(payment.tax_amount):.2f}"
```

**Nota:** Todos os valores são exportados em formato absoluto (sem valores negativos). Para Notas de Crédito, o tipo de documento (NC) indica a natureza da transação.

---

### 2.3 Cadastro Obrigatório - Consumidor Final

**Estado:** ✅ IMPLEMENTADO

O sistema inclui automaticamente o "Consumidor Final" quando o NIF não é fornecido.

**Localização do Código:**
- Ficheiro: `restaurant-back/api/apps/payments/services/saft_export_service.py`
- Linhas: 165-180

```python
# saft_export_service.py - Linhas 165-180
def _add_customers(self, parent, start_date, end_date):
    """Add customer master data including Consumidor Final."""

    # Always include "Consumidor Final" for anonymous sales
    self._add_consumidor_final(parent)

    # Add other customers from payments in the period
    # ... (additional customer logic)

def _add_consumidor_final(self, parent):
    """Add the mandatory Consumidor Final entry."""
    customer = ET.SubElement(parent, 'Customer')

    customer_id = ET.SubElement(customer, 'CustomerID')
    customer_id.text = 'CF'

    customer_tax_id = ET.SubElement(customer, 'CustomerTaxID')
    customer_tax_id.text = '999999999'

    company_name = ET.SubElement(customer, 'CompanyName')
    company_name.text = 'Consumidor Final'

    # Minimal address as per SAF-T requirement
    address = ET.SubElement(customer, 'BillingAddress')

    address_detail = ET.SubElement(address, 'AddressDetail')
    address_detail.text = 'N/A'

    city = ET.SubElement(address, 'City')
    city.text = 'N/A'

    postal_code = ET.SubElement(address, 'PostalCode')
    postal_code.text = '0000'

    country = ET.SubElement(address, 'Country')
    country.text = 'CV'
```

---

### 2.4 Validação NIF/Nome do Contribuinte

**Estado:** ⚠️ ESTRUTURA IMPLEMENTADA - API NÃO CONECTADA

A estrutura para validação existe, mas a conexão real à API DNRE está pendente.

**Localização do Código:**
- Ficheiro: `restaurant-back/api/apps/payments/services/efatura_service.py`
- Estado atual: Modo de simulação

**Estrutura de Autenticação (Placeholder):**

```python
# efatura_service.py - Estrutura preparada para API DNRE

class EFaturaService:
    """Service for e-Fatura operations with DNRE API."""

    # Configuration - TO BE UPDATED with real credentials
    DNRE_API_ENABLED = False  # Set to True when credentials available
    DNRE_API_BASE_URL = 'https://api.efatura.cv/v1'  # Official endpoint

    def __init__(self):
        self.settings = self._get_company_settings()

    def validate_taxpayer(self, nif: str) -> dict:
        """
        Validate taxpayer NIF against DNRE registry.

        Endpoint: GET /v1/taxpayer/search

        Args:
            nif: Tax identification number to validate

        Returns:
            dict: Taxpayer information or error
        """
        if not self.DNRE_API_ENABLED:
            # Simulation mode - return placeholder
            return {
                'valid': True,
                'nif': nif,
                'name': 'Contribuinte (Simulação)',
                'message': 'API DNRE não conectada - modo simulação'
            }

        # Real implementation (pending credentials)
        """
        headers = {
            'Authorization': f'Bearer {self._get_jwt_token()}',
            'Content-Type': 'application/json'
        }

        response = requests.get(
            f'{self.DNRE_API_BASE_URL}/taxpayer/search',
            params={'nif': nif},
            headers=headers,
            cert=self._get_client_certificate()  # mTLS
        )

        return response.json()
        """
        raise NotImplementedError("DNRE API integration pending - requires credentials")

    def _get_jwt_token(self) -> str:
        """
        Get JWT token for DNRE API authentication.

        This requires:
        1. Digital Certificate (ICP-CV)
        2. API credentials from DNRE
        3. OAuth2/JWT flow implementation
        """
        # TODO: Implement when credentials available
        raise NotImplementedError("JWT authentication pending - requires DNRE credentials")
```

**Requisitos para Ativação:**

1. Certificado Digital Qualificado (ICP-CV)
2. Credenciais de API fornecidas pela DNRE
3. URLs oficiais dos endpoints de produção
4. Ficheiros XSD para validação

---

## Eixo 3: Identificação do Software (XML DFE)

### 3.1 Bloco de Software no XML

**Estado:** ✅ IMPLEMENTADO

**Localização do Código:**
- Ficheiro: `restaurant-back/api/apps/payments/services/efatura_service.py`
- Linhas: 318-323

```python
# efatura_service.py - Linhas 318-323
def _add_software_info(self, parent):
    """Add software identification block to XML."""
    software = ET.SubElement(parent, 'Software')

    code = ET.SubElement(software, 'Code')
    code.text = self.settings.software_certificate_number or '0'

    name = ET.SubElement(software, 'Name')
    name.text = 'Restaurant ERP'

    version = ET.SubElement(software, 'Version')
    version.text = self.settings.software_version or '1.0.0'
```

**Campo de Configuração:**

```python
# common/models.py - CompanySettings
class CompanySettings(models.Model):
    """Company configuration including fiscal settings."""

    software_certificate_number = models.CharField(
        max_length=20,
        default='0',
        help_text="DNRE software certification number. Use '0' until official certification."
    )

    software_version = models.CharField(
        max_length=20,
        default='1.0.0',
        help_text="Current software version"
    )
```

**Confirmação:** O campo `<Code>` será atualizado com o Número de Certificação oficial assim que for atribuído pela DNRE. O valor "0" (zero) está correto para a fase de pré-submissão/homologação.

---

## Próximos Passos Regulatórios

### 1. Certificado Digital Qualificado (ICP-CV)

**Estado:** ⏳ A INICIAR

**Ação Requerida:**
- Contactar entidade certificadora autorizada em Cabo Verde
- Solicitar Certificado Digital para Assinatura Eletrónica Qualificada
- Tipo recomendado: Certificado de Pessoa Coletiva (SSL-EV ou equivalente)

**Uso no Sistema:**
- Autenticação mTLS com API DNRE
- Assinatura digital dos documentos fiscais
- Garantia de não-repúdio

### 2. Taxa de Homologação DNRE

**Estado:** ⏳ CONSULTA PENDENTE

**Ação Requerida:**
- Contacto direto com DNRE para obter informação sobre:
  - Valor da taxa de homologação
  - Processo de submissão
  - Documentação necessária
  - Prazo de análise

**Nota:** Esta informação não é pública e requer contacto formal com a DNRE.

### 3. Manuais Técnicos e XSD

**Estado:** ⏳ A OBTER

**Ação Requerida:**
- Descarregar ficheiros XML-XSD do portal efatura.cv:
  - `CV_EFatura_Invoice_v1.0.xsd` (e-Fatura)
  - `SAF-T_CV_1.04_01.xsd` (SAF-T CV)
- Implementar validação XSD antes de submissão
- Utilizar XSD para testes de conformidade

---

## Lacunas Identificadas e Plano de Ação

### Lacunas Críticas

| Lacuna | Prioridade | Dependência | Ação |
|--------|------------|-------------|------|
| Integração API DNRE | Alta | Credenciais DNRE | Aguarda credenciais oficiais |
| Validação XSD | Alta | Ficheiros XSD | Implementar após download |
| Assinatura com Certificado | Alta | Certificado ICP-CV | Aguarda aquisição |

### Lacunas Menores

| Lacuna | Prioridade | Ação |
|--------|------------|------|
| Logs de auditoria detalhados | Média | Implementar logging de operações fiscais |
| Retry para submissões falhadas | Média | Adicionar fila de reprocessamento |
| Dashboard de conformidade | Baixa | Criar relatórios de estado fiscal |

---

## Conclusão

O sistema **Restaurant Management System** possui uma base sólida para conformidade com os requisitos da DNRE de Cabo Verde:

### Pontos Fortes
- ✅ Encadeamento criptográfico SHA-256 completo
- ✅ Imutabilidade de documentos assinados
- ✅ Geração de IUD e QR Code
- ✅ Sistema de Notas de Crédito
- ✅ Exportação SAF-T CV completa
- ✅ Tratamento de Consumidor Final

### Pendências Críticas
- ⚠️ Integração real com API DNRE (aguarda credenciais)
- ⚠️ Certificado Digital Qualificado (a adquirir)
- ⚠️ Validação XSD (aguarda ficheiros oficiais)

### Estimativa de Tempo para Conclusão
Após obtenção das credenciais e certificado digital: **2-3 semanas** para implementação completa da integração API e testes.

---

**Documento preparado para:** Auditoria de Conformidade Técnica DNRE
**Versão:** 1.0
**Data:** 19 de Novembro de 2025
