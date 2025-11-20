export interface PurchaseOrder {
  purchaseOrderID: number
  po_number: string
  supplier: number
  supplier_name?: string
  supplier_info?: {
    supplierID: number
    company_name: string
    contact_name: string | null
    email: string | null
    phone: string | null
    address: string | null
    tax_id: string | null
  }
  status: 'DRAFT' | 'SUBMITTED' | 'PARTIALLY_RECEIVED' | 'RECEIVED' | 'INVOICED' | 'PAID' | 'CANCELLED'
  order_date: string
  expected_delivery_date: string | null
  total_amount: string
  notes: string
  items?: PurchaseOrderItem[]
  items_count?: number
  created_by: number | null
  created_by_name?: string | null
  created_at: string
  updated_at: string
}

export interface PurchaseOrderItem {
  id: number
  purchase_order: number
  inventory_item: number
  inventory_item_name?: string
  product_name?: string | null
  quantity_ordered: string
  unit_price: string
  line_total?: string
  received_quantity: string
  remaining_quantity?: string
  received_date: string | null
  notes: string
}

export interface CreatePurchaseOrderRequest {
  supplier: number
  order_date: string
  expected_delivery_date?: string | null
  notes?: string
  items: {
    inventory_item: number
    quantity_ordered: number
    unit_price: number
  }[]
}

export interface ReceiveGoodsRequest {
  purchase_order_item_id: number
  quantity_received: number
  received_date?: string | null
  notes?: string
}

export interface SupplierInvoice {
  supplierInvoiceID: number
  invoice_number: string
  supplier: number
  supplier_name?: string
  purchase_order: number | null
  po_number?: string | null
  invoice_date: string
  due_date: string | null
  amount: string
  tax_amount: string
  total_amount: string
  status: 'RECEIVED' | 'APPROVED' | 'SCHEDULED_PAYMENT' | 'PAID' | 'CANCELLED'
  payment_date: string | null
  payment_method: string | null
  notes: string
  days_until_due?: number | null
  created_by: number | null
  created_by_name?: string | null
  created_at: string
  updated_at: string
}

export interface CreateSupplierInvoiceRequest {
  invoice_number: string
  supplier: number
  purchase_order?: number | null
  invoice_date: string
  due_date?: string | null
  amount: number
  tax_amount: number
  total_amount: number
  status?: 'RECEIVED' | 'APPROVED' | 'SCHEDULED_PAYMENT'
  notes?: string
}

export interface MarkInvoiceAsPaidRequest {
  payment_date?: string | null
  payment_method?: string
}
