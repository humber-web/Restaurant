export interface User {
  id: number
  username: string
  email: string
  groups: number[]
  first_name?: string
  last_name?: string
  is_active?: boolean
  is_staff?: boolean
  is_superuser?: boolean
  date_joined?: string
  last_login?: string | null
}

export interface Profile {
  user: number
  bio: string
  location: string
}

export interface Group {
  id: number
  name: string
}
