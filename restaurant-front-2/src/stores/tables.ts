import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tablesApi } from '@/services/api'
import type { Table } from '@/types/models'

export const useTablesStore = defineStore('tables', () => {
  const tables = ref<Table[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const availableTables = computed(() =>
    tables.value.filter((table) => table.status === 'AV')
  )

  const occupiedTables = computed(() =>
    tables.value.filter((table) => table.status === 'OC')
  )

  async function fetchTables(force = false) {
    // Smart fetching: skip if already loaded (unless forced)
    if (!force && tables.value.length > 0) {
      return
    }

    isLoading.value = true
    error.value = null

    try {
      tables.value = await tablesApi.getTables()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createTable(data: Omit<Table, 'tableid'>) {
    isLoading.value = true
    error.value = null

    try {
      const newTable = await tablesApi.createTable(data)
      tables.value.push(newTable)
      return newTable
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateTable(id: number, data: Partial<Table>) {
    isLoading.value = true
    error.value = null

    try {
      const updated = await tablesApi.updateTable(id, data)
      const index = tables.value.findIndex((t) => t.tableid === id)
      if (index !== -1) {
        tables.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteTable(id: number) {
    isLoading.value = true
    error.value = null

    try {
      await tablesApi.deleteTable(id)
      tables.value = tables.value.filter((t) => t.tableid !== id)
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    tables,
    availableTables,
    occupiedTables,
    isLoading,
    error,
    fetchTables,
    createTable,
    updateTable,
    deleteTable,
  }
})
