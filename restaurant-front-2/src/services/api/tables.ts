import { api } from './client'
import type { Table } from '@/types/models'

export const tablesApi = {
  async getTables(): Promise<Table[]> {
    const response = await api.get('/table/')
    return response.data
  },

  async getTable(id: number): Promise<Table> {
    const response = await api.get(`/table/${id}/`)
    return response.data
  },

  async createTable(data: Omit<Table, 'tableid'>): Promise<Table> {
    const payload = {
      ...data,
      model: "table",
      operation: "CREATE",
    };
    const response = await api.post('/table/register/', payload)
    return response.data
  },

  async updateTable(id: number, data: Partial<Table>): Promise<Table> {
    const payload = {
      ...data,
      model: "table",
      operation: "UPDATE",
      object_id: id
    };
    const response = await api.put(`/table/${id}/update/`, payload)
    return response.data
  },

  async deleteTable(id: number): Promise<void> {
    await api.delete(`/table/${id}/delete/`)
  },
}
