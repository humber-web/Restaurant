import { api } from './client'
import type { Order, CreateOrderPayload } from '@/types/models'

export const ordersApi = {
  async getOrders(): Promise<Order[]> {
    const response = await api.get('/order/')
    return response.data
  },

  async getOrder(id: number): Promise<Order> {
    const response = await api.get(`/order/${id}/`)
    return response.data
  },

  async createOrder(data: CreateOrderPayload): Promise<Order> {
    const response = await api.post('/order/register/', data)
    return response.data
  },

  async updateOrder(id: number, data: Partial<Order>): Promise<Order> {
    const response = await api.put(`/order/${id}/update/`, data)
    return response.data
  },

  async updateOrderItems(id: number, items: Order['items']): Promise<Order> {
    const response = await api.patch(`/order/${id}/update/`, { items })
    return response.data
  },

  async transferItems(data: {
    from_order: number
    to_order: number
    items: Array<{ menu_item: number; quantity: number }>
  }): Promise<void> {
    await api.post('/order/transfer/', data)
  },

  async deleteOrder(id: number): Promise<void> {
    await api.delete(`/order/${id}/delete/`)
  },
}
