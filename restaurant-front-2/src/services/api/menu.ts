import { api } from './client'
import type { MenuCategory, MenuItem } from '@/types/models'

export const menuApi = {
  // Categories
  async getCategories(): Promise<MenuCategory[]> {
    const response = await api.get('/menu_category/')
    return response.data
  },

  async getCategory(id: number): Promise<MenuCategory> {
    const response = await api.get(`/menu_category/${id}/`)
    return response.data
  },

  async createCategory(data: Omit<MenuCategory, 'categoryID'>): Promise<MenuCategory> {
     const payload = {
    ...data,
    model: "menucategory",
    operation: "CREATE",
  };
    const response = await api.post('/menu_category/register/', payload)
    return response.data
  },

  async updateCategory(id: number, data: Partial<MenuCategory>): Promise<MenuCategory> {
    const payload = {
      ...data,
      model: 'menucategory',
      operation: 'UPDATE',
      object_id: String(id)
    }
    const response = await api.put(`/menu_category/${id}/update/`, payload)
    return response.data
  },

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`/menu_category/${id}/delete/`)
  },

  // Menu Items
  async getItems(): Promise<MenuItem[]> {
    const response = await api.get('/menu_item/')
    return response.data
  },

  async getItem(id: number): Promise<MenuItem> {
    const response = await api.get(`/menu_item/${id}/`)
    return response.data
  },

  async getItemsByCategory(): Promise<Record<string, MenuItem[]>> {
    const response = await api.get('/menu_item/category/')
    return response.data
  },

  async createItem(data: Omit<MenuItem, 'itemID'>): Promise<MenuItem> {
    const payload = {
      ...data,
      model: 'menuitem',
      operation: 'CREATE',
    }
    const response = await api.post('/menu_item/register/', payload)
    return response.data
  },

  async updateItem(id: number, data: Partial<MenuItem>): Promise<MenuItem> {
    const payload = {
      ...data,
      model: 'menuitem',
      operation: 'UPDATE',
      object_id: String(id)
    }
    const response = await api.put(`/menu_item/${id}/update/`, payload)
    return response.data
  },

  async deleteItem(id: number): Promise<void> {
    await api.delete(`/menu_item/${id}/delete/`)
  },
}
