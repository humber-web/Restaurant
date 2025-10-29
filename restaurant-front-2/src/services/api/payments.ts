import { api } from './client'
import type { Payment, ProcessPaymentPayload } from '@/types/models'

export const paymentsApi = {
  async processPayment(data: ProcessPaymentPayload): Promise<Payment> {
    const response = await api.post('/payment/register/', data)
    return response.data
  },

  async getPayments(): Promise<Payment[]> {
    const response = await api.get('/payment/')
    return response.data
  },

  async getPayment(id: number): Promise<Payment> {
    const response = await api.get(`/payment/${id}/`)
    return response.data
  },
}
