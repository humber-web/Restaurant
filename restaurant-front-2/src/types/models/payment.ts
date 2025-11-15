export type PaymentMethod = 'CASH' | 'CREDIT_CARD' | 'DEBIT_CARD' | 'ONLINE'
export type PaymentStatus = 'PENDING' | 'COMPLETED' | 'FAILED'
export type InvoiceType = 'FT' | 'FR' | 'NC' | 'TV'

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
}

export interface ProcessPaymentPayload {
  order: number
  amount: number
  payment_method: PaymentMethod
  transaction_id?: string
}
