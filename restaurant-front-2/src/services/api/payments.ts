import { api } from './client'
import type { Payment } from '@/types/models'

export interface ProcessPaymentPayload {
  orderID: number
  amount: number
  payment_method: 'CASH' | 'CREDIT_CARD' | 'DEBIT_CARD' | 'ONLINE'
  selected_items?: Array<{
    menu_item_id: number
    quantity: number
  }>  // Optional: items with quantities being paid for
}

export interface ProcessPaymentResponse {
  detail: string
  change_due: string
  payment: Payment
}

export interface EFaturaResponse {
  detail: string
  payment: Payment
  efatura: {
    mode: 'simulation' | 'production'
    invoice_no: string
    iud: string
    file_path?: string
    message: string
  }
}

export const paymentsApi = {
  async processPayment(data: ProcessPaymentPayload): Promise<ProcessPaymentResponse> {
    const response = await api.post('/payment/process/', data)
    return response.data
  },

  async getPayments(): Promise<Payment[]> {
    const response = await api.get('/payments/')
    return response.data
  },

  async getPayment(id: number): Promise<Payment> {
    const response = await api.get(`/payment/${id}/`)
    return response.data
  },

  async getPaymentsByOrder(orderID: number): Promise<Payment[]> {
    const response = await api.get(`/payments/order/${orderID}/`)
    return response.data
  },

  // ===== E-FATURA CV METHODS =====

  /**
   * Sign invoice and generate e-Fatura XML (all-in-one - recommended)
   * This will:
   * 1. Sign the invoice (if not already signed)
   * 2. Generate e-Fatura XML
   * 3. Submit to DNRE (or save locally in simulation mode)
   *
   * @param paymentId - Payment ID
   * @param customerTaxId - Optional customer NIF (defaults to "Consumidor Final" if not provided)
   */
  async generateEFatura(paymentId: number, customerTaxId?: string): Promise<EFaturaResponse> {
    const response = await api.post(`/payment/${paymentId}/efatura/submit/`, {
      customer_tax_id: customerTaxId
    })
    return response.data
  },

  /**
   * Download e-Fatura XML file for a payment
   */
  async downloadEFaturaXML(paymentId: number): Promise<Blob> {
    const response = await api.get(`/payment/${paymentId}/efatura/download/`, {
      responseType: 'blob'
    })
    return response.data
  },

  /**
   * Sign invoice (generate fiscal fields)
   */
  async signInvoice(paymentId: number): Promise<{ detail: string; payment: Payment }> {
    const response = await api.post(`/payment/${paymentId}/sign/`)
    return response.data
  }
}
