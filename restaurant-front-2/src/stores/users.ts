import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usersApi, type CreateUserPayload } from '@/services/api'
import type { User, Group } from '@/types/models'

export const useUsersStore = defineStore('users', () => {
  const users = ref<User[]>([])
  const groups = ref<Group[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchUsers(force = false) {
    // Smart fetching: skip if already loaded (unless forced)
    if (!force && users.value.length > 0) {
      return
    }

    isLoading.value = true
    error.value = null

    try {
      users.value = await usersApi.getUsers()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchGroups(force = false) {
    // Smart fetching: skip if already loaded (unless forced)
    if (!force && groups.value.length > 0) {
      return
    }

    isLoading.value = true
    error.value = null

    try {
      groups.value = await usersApi.getGroups()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createUser(data: CreateUserPayload) {
    isLoading.value = true
    error.value = null

    try {
      const newUser = await usersApi.createUser(data)
      users.value.push(newUser)
      return newUser
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateUser(id: number, data: Partial<User>) {
    isLoading.value = true
    error.value = null

    try {
      const updated = await usersApi.updateUser(id, data)
      const index = users.value.findIndex((user) => user.id === id)
      if (index !== -1) {
        users.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteUser(id: number) {
    isLoading.value = true
    error.value = null

    try {
      await usersApi.deleteUser(id)
      users.value = users.value.filter((user) => user.id !== id)
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    users,
    groups,
    isLoading,
    error,
    fetchUsers,
    fetchGroups,
    createUser,
    updateUser,
    deleteUser,
  }
})
