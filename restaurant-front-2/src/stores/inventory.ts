import { defineStore } from 'pinia'
import { ref } from 'vue'
import { inventoryApi } from '@/services/api'
import type { InventoryItem } from '@/types/models'

export const useInventoryStore = defineStore('inventory', () => {
  const items = ref<InventoryItem[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchItems(force = false) {
    // Smart fetching: skip if already loaded (unless forced)
    if (!force && items.value.length > 0) {
      return
    }

    isLoading.value = true
    error.value = null

    try {
      items.value = await inventoryApi.getItems()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createItem(data: Omit<InventoryItem, 'itemID'>) {
    isLoading.value = true
    error.value = null

    try {
      const newItem = await inventoryApi.createItem(data)
      items.value.push(newItem)
      return newItem
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateItem(id: number, data: Partial<InventoryItem>) {
    isLoading.value = true
    error.value = null

    try {
      const updated = await inventoryApi.updateItem(id, data)
      const index = items.value.findIndex((item) => item.itemID === id)
      if (index !== -1) {
        items.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteItem(id: number) {
    isLoading.value = true
    error.value = null

    try {
      await inventoryApi.deleteItem(id)
      items.value = items.value.filter((item) => item.itemID !== id)
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    items,
    isLoading,
    error,
    fetchItems,
    createItem,
    updateItem,
    deleteItem,
  }
})
