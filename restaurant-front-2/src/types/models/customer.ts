/**
 * Customer Type Definitions
 */

export type CustomerType = 'INDIVIDUAL' | 'COMPANY'

export interface Customer {
  customerID: number
  customer_type: CustomerType
  tax_id: string

  // Company info
  company_name?: string

  // Individual info
  first_name?: string
  last_name?: string

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

  // Status
  is_active: boolean
  notes?: string

  // Metadata
  created_at: string
  updated_at: string

  // Computed fields
  full_name: string
  full_address: string
}

export interface CreateCustomerPayload {
  customer_type: CustomerType
  tax_id: string
  company_name?: string
  first_name?: string
  last_name?: string
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
  notes?: string
}

export interface UpdateCustomerPayload extends Partial<CreateCustomerPayload> {}

export interface ListCustomersParams {
  is_active?: boolean
  customer_type?: CustomerType
  search?: string
  ordering?: string
}
