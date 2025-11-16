/**
 * Suppliers API Service
 */
import { api } from './client'
import type {
  Supplier,
  CreateSupplierPayload,
  UpdateSupplierPayload,
  ListSuppliersParams
} from '@/types/models/supplier'

class SuppliersAPI {
  /**
   * List all suppliers with optional filters
   */
  async list(params?: ListSuppliersParams): Promise<Supplier[]> {
    const queryParams = new URLSearchParams()

    if (params?.is_active !== undefined) {
      queryParams.append('is_active', params.is_active.toString())
    }
    if (params?.search) {
      queryParams.append('search', params.search)
    }
    if (params?.ordering) {
      queryParams.append('ordering', params.ordering)
    }

    const response = await api.get(`/suppliers/?${queryParams.toString()}`)
    return response.data
  }

  /**
   * Get active suppliers only
   */
  async listActive(): Promise<Supplier[]> {
    const response = await api.get('/suppliers/active/')
    return response.data
  }

  /**
   * Get supplier by ID
   */
  async get(id: number): Promise<Supplier> {
    const response = await api.get(`/suppliers/${id}/`)
    return response.data
  }

  /**
   * Search supplier by exact NIF match
   */
  async searchByNIF(nif: string): Promise<Supplier> {
    const response = await api.get(`/suppliers/search_by_nif/?nif=${nif}`)
    return response.data
  }

  /**
   * Create new supplier
   */
  async create(data: CreateSupplierPayload): Promise<Supplier> {
    const response = await api.post('/suppliers/', data)
    return response.data
  }

  /**
   * Update existing supplier
   */
  async update(id: number, data: UpdateSupplierPayload): Promise<Supplier> {
    const response = await api.patch(`/suppliers/${id}/`, data)
    return response.data
  }

  /**
   * Delete supplier (soft delete - sets is_active to false)
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/suppliers/${id}/`)
  }
}

export const suppliersApi = new SuppliersAPI()
