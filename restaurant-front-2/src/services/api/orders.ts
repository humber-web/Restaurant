import { api } from './client'
import type { Order, CreateOrderPayload } from '@/types/models'

export const ordersApi = {
  async getOrders(): Promise<Order[]> {
    const response = await api.get('/orders/')
    return response.data
  },

  async getOrder(id: number): Promise<Order> {
    const response = await api.get(`/order/${id}/`)
    return response.data
  },

  async getOrdersByTable(tableId: number): Promise<Order[]> {
    const response = await api.get(`/order/?table=${tableId}`)
    return response.data
  },

  async createOrder(data: CreateOrderPayload): Promise<Order> {
    const payload = {
      ...data,
      model: 'order',
      operation: 'CREATE'
    }
    const response = await api.post('/order/register/', payload)
    return response.data
  },

  async updateOrder(id: number, data: Partial<Order>): Promise<Order> {
    const payload = {
      ...data,
      model: 'order',
      operation: 'UPDATE',
      object_id: String(id)
    }
    const response = await api.put(`/order/${id}/update/`, payload)
    return response.data
  },

  async updateOrderItems(id: number, items: Order['items']): Promise<Order> {
    const response = await api.patch(`/order/${id}/update/`, { items })
    return response.data
  },

  async transferItems(data: {
    source_order_id: number
    target_order_id: number
  }): Promise<Order> {
    const response = await api.post('/order/transfer/', data)
    return response.data
  },

  async deleteOrder(id: number): Promise<void> {
    await api.delete(`/order/${id}/delete/`)
  },

  async updateOrderItemStatus(itemId: number, status: string): Promise<Order> {
    const response = await api.patch(`/order-item/${itemId}/status/`, { status })
    return response.data.order
  },
}
