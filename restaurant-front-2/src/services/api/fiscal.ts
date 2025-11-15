import { api } from './client'

export interface CompanySettings {
  id: number
  tax_registration_number: string
  company_name: string
  street_name: string
  building_number?: string
  city: string
  postal_code: string
  country: string
  telephone: string
  fax?: string
  email: string
  website?: string
  fiscal_year_start_month: number
  invoice_series: string
  credit_note_series: string
  receipt_series: string
  software_certificate_number: string
  software_version: string
  default_tax_code: 'NOR' | 'ISE' | 'RED' | 'OUT'
  default_tax_percentage: number
  created_at: string
  updated_at: string
}

export interface TaxRate {
  id: number
  tax_code: 'NOR' | 'RED' | 'ISE' | 'OUT'
  tax_code_display: string
  description: string
  percentage: number
  valid_from: string
  valid_to?: string
  is_active: boolean
  status: string
  created_at: string
  updated_at: string
}

export const fiscalApi = {
  // ===== COMPANY SETTINGS =====

  /**
   * Get company settings (singleton)
   */
  async getCompanySettings(): Promise<CompanySettings> {
    const response = await api.get('/company-settings/')
    return response.data
  },

  /**
   * Update company settings
   */
  async updateCompanySettings(data: Partial<CompanySettings>): Promise<{ detail: string; data: CompanySettings }> {
    const response = await api.put('/company-settings/', data)
    return response.data
  },

  // ===== TAX RATES =====

  /**
   * List all tax rates
   * @param activeOnly - Filter only active rates
   * @param taxCode - Filter by specific tax code
   */
  async getTaxRates(activeOnly = false, taxCode?: string): Promise<TaxRate[]> {
    const params = new URLSearchParams()
    if (activeOnly) params.append('active_only', 'true')
    if (taxCode) params.append('tax_code', taxCode)

    const response = await api.get(`/tax-rates/?${params.toString()}`)
    return response.data
  },

  /**
   * Get a specific tax rate
   */
  async getTaxRate(id: number): Promise<TaxRate> {
    const response = await api.get(`/tax-rates/${id}/`)
    return response.data
  },

  /**
   * Create a new tax rate
   */
  async createTaxRate(data: Omit<TaxRate, 'id' | 'tax_code_display' | 'status' | 'created_at' | 'updated_at'>): Promise<{ detail: string; data: TaxRate }> {
    const response = await api.post('/tax-rates/', data)
    return response.data
  },

  /**
   * Update an existing tax rate
   */
  async updateTaxRate(id: number, data: Partial<TaxRate>): Promise<{ detail: string; data: TaxRate }> {
    const response = await api.put(`/tax-rates/${id}/`, data)
    return response.data
  },

  /**
   * Delete a tax rate
   */
  async deleteTaxRate(id: number): Promise<{ detail: string }> {
    const response = await api.delete(`/tax-rates/${id}/`)
    return response.data
  },

  /**
   * Get the currently active tax rate for a specific tax code
   * @param taxCode - Tax code (default: NOR)
   * @param asOfDate - Date in YYYY-MM-DD format (default: today)
   */
  async getActiveTaxRate(taxCode = 'NOR', asOfDate?: string): Promise<TaxRate> {
    const params = new URLSearchParams()
    params.append('tax_code', taxCode)
    if (asOfDate) params.append('as_of_date', asOfDate)

    const response = await api.get(`/tax-rates/active/?${params.toString()}`)
    return response.data
  }
}
