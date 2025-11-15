# Estado da Conformidade Fiscal - DNRE Cabo Verde

**Última atualização**: 15 de Novembro de 2025
**Branch**: `claude/ux-improvements-01TFNgAprYzTRhPaRq2F3Tft`

---

## 📊 Resumo do Estado Atual

### ✅ IMPLEMENTADO (SAF-T CV)

O sistema **já está conforme** para exportação de dados fiscais (auditoria):

| Componente | Estado | Descrição |
|---|---|---|
| **SAF-T CV Export** | ✅ Completo | Export XML com todos os dados de um período |
| **Invoice Numbering** | ✅ Completo | Numeração sequencial (SÉRIE/ANO/NÚMERO) |
| **Hash Chain** | ✅ Completo | SHA-256 para integridade |
| **IUD Generation** | ✅ Completo | Identificador Único do Documento |
| **CompanySettings** | ✅ Completo | Modelo para dados da empresa |
| **Customer Tax ID** | ✅ Completo | Campo NIF em Profile |
| **Fiscal Fields** | ✅ Completo | Payment model com 14 campos fiscais |

**API Endpoints disponíveis:**
```bash
POST   /api/payment/<id>/sign/              # Assinar fatura
GET    /api/saft/export/?start_date=...     # Exportar SAF-T XML
GET    /api/payment/<id>/validate-hash/     # Validar integridade
```

---

### ⚠️ FALTA IMPLEMENTAR (e-Fatura CV)

Para **faturação eletrónica em tempo real** (obrigatória desde junho 2022):

| Componente | Estado | Prioridade | Descrição |
|---|---|---|---|
| **e-Fatura XML Generator** | ❌ Falta | 🔴 Alta | Gerar XML conforme CV_EFatura_Invoice_v1.0.xsd |
| **Digital Signature (XAdES)** | ❌ Falta | 🔴 Alta | Assinatura digital XML (ETSI XAdES) |
| **DNRE API Integration** | ❌ Falta | 🔴 Alta | Envio em tempo real para plataforma e-Fatura |
| **Contingency Mode** | ❌ Falta | 🟡 Média | Modo offline quando DNRE indisponível |
| **QR Code Generation** | ❌ Falta | 🟡 Média | QR code com IUD na fatura impressa |

---

## 📂 Recursos Disponíveis

### Schemas e Documentação (já no repositório)

```
2024-05-27-XML-XSD/
├── common/
│   ├── CV_EFatura_Invoice_v1.0.xsd          ✅ Schema principal
│   ├── CV_EFatura_Elements_v1.0.xsd         ✅ Elementos comuns
│   ├── CV_EFatura_Types_v1.0.xsd            ✅ Tipos de dados
│   ├── W3C_XMLDSig.xsd                      ✅ Assinatura digital
│   └── ETSI_XAdESv132.xsd                   ✅ XAdES standard
├── 1 Invoice - EnvelopedSignature.xml       ✅ Exemplo de fatura
├── 5 CreditNote.xml                         ✅ Exemplo de nota de crédito
└── Read Me.txt                              ✅ Changelog oficial

manual-tecnico-da-fatura-eletronica-v10.0.pdf  ✅ Manual completo DNRE
```

---

## 🎯 Diferença entre SAF-T e e-Fatura

### SAF-T CV (✅ Implementado)
- **Quando**: Mensal ou sob pedido da fiscalização
- **O quê**: Export de **todos** os dados contabilísticos de um período
- **Formato**: 1 ficheiro XML grande com Header + Clientes + Produtos + Faturas
- **Para**: Auditoria e verificação fiscal
- **Obrigatório**: Sim, sob pedido

### e-Fatura CV (❌ Falta implementar)
- **Quando**: Em tempo real, no momento da emissão
- **O quê**: Cada fatura individual é enviada à DNRE
- **Formato**: 1 XML por fatura, conforme schema CV_EFatura
- **Para**: Controlo fiscal em tempo real
- **Obrigatório**: Sim, desde junho 2022
- **Tempo máximo**: 1 minuto após emissão (senão entra em contingência)

---

## 🚀 Próximos Passos Prioritários

### Fase 1: Preparação (Agora)
1. ✅ Migrar base de dados (`python manage.py migrate`)
2. ✅ Configurar `CompanySettings` no Django Admin
3. ✅ Testar SAF-T export com dados reais

### Fase 2: e-Fatura Implementation (Urgente)
4. ❌ Criar `EFaturaService` para gerar XML individual
5. ❌ Implementar assinatura digital XAdES
6. ❌ Integrar com API da DNRE (endpoints de submissão)
7. ❌ Implementar modo de contingência
8. ❌ Gerar QR Code com IUD

### Fase 3: Certificação
9. ❌ Obter certificado digital ICP-CV
10. ❌ Solicitar certificação do software à DNRE
11. ❌ Testes em ambiente de homologação
12. ❌ Go-live em produção

---

## 📋 Requisitos Técnicos e-Fatura

### Estrutura XML Obrigatória

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Dfe xmlns="urn:cv:efatura:xsd:v1.0" Version="1.0"
     Id="CV1200520123456789000112345678901112345678904"
     DocumentTypeCode="1">

    <Invoice>
        <LedCode>1</LedCode>
        <Serie>FT A</Serie>
        <DocumentNumber>00001</DocumentNumber>
        <IssueDate>2025-11-15</IssueDate>
        <IssueTime>14:30:00</IssueTime>

        <EmitterParty>
            <TaxId CountryCode="CV">123456789</TaxId>
            <Name>Restaurante Exemplo Lda</Name>
            <Address CountryCode="CV">...</Address>
        </EmitterParty>

        <ReceiverParty>...</ReceiverParty>

        <Lines>
            <Line LineTypeCode="N">
                <Quantity UnitCode="EA">2</Quantity>
                <Price>500.00</Price>
                <Tax TaxTypeCode="IVA">
                    <TaxPercentage>15</TaxPercentage>
                    <TaxTotal>150.00</TaxTotal>
                </Tax>
                <Item>
                    <Description>Prato do Dia</Description>
                </Item>
            </Line>
        </Lines>

        <Totals>
            <TaxTotal>150.00</TaxTotal>
            <NetTotal>1000.00</NetTotal>
            <GrandTotal>1150.00</GrandTotal>
        </Totals>

        <Payments>...</Payments>
    </Invoice>

    <!-- Assinatura Digital XAdES -->
    <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">...</Signature>
</Dfe>
```

### Campos Críticos

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `Id` (IUD) | string(45) | ✅ Sim | Identificador único |
| `Serie` | string | ✅ Sim | Série da fatura (ex: "FT A") |
| `DocumentNumber` | integer | ✅ Sim | Número sequencial |
| `IssueDate` | date | ✅ Sim | Data de emissão |
| `IssueTime` | time | ✅ Sim | Hora de emissão |
| `EmitterParty.TaxId` | string(9) | ✅ Sim | NIF do emissor |
| `ReceiverParty.TaxId` | string | ✅ Sim | NIF do cliente |
| `Tax.TaxPercentage` | decimal | ✅ Sim | 15% para IVA normal |
| `Signature` | XML | ✅ Sim | Assinatura XAdES |

---

## 🔐 Segurança e Certificação

### Certificado Digital (ICP-CV)
- **O quê**: Certificado digital emitido pela Infraestrutura de Chaves Públicas de CV
- **Para quê**: Assinar digitalmente as faturas (XAdES)
- **Como obter**: Solicitação à entidade certificadora de CV
- **Custo**: (A verificar com a entidade emissora)

### Software Certificate Number
- **Estado atual**: "0" (ambiente de testes)
- **Produção**: Obter certificação DNRE após implementação completa
- **Processo**:
  1. Completar implementação e-Fatura
  2. Testes em ambiente de homologação
  3. Submeter pedido de certificação à DNRE
  4. Receber número de certificado oficial

---

## 🛠️ Tecnologias Necessárias

### Backend (Django)
- ✅ `hashlib` - SHA-256 (já usado)
- ❌ `lxml` - XML generation e validação
- ❌ `xmlsec` - XML Digital Signature
- ❌ `requests` - HTTP client para DNRE API
- ❌ `qrcode` - QR Code generation

### Instalação:
```bash
pip install lxml xmlsec requests qrcode[pil]
```

---

## 📞 Contactos Úteis

- **DNRE**: Direção Nacional de Receitas do Estado
- **Portal e-Fatura**: https://efatura.cv
- **Suporte técnico**: (consultar portal oficial)

---

## 📝 Notas Finais

### Compliance Status
- **SAF-T CV**: ✅ Pronto para produção
- **e-Fatura CV**: ⚠️ Implementação urgente necessária

### Riscos
- ⚠️ **Sem e-Fatura**: Multas por não conformidade (obrigatório desde junho 2022)
- ✅ **Com SAF-T**: Possibilidade de auditoria fiscal está coberta

### Recomendação
**Prioridade máxima**: Implementar e-Fatura CV nos próximos sprints para garantir conformidade legal total.

---

**Status**: Trabalho em progresso
**Branch**: `claude/ux-improvements-01TFNgAprYzTRhPaRq2F3Tft`
**Commits**:
- `202d96f` - SAF-T CV implementation
- `ab8b0f1` - e-Fatura schemas and manual
