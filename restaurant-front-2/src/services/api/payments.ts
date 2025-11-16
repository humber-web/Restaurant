import { api } from './client'
import type { Payment, IssueCreditNotePayload, IssueCreditNoteResponse } from '@/types/models'

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

export interface ListInvoicesParams {
  invoice_type?: 'FT' | 'FR' | 'NC' | 'TV'
  start_date?: string
  end_date?: string
  search?: string
  page?: number
  page_size?: number
}

export interface ListInvoicesResponse {
  results: Payment[]
  count: number
  page: number
  page_size: number
  total_pages: number
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

  /**
   * List all invoices (signed payments) with advanced filtering
   */
  async getInvoices(params?: ListInvoicesParams): Promise<ListInvoicesResponse> {
    const queryParams = new URLSearchParams()
    if (params?.invoice_type) queryParams.append('invoice_type', params.invoice_type)
    if (params?.start_date) queryParams.append('start_date', params.start_date)
    if (params?.end_date) queryParams.append('end_date', params.end_date)
    if (params?.search) queryParams.append('search', params.search)
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString())

    const response = await api.get(`/invoices/?${queryParams.toString()}`)
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
  },

  // ===== CREDIT NOTE METHODS =====

  /**
   * Issue a Credit Note (NC) against an existing invoice
   * @param payload - Credit note details (original invoice ID, reason, optional partial amount)
   * @returns Credit note details and original invoice reference
   */
  async issueCreditNote(payload: IssueCreditNotePayload): Promise<IssueCreditNoteResponse> {
    const response = await api.post('/credit-note/issue/', payload)
    return response.data
  }
}
