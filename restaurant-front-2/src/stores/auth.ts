import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services/api'
import type { User } from '@/types/models'
import type { LoginPayload, RegisterUserPayload } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = computed(() => !!user.value)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function login(payload: LoginPayload) {
    isLoading.value = true
    error.value = null

    try {
      const data = await authApi.login(payload)
      user.value = data.user
      return data
    } catch (err: any) {
      error.value = err.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function registerCustomer(payload: RegisterUserPayload) {
    isLoading.value = true
    error.value = null

    try {
      const data = await authApi.registerCustomer(payload)
      user.value = data.user
      return data
    } catch (err: any) {
      error.value = err.message || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCurrentUser() {
    isLoading.value = true
    error.value = null

    try {
      user.value = await authApi.getCurrentUser()
    } catch (err: any) {
      error.value = err.message
      user.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    authApi.logout()
    user.value = null
  }

  function isManager() {
    // Check if user is staff, superuser, or in manager group (ID 1)
    return user.value?.is_staff === true ||
           user.value?.is_superuser === true ||
           user.value?.groups.some((group) => group === 1)
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    registerCustomer,
    fetchCurrentUser,
    logout,
    isManager,
  }
})
