export type PaymentMethod = 'CASH' | 'CREDIT_CARD' | 'DEBIT_CARD' | 'ONLINE'
export type PaymentStatus = 'PENDING' | 'COMPLETED' | 'FAILED'

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
}

export interface ProcessPaymentPayload {
  order: number
  amount: number
  payment_method: PaymentMethod
  transaction_id?: string
}
