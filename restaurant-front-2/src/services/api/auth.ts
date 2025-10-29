import { api, apiClient } from './client'
import type { LoginPayload, RegisterUserPayload, AuthTokens } from '@/types/api'
import type { User } from '@/types/models'

export const authApi = {
  async login(payload: LoginPayload): Promise<AuthTokens & { user: User }> {
    const response = await api.post('/login/', payload)
    const { access, refresh, user } = response.data
    
    apiClient.setAuthToken(access)
    apiClient.setRefreshToken(refresh)
    
    return response.data
  },

  async registerCustomer(payload: RegisterUserPayload): Promise<{ user: User } & AuthTokens> {
    const response = await api.post('/register/customer/', payload)
    const { access, refresh } = response.data
    
    if (access && refresh) {
      apiClient.setAuthToken(access)
      apiClient.setRefreshToken(refresh)
    }
    
    return response.data
  },

  async registerUser(payload: RegisterUserPayload): Promise<{ user: User }> {
    const response = await api.post('/register/', payload)
    return response.data
  },

  logout() {
    apiClient.clearTokens()
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/user/me/')
    return response.data
  },
}
