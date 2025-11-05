import { api } from './client'
import type { User, Group } from '@/types/models'

export interface CreateUserPayload {
  username: string
  email: string
  password: string
  group?: string
}

export const usersApi = {
  async getUsers(): Promise<User[]> {
    const response = await api.get('/user/')
    return response.data
  },

  async getUser(id: number): Promise<User> {
    const response = await api.get(`/user/${id}/`)
    return response.data
  },

  async createUser(data: CreateUserPayload): Promise<User> {
    const payload = {
      ...data,
      model: 'user',
      operation: 'CREATE',
    }
    const response = await api.post('/register/', payload)
    return response.data.user
  },

  async updateUser(id: number, data: Partial<User>): Promise<User> {
    const payload = {
      ...data,
      model: 'user',
      operation: 'UPDATE',
      object_id: String(id)
    }
    const response = await api.put(`/user/${id}/update/`, payload)
    return response.data.user
  },

  async deleteUser(id: number): Promise<void> {
    await api.delete(`/user/${id}/delete/`)
  },

  async getGroups(): Promise<Group[]> {
    const response = await api.get('/groups/')
    return response.data
  },
}
