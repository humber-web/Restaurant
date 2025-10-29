export type OrderStatus = 'PENDING' | 'PREPARING' | 'READY' | 'DELIVERED' | 'CANCELLED'
export type PaymentStatus = 'PENDING' | 'PARTIALLY_PAID' | 'PAID' | 'FAILED'
export type OrderType = 'RESTAURANT' | 'ONLINE'
export type OrderItemStatus = '1' | '2' | '3' | '4'

export interface OrderItem {
  menu_item: number
  name?: string
  quantity: number
  price: number
  status: OrderItemStatus
  to_be_prepared_in: string
}

export interface OrderDetails {
  table?: number | null
  online_order_info?: string
}

export interface Order {
  orderID: number
  customer?: number | null
  items: OrderItem[]
  status: OrderStatus
  totalAmount: number
  totalIva: number
  grandTotal: number
  paymentStatus: PaymentStatus
  orderType: OrderType
  created_at: string
  updated_at: string
  last_updated_by?: number | null
  details: OrderDetails
}

export interface CreateOrderPayload {
  customer?: number | null
  items: Array<{
    menu_item: number
    quantity: number
  }>
  orderType: OrderType
  details: OrderDetails
}
