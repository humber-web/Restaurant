export type PreparedIn = '1' | '2' | '3'

export interface MenuCategory {
  categoryID: number
  name: string
  prepared_in: PreparedIn
}

export interface MenuItem {
  itemID: number
  name: string
  description: string
  ingredients?: string
  price: number
  availability: boolean
  categoryID: number
  is_quantifiable: boolean
}

export interface MenuItemWithCategory extends MenuItem {
  category: MenuCategory
}
