import { defineStore } from 'pinia'
import { ref } from 'vue'
import { menuApi } from '@/services/api'
import type { MenuCategory, MenuItem } from '@/types/models'

export const useMenuStore = defineStore('menu', () => {
  const categories = ref<MenuCategory[]>([])
  const items = ref<MenuItem[]>([])
  const itemsByCategory = ref<Record<string, MenuItem[]>>({})
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchCategories() {
    isLoading.value = true
    error.value = null

    try {
      categories.value = await menuApi.getCategories()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchItems() {
    isLoading.value = true
    error.value = null

    try {
      items.value = await menuApi.getItems()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchItemsByCategory() {
    isLoading.value = true
    error.value = null

    try {
      itemsByCategory.value = await menuApi.getItemsByCategory()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createCategory(data: Omit<MenuCategory, 'categoryID'>) {
    isLoading.value = true
    error.value = null

    try {
      const newCategory = await menuApi.createCategory(data)
      categories.value.push(newCategory)
      return newCategory
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createItem(data: Omit<MenuItem, 'itemID'>) {
    isLoading.value = true
    error.value = null

    try {
      const newItem = await menuApi.createItem(data)
      items.value.push(newItem)
      return newItem
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateItem(id: number, data: Partial<MenuItem>) {
    isLoading.value = true
    error.value = null

    try {
      const updated = await menuApi.updateItem(id, data)
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
      await menuApi.deleteItem(id)
      items.value = items.value.filter((item) => item.itemID !== id)
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    categories,
    items,
    itemsByCategory,
    isLoading,
    error,
    fetchCategories,
    fetchItems,
    fetchItemsByCategory,
    createCategory,
    createItem,
    updateItem,
    deleteItem,
  }
})
