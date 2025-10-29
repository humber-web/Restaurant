import { defineStore } from 'pinia'
import { ref, onMounted, onUnmounted } from 'vue'
import { ordersApi } from '@/services/api'
import { orderWebSocket } from '@/services/websocket/orders'
import type { Order, CreateOrderPayload } from '@/types/models'

export const useOrdersStore = defineStore('orders', () => {
  const orders = ref<Order[]>([])
  const currentOrder = ref<Order | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  let unsubscribe: (() => void) | null = null

  function initWebSocket() {
    orderWebSocket.connect()

    unsubscribe = orderWebSocket.subscribe((data) => {
      console.log('Order update received:', data)
      
      // Update orders list
      const index = orders.value.findIndex((o) => o.orderID === data.order.orderID)
      if (index !== -1) {
        orders.value[index] = data.order
      } else {
        orders.value.unshift(data.order)
      }

      // Update current order if it matches
      if (currentOrder.value?.orderID === data.order.orderID) {
        currentOrder.value = data.order
      }
    })
  }

  function closeWebSocket() {
    if (unsubscribe) {
      unsubscribe()
      unsubscribe = null
    }
    orderWebSocket.disconnect()
  }

  async function fetchOrders() {
    isLoading.value = true
    error.value = null

    try {
      orders.value = await ordersApi.getOrders()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchOrder(id: number) {
    isLoading.value = true
    error.value = null

    try {
      currentOrder.value = await ordersApi.getOrder(id)
      return currentOrder.value
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createOrder(data: CreateOrderPayload) {
    isLoading.value = true
    error.value = null

    try {
      const newOrder = await ordersApi.createOrder(data)
      orders.value.unshift(newOrder)
      
      // Broadcast via WebSocket
      orderWebSocket.send('Order created', newOrder)
      
      return newOrder
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateOrder(id: number, data: Partial<Order>) {
    isLoading.value = true
    error.value = null

    try {
      const updated = await ordersApi.updateOrder(id, data)
      const index = orders.value.findIndex((o) => o.orderID === id)
      if (index !== -1) {
        orders.value[index] = updated
      }
      
      // Broadcast via WebSocket
      orderWebSocket.send('Order updated', updated)
      
      return updated
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteOrder(id: number) {
    isLoading.value = true
    error.value = null

    try {
      await ordersApi.deleteOrder(id)
      orders.value = orders.value.filter((o) => o.orderID !== id)
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    orders,
    currentOrder,
    isLoading,
    error,
    initWebSocket,
    closeWebSocket,
    fetchOrders,
    fetchOrder,
    createOrder,
    updateOrder,
    deleteOrder,
  }
})
