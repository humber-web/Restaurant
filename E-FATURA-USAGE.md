# e-Fatura CV - Guia de Utilização

**Status**: ⚠️ **MODO SIMULAÇÃO** (Salva XMLs localmente)
**Versão**: 1.0
**Última atualização**: 15 de Novembro de 2025

---

## 📋 Visão Geral

O sistema está configurado para gerar XMLs de e-Fatura conforme os schemas oficiais da DNRE.

**Modo atual**: SIMULAÇÃO
- XMLs são salvos em `restaurant-back/api/efatura_xml/`
- Não há comunicação com a API da DNRE
- Ideal para testes e validação

**Modo produção** (quando tiver credenciais DNRE):
- Editar `efatura_service.py`: `DNRE_API_ENABLED = True`
- Configurar credenciais de API
- XMLs serão enviados em tempo real para a DNRE

---

## 🚀 Como Usar

### Opção 1: Endpoint All-in-One (Recomendado)

Este endpoint faz tudo de uma vez: assina a fatura E gera o e-Fatura.

```bash
POST /api/payment/<payment_id>/efatura/submit/

# Exemplo
POST /api/payment/123/efatura/submit/

# Resposta
{
  "detail": "Invoice signed and e-Fatura generated successfully",
  "payment": {
    "paymentID": 123,
    "invoice_no": "FT A/2025/00001",
    "invoice_hash": "a3f8b2c1...",
    "is_signed": true,
    ...
  },
  "efatura": {
    "mode": "simulation",
    "invoice_no": "FT A/2025/00001",
    "iud": "CV1202511151234567890FTA00001000000001...",
    "file_path": "/path/to/efatura_xml/efatura_FT_FT_A_2025_00001_2025-11-15.xml",
    "message": "XML saved locally (simulation mode)"
  }
}
```

### Opção 2: Workflow em Dois Passos

**Passo 1: Assinar fatura**
```bash
POST /api/payment/<payment_id>/sign/
```

**Passo 2: Gerar e-Fatura**
```bash
POST /api/payment/<payment_id>/efatura/generate/
```

### Opção 3: Apenas Download do XML

Para baixar o XML sem submeter:
```bash
GET /api/payment/<payment_id>/efatura/download/

# Retorna arquivo XML para download
```

---

## 📊 Estrutura do XML Gerado

O XML segue o schema oficial `CV_EFatura_Invoice_v1.0.xsd`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Dfe xmlns="urn:cv:efatura:xsd:v1.0"
     Version="1.0"
     Id="CV1202511151234567890FTA00001000000001..."
     DocumentTypeCode="1">

    <IsSpecimen>true</IsSpecimen>  <!-- Modo teste -->

    <Invoice>
        <!-- Identificação -->
        <LedCode>1</LedCode>
        <Serie>FT A</Serie>
        <DocumentNumber>00001</DocumentNumber>
        <IssueDate>2025-11-15</IssueDate>
        <IssueTime>14:30:00</IssueTime>

        <!-- Emissor (Empresa) -->
        <EmitterParty>
            <TaxId CountryCode="CV">123456789</TaxId>
            <Name>Restaurante Exemplo Lda</Name>
            <Address CountryCode="CV">
                <AddressDetail>Av. Principal, 123, Praia, 7600</AddressDetail>
                <AddressCode>CV7600</AddressCode>
            </Address>
            <Contacts>
                <Telephone>+2382345678</Telephone>
                <Email>fiscal@restaurante.cv</Email>
                <Website>www.restaurante.cv</Website>
            </Contacts>
        </EmitterParty>

        <!-- Receptor (Cliente) -->
        <ReceiverParty>
            <TaxId CountryCode="CV">987654321</TaxId>
            <Name>Cliente Exemplo</Name>
            ...
        </ReceiverParty>

        <!-- Linhas (Produtos) -->
        <Lines>
            <Line LineTypeCode="N">
                <Id>1</Id>
                <Quantity UnitCode="UN" IsStandardUnitCode="true">2</Quantity>
                <Price>500.00</Price>
                <PriceExtension>1000.00</PriceExtension>
                <NetTotal>1000.00</NetTotal>
                <Tax TaxTypeCode="IVA">
                    <TaxPercentage>15.00</TaxPercentage>
                    <TaxTotal>150.00</TaxTotal>
                </Tax>
                <Item>
                    <Description>Prato do Dia</Description>
                    <EmitterIdentification>42</EmitterIdentification>
                </Item>
            </Line>
        </Lines>

        <!-- Totais -->
        <Totals>
            <TaxTotal>150.00</TaxTotal>
            <NetTotal>1000.00</NetTotal>
            <GrandTotal>1150.00</GrandTotal>
        </Totals>

        <!-- Pagamentos -->
        <Payments>
            <Payment>
                <PaymentMeansCode>10</PaymentMeansCode>  <!-- 10 = Cash -->
                <PaymentAmount>1150.00</PaymentAmount>
                <IsPaid>true</IsPaid>
            </Payment>
        </Payments>

        <!-- Software -->
        <Software>
            <Code>0</Code>  <!-- Certificado software (0 = teste) -->
            <Name>Restaurant ERP</Name>
            <Version>1.0.0</Version>
        </Software>
    </Invoice>
</Dfe>
```

---

## 🔧 Configuração

### Pré-requisitos

1. **CompanySettings configurado** no Django Admin
   ```python
   # Campos obrigatórios:
   - tax_registration_number (NIF)
   - company_name
   - street_name, city, postal_code
   - telephone, email
   - invoice_series (ex: "FT A")
   ```

2. **Payment assinado**
   - `is_signed = True`
   - `invoice_no` preenchido
   - `invoice_hash` calculado

### Diretório de Armazenamento

XMLs são salvos em:
```bash
restaurant-back/api/efatura_xml/
```

Formato do nome do ficheiro:
```
efatura_{invoice_type}_{invoice_no}_{date}.xml
# Exemplo:
efatura_FT_FT_A_2025_00001_2025-11-15.xml
```

---

## 📝 Tipos de Documentos Suportados

| Tipo | Código | DocumentTypeCode | Descrição |
|---|---|---|---|
| FT | Fatura | 1 | Fatura normal |
| FR | Fatura Recibo | 2 | Fatura com pagamento total |
| TV | Talão de Venda | 3 | Venda a consumidor final |
| NC | Nota de Crédito | 5 | Anulação/devolução |

---

## 🔐 Códigos de Meio de Pagamento

| Método | PaymentMeansCode |
|---|---|
| Cash (Dinheiro) | 10 |
| Credit Card | 48 |
| Debit Card | 49 |
| Online/Transfer | 30 |

---

## ⚙️ Configuração para Produção

Quando tiver credenciais da DNRE:

1. **Editar `efatura_service.py`:**
   ```python
   DNRE_API_ENABLED = True
   ```

2. **Configurar credenciais** (adicionar ao settings.py):
   ```python
   DNRE_API_URL = 'https://efatura.cv/api/v1'
   DNRE_API_KEY = 'sua-chave-api'
   DNRE_API_SECRET = 'seu-secret'
   ```

3. **Implementar `submit_to_dnre()` real**:
   ```python
   def submit_to_dnre(self):
       import requests

       xml_content = self.generate_xml()

       response = requests.post(
           f"{settings.DNRE_API_URL}/dfe/invoice/submit",
           headers={
               'Authorization': f'Bearer {settings.DNRE_API_KEY}',
               'Content-Type': 'application/xml',
           },
           data=xml_content.encode('utf-8')
       )

       return response.json()
   ```

4. **Obter Certificado Digital ICP-CV**
   - Necessário para assinatura XAdES
   - Contactar entidade certificadora de Cabo Verde

---

## 🧪 Testes

### Teste Básico

```python
# Django shell
python manage.py shell

from apps.payments.models import Payment
from apps.payments.services.efatura_service import EFaturaService

# Get a signed payment
payment = Payment.objects.filter(is_signed=True).first()

# Generate XML
service = EFaturaService(payment)
xml = service.generate_xml()
print(xml)

# Submit (simulation mode)
result = service.submit_to_dnre()
print(result)
```

### Verificar XMLs Gerados

```bash
ls -la restaurant-back/api/efatura_xml/
cat restaurant-back/api/efatura_xml/efatura_FT_*.xml
```

---

## ❗ Limitações Atuais

### ❌ Não Implementado

1. **Assinatura Digital XAdES**
   - XMLs não estão assinados digitalmente
   - Necessário para produção
   - Requer certificado ICP-CV

2. **Validação XSD**
   - Função `validate_xml()` é placeholder
   - Implementar com `lxml`

3. **API DNRE Real**
   - Apenas modo simulação
   - Falta integração com endpoints oficiais

4. **Modo de Contingência**
   - Quando DNRE offline
   - Queue de XMLs pendentes

### ✅ Implementado

- ✅ Geração XML conforme schema oficial
- ✅ IUD (Identificador Único)
- ✅ Todos os tipos de documento (FT, FR, TV, NC)
- ✅ Cálculo de impostos (IVA 15%)
- ✅ Múltiplas linhas de produtos
- ✅ Informação de pagamentos
- ✅ Consumidor Final support
- ✅ Software metadata

---

## 📚 Recursos

### Schemas Oficiais
```
2024-05-27-XML-XSD/common/
├── CV_EFatura_Invoice_v1.0.xsd
├── CV_EFatura_Elements_v1.0.xsd
├── CV_EFatura_Types_v1.0.xsd
└── ...
```

### Documentação
- `manual-tecnico-da-fatura-eletronica-v10.0.pdf`
- `2024-05-27-XML-XSD/Read Me.txt`
- `FISCAL-COMPLIANCE-STATUS.md`

---

## 🚨 Troubleshooting

### Erro: "Payment must be signed"
**Solução**: Assinar fatura primeiro
```bash
POST /api/payment/<id>/sign/
```

### Erro: "CompanySettings not configured"
**Solução**: Configurar empresa no Django Admin
```bash
/admin/common/companysettings/
```

### XML não encontrado
**Solução**: Verificar se diretório existe
```bash
mkdir -p restaurant-back/api/efatura_xml
chmod 755 restaurant-back/api/efatura_xml
```

---

## 📞 Próximos Passos

1. ✅ Testar geração de XML em ambiente local
2. ✅ Validar XML contra schemas oficiais
3. ⏳ Obter certificado digital ICP-CV
4. ⏳ Implementar assinatura XAdES
5. ⏳ Obter credenciais API DNRE
6. ⏳ Testar em ambiente de homologação DNRE
7. ⏳ Go-live em produção

---

**Modo atual**: ⚠️ SIMULAÇÃO
**Pronto para produção**: ❌ Não (falta assinatura digital e credenciais DNRE)
**Conforme com schemas**: ✅ Sim
