export type ActionType = 'CREATE' | 'UPDATE' | 'DELETE'

export interface OperationLog {
  id: number
  user: number
  username: string
  user_email: string
  action: ActionType
  content_type: number
  model_name: string
  object_id: number
  object_repr: string
  change_message: string
  timestamp: string
}
