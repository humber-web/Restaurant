export interface ApiResponse<T> {
  data: T
  status: number
  message?: string
}

export interface ApiError {
  message: string
  errors?: Record<string, string[]>
  status: number
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterUserPayload {
  username: string
  email: string
  password: string
  group?: string
}
