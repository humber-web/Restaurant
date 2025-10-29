import { api } from './client'
import type { InventoryItem } from '@/types/models'

export const inventoryApi = {
  async getItems(): Promise<InventoryItem[]> {
    const response = await api.get('/inventory_item/')
    return response.data
  },

  async getItem(id: number): Promise<InventoryItem> {
    const response = await api.get(`/inventory_item/${id}/`)
    return response.data
  },

  async createItem(data: Omit<InventoryItem, 'itemID'>): Promise<InventoryItem> {
    const response = await api.post('/inventory_item/register/', data)
    return response.data
  },

  async updateItem(id: number, data: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await api.put(`/inventory_item/${id}/update/`, data)
    return response.data
  },

  async deleteItem(id: number): Promise<void> {
    await api.delete(`/inventory_item/${id}/delete/`)
  },
}
