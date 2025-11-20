import axios, { type AxiosInstance, AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiError } from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token')
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor - handle errors and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

        // Handle 401 Unauthorized - try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
                refresh: refreshToken,
              })

              const { access } = response.data
              localStorage.setItem('access_token', access)

              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${access}`
              }

              return this.client(originalRequest)
            }
          } catch (refreshError) {
            // Refresh failed - clear tokens and redirect to login
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        // Format error
        const apiError: ApiError = {
          message: error.response?.data?.message || error.message || 'An error occurred',
          errors: error.response?.data?.errors,
          status: error.response?.status || 500,
        }

        return Promise.reject(apiError)
      }
    )
  }

  public getClient(): AxiosInstance {
    return this.client
  }

  // Helper methods
  public setAuthToken(token: string) {
    localStorage.setItem('access_token', token)
  }

  public setRefreshToken(token: string) {
    localStorage.setItem('refresh_token', token)
  }

  public clearTokens() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  public getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }
}

export const apiClient = new ApiClient()
export const api = apiClient.getClient()
