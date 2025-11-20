export interface InventoryItem {
  itemID: number
  itemName?: string
  quantity: string // DecimalField
  reserved_quantity: string // DecimalField
  supplier: number | null // ForeignKey to Supplier
  unit_cost?: string // DecimalField
  menu_item: number | null
  product_name?: string | null // Name of related menu item (computed from backend)
  oversell_quantity: string // DecimalField
  reorder_level?: string | null // DecimalField
  reorder_quantity?: string | null // DecimalField
  available_quantity?: string // Computed property
  needs_reorder?: boolean // Computed property
  created_at?: string
  updated_at?: string
}
