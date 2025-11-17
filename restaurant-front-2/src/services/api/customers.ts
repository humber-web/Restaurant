/**
 * Customers API Service
 */
import { api } from './client'
import type {
  Customer,
  CreateCustomerPayload,
  UpdateCustomerPayload,
  ListCustomersParams
} from '@/types/models/customer'

class CustomersAPI {
  /**
   * List all customers with optional filters
   */
  async list(params?: ListCustomersParams): Promise<Customer[]> {
    const queryParams = new URLSearchParams()

    if (params?.is_active !== undefined) {
      queryParams.append('is_active', params.is_active.toString())
    }
    if (params?.customer_type) {
      queryParams.append('customer_type', params.customer_type)
    }
    if (params?.search) {
      queryParams.append('search', params.search)
    }
    if (params?.ordering) {
      queryParams.append('ordering', params.ordering)
    }

    const response = await api.get(`/customers/?${queryParams.toString()}`)
    return response.data
  }

  /**
   * Get active customers only
   */
  async listActive(): Promise<Customer[]> {
    const response = await api.get('/customers/active/')
    return response.data
  }

  /**
   * Get customer by ID
   */
  async get(id: number): Promise<Customer> {
    const response = await api.get(`/customers/${id}/`)
    return response.data
  }

  /**
   * Search customer by exact NIF match
   */
  async searchByNIF(nif: string): Promise<Customer> {
    const response = await api.get(`/customers/search_by_nif/?nif=${nif}`)
    return response.data
  }

  /**
   * Create new customer
   */
  async create(data: CreateCustomerPayload): Promise<Customer> {
    const response = await api.post('/customers/', data)
    return response.data
  }

  /**
   * Update existing customer
   */
  async update(id: number, data: UpdateCustomerPayload): Promise<Customer> {
    const response = await api.patch(`/customers/${id}/`, data)
    return response.data
  }

  /**
   * Delete customer (soft delete - sets is_active to false)
   */
  async delete(id: number): Promise<void> {
    await api.delete(`/customers/${id}/`)
  }
}

export const customersApi = new CustomersAPI()
