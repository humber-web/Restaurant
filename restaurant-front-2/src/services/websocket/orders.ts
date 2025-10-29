import type { Order } from '@/types/models'

type OrderUpdateCallback = (data: { message: string; order: Order }) => void

class OrderWebSocketService {
  private ws: WebSocket | null = null
  private callbacks: Set<OrderUpdateCallback> = new Set()
  private reconnectTimeout: number | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect() {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/orders/'

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.callbacks.forEach((callback) => callback(data))
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.attemptReconnect()
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      this.attemptReconnect()
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`)

    this.reconnectTimeout = window.setTimeout(() => {
      this.connect()
    }, delay)
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.callbacks.clear()
  }

  subscribe(callback: OrderUpdateCallback) {
    this.callbacks.add(callback)

    return () => {
      this.callbacks.delete(callback)
    }
  }

  send(message: string, order: Order) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ message, order }))
    } else {
      console.warn('WebSocket is not connected')
    }
  }
}

export const orderWebSocket = new OrderWebSocketService()
