/**
 * Supplier Type Definitions
 */

export interface Supplier {
  supplierID: number
  tax_id: string
  company_name: string
  contact_person?: string

  // Address (required)
  street_name: string
  building_number?: string
  city: string
  postal_code: string
  region?: string
  country: string
  address_detail?: string

  // Contacts
  telephone?: string
  mobile_phone?: string
  fax?: string
  email?: string
  website?: string

  // Bank info
  bank_name?: string
  bank_account?: string
  iban?: string

  // Payment terms
  payment_terms?: string

  // Status
  is_active: boolean
  notes?: string

  // Metadata
  created_at: string
  updated_at: string

  // Computed fields
  full_address: string
}

export interface CreateSupplierPayload {
  tax_id: string
  company_name: string
  contact_person?: string
  street_name: string
  building_number?: string
  city: string
  postal_code: string
  region?: string
  country?: string
  address_detail?: string
  telephone?: string
  mobile_phone?: string
  fax?: string
  email?: string
  website?: string
  bank_name?: string
  bank_account?: string
  iban?: string
  payment_terms?: string
  notes?: string
}

export interface UpdateSupplierPayload extends Partial<CreateSupplierPayload> {}

export interface ListSuppliersParams {
  is_active?: boolean
  search?: string
  ordering?: string
}
