export type PaymentMethod = 'CASH' | 'CREDIT_CARD' | 'DEBIT_CARD' | 'ONLINE'
export type PaymentStatus = 'PENDING' | 'COMPLETED' | 'FAILED'
export type InvoiceType = 'FT' | 'FR' | 'NC' | 'TV'

// SAF-T CV Credit Note Reason Codes
export type CreditNoteReason = 'M01' | 'M02' | 'M03' | 'M04' | 'M05' | 'M99'

export const CREDIT_NOTE_REASONS: Record<CreditNoteReason, string> = {
  M01: 'Mercadorias devolvidas',
  M02: 'Erro de faturação',
  M03: 'Anulação total do documento',
  M04: 'Desconto',
  M05: 'Devolução parcial',
  M99: 'Outros motivos',
}

export interface ReferencedDocumentInfo {
  paymentID: number
  invoice_no: string
  invoice_type: InvoiceType
  amount: string
  invoice_date: string
}

export interface Payment {
  paymentID: number
  order: number
  amount: number
  payment_method: PaymentMethod
  payment_status: PaymentStatus
  transaction_id?: string
  created_at: string
  updated_at: string
  processed_by?: number
  cash_register?: number

  // Fiscal compliance fields (SAF-T CV / e-Fatura)
  invoice_no?: string
  invoice_date?: string
  invoice_type?: InvoiceType
  invoice_hash?: string
  previous_invoice_hash?: string  // Empty string '' for first invoice
  iud?: string
  is_signed?: boolean
  signed_at?: string
  customer_tax_id?: string
  customer_name?: string
  hash_algorithm?: string
  software_certificate_number?: string

  // Credit Note fields
  referenced_document?: number  // Payment ID of original invoice
  credit_note_reason?: CreditNoteReason
  referenced_document_info?: ReferencedDocumentInfo  // Nested info from backend

  // QR Code (base64 data URL)
  qr_code?: string  // data:image/png;base64,{base64}
}

export interface ProcessPaymentPayload {
  order: number
  amount: number
  payment_method: PaymentMethod
  transaction_id?: string
}

export interface IssueCreditNotePayload {
  original_invoice_id: number
  credit_note_reason: CreditNoteReason
  partial_amount?: number  // Optional: for partial credits
}

export interface IssueCreditNoteResponse {
  detail: string
  credit_note: Payment
  original_invoice: {
    paymentID: number
    invoice_no: string
    amount: string
  }
  message: string
}
