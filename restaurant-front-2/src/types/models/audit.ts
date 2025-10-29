export type ActionType = 'CREATE' | 'UPDATE' | 'DELETE'

export interface OperationLog {
  id: number
  user: number
  action: ActionType
  content_type: number
  object_id: number
  object_repr: string
  change_message: string
  timestamp: string
}
