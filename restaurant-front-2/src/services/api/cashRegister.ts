import { api } from './client'
import type {
  CashRegister,
  CashRegisterSummary,
  StartCashRegisterPayload,
  CloseCashRegisterPayload,
  InsertMoneyPayload,
  ExtractMoneyPayload,
} from '@/types/models'

export const cashRegisterApi = {
  async start(data: StartCashRegisterPayload): Promise<CashRegister> {
    const response = await api.post('/cash_register/start/', data)
    return response.data
  },

  async close(data: CloseCashRegisterPayload): Promise<CashRegisterSummary> {
    const response = await api.post('/cash_register/close/', data)
    // Backend returns data nested under 'results' key, extract it
    return response.data.results as CashRegisterSummary
  },

  async getSummary(): Promise<CashRegisterSummary> {
    const response = await api.get('/cash_register/summary/')
    return response.data
  },

  async getOpenRegister(): Promise<CashRegister | null> {
    try {
      const response = await api.get('/cash_register/?is_open=true')
      const registers = response.data
      return registers.length > 0 ? registers[0] : null
    } catch {
      return null
    }
  },

  async insertMoney(data: InsertMoneyPayload): Promise<void> {
    await api.post('/cash_register/insert_money/', data)
  },

  async extractMoney(data: ExtractMoneyPayload): Promise<void> {
    await api.post('/cash_register/extract_money/', data)
  },
}
