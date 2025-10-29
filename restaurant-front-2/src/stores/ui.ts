import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Toast {
  id: string
  title: string
  description?: string
  variant?: 'default' | 'destructive' | 'success'
  duration?: number
}

export const useUIStore = defineStore('ui', () => {
  const toasts = ref<Toast[]>([])
  const isSidebarOpen = ref(true)
  const isLoading = ref(false)

  function showToast(toast: Omit<Toast, 'id'>) {
    const id = Math.random().toString(36).substring(7)
    const newToast: Toast = { id, ...toast }
    
    toasts.value.push(newToast)

    // Auto-remove after duration
    const duration = toast.duration || 3000
    setTimeout(() => {
      removeToast(id)
    }, duration)

    return id
  }

  function removeToast(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function toggleSidebar() {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  return {
    toasts,
    isSidebarOpen,
    isLoading,
    showToast,
    removeToast,
    toggleSidebar,
    setLoading,
  }
})
