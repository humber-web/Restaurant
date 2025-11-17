import { api } from './client'
import type {
  PurchaseOrder,
  CreatePurchaseOrderRequest,
  ReceiveGoodsRequest,
  SupplierInvoice,
  CreateSupplierInvoiceRequest,
  MarkInvoiceAsPaidRequest
} from '@/types/models'

export const purchasesApi = {
  // Purchase Orders
  async getPurchaseOrders(params?: {
    status?: string
    supplier?: number
    from_date?: string
    to_date?: string
  }): Promise<PurchaseOrder[]> {
    const response = await api.get('/purchases/purchase-orders/', { params })
    return response.data
  },

  async getPurchaseOrder(id: number): Promise<PurchaseOrder> {
    const response = await api.get(`/purchases/purchase-orders/${id}/`)
    return response.data
  },

  async createPurchaseOrder(data: CreatePurchaseOrderRequest): Promise<PurchaseOrder> {
    const response = await api.post('/purchases/purchase-orders/', data)
    return response.data
  },

  async updatePurchaseOrder(
    id: number,
    data: Partial<Pick<PurchaseOrder, 'status' | 'notes' | 'expected_delivery_date'>>
  ): Promise<PurchaseOrder> {
    const response = await api.patch(`/purchases/purchase-orders/${id}/`, data)
    return response.data
  },

  async cancelPurchaseOrder(id: number): Promise<{ detail: string }> {
    const response = await api.delete(`/purchases/purchase-orders/${id}/`)
    return response.data
  },

  // Goods Receipt
  async receiveGoods(data: ReceiveGoodsRequest): Promise<{
    detail: string
    purchase_order_item: any
  }> {
    const response = await api.post('/purchases/receive-goods/', data)
    return response.data
  },

  // Supplier Invoices
  async getSupplierInvoices(params?: {
    status?: string
    supplier?: number
    overdue?: boolean
  }): Promise<SupplierInvoice[]> {
    const response = await api.get('/purchases/supplier-invoices/', { params })
    return response.data
  },

  async getSupplierInvoice(id: number): Promise<SupplierInvoice> {
    const response = await api.get(`/purchases/supplier-invoices/${id}/`)
    return response.data
  },

  async createSupplierInvoice(data: CreateSupplierInvoiceRequest): Promise<SupplierInvoice> {
    const response = await api.post('/purchases/supplier-invoices/', data)
    return response.data
  },

  async updateSupplierInvoice(
    id: number,
    data: Partial<CreateSupplierInvoiceRequest>
  ): Promise<SupplierInvoice> {
    const response = await api.patch(`/purchases/supplier-invoices/${id}/`, data)
    return response.data
  },

  async cancelSupplierInvoice(id: number): Promise<{ detail: string }> {
    const response = await api.delete(`/purchases/supplier-invoices/${id}/`)
    return response.data
  },

  async markInvoiceAsPaid(
    id: number,
    data?: MarkInvoiceAsPaidRequest
  ): Promise<{
    detail: string
    invoice: SupplierInvoice
  }> {
    const response = await api.post(`/purchases/supplier-invoices/${id}/mark-paid/`, data || {})
    return response.data
  },
}
