export interface CashRegister {
  id: number
  user: number
  initial_amount: number
  final_amount?: number
  operations_cash: number
  operations_card: number
  operations_transfer: number
  operations_other: number
  operations_check: number
  start_time: string
  end_time?: string
  is_open: boolean
}

export interface StartCashRegisterPayload {
  initial_amount: number
}

export interface CloseCashRegisterPayload {
  declared_cash: number
  declared_card: number
}

export interface InsertMoneyPayload {
  amount: number
}

export interface ExtractMoneyPayload {
  amount: number
}

export interface CashRegisterSummary {
  initial_amount: number
  operations_cash: number
  operations_card: number
  operations_other: number
  final_amount: number
  start_time: string
  end_time?: string
  expected_cash?: number
  declared_cash?: number
  cash_difference?: number
  expected_card?: number
  declared_card?: number
  card_difference?: number
}
