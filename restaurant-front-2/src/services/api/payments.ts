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
  }
}
