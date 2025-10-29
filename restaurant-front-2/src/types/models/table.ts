export type TableStatus = 'AV' | 'OC' | 'RE'

export interface Table {
  tableid: number
  capacity: number
  status: TableStatus
}
