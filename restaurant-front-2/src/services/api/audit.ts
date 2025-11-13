import { api } from './client'
import type { OperationLog } from '@/types/models/audit'

export const auditApi = {
  async getOperationLogs(): Promise<OperationLog[]> {
    const response = await api.get('/audit/logs/')
    return response.data
  },

  async getOperationLog(id: number): Promise<OperationLog> {
    const response = await api.get(`/audit/logs/${id}/`)
    return response.data
  },
}
