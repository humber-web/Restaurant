<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { tablesApi, type Table } from '@/services/api'
import { useOrdersStore } from '@/stores/orders'
import type { Order } from '@/types/models'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import {
  CreditCard,
  Users,
  Search,
  Clock,
} from 'lucide-vue-next'

const router = useRouter()
const ordersStore = useOrdersStore()

// State
const tables = ref<Table[]>([])
const isLoading = ref(true)
const isMounted = ref(true)
const searchQuery = ref('')

// Toast notifications
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

function showToast(message: string, variant: 'success' | 'error' = 'success') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

// Computed: Orders with pending payments
const pendingOrders = computed(() => {
  if (!isMounted.value) return []
  return ordersStore.orders.filter(order =>
    order.paymentStatus !== 'PAID' &&
    order.status !== 'CANCELLED'
  )
})

// Computed: Filtered pending orders
const filteredOrders = computed(() => {
  if (!searchQuery.value) return pendingOrders.value

  const query = searchQuery.value.toLowerCase()
  return pendingOrders.value.filter(order => {
    const orderNum = order.orderID.toString()
    const tableNum = order.details?.table?.toString() || ''
    return orderNum.includes(query) || tableNum.includes(query)
  })
})

// Get table info for an order
function getTableInfo(order: Order): Table | undefined {
  const tableId = order.details?.table
  if (!tableId) return undefined
  return tables.value.find(t => t.tableid === tableId)
}

// Format date/time helper
function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Calculate time elapsed
function timeElapsed(dateStr: string): string {
  const created = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - created.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 60) {
    return `${diffMins} min`
  }

  const diffHours = Math.floor(diffMins / 60)
  const remainingMins = diffMins % 60
  return `${diffHours}h ${remainingMins}m`
}

// Navigate to payment processing
function processPayment(order: Order) {
  router.push({ path: '/pagamentos/processar', query: { order: order.orderID } })
}

// Payment status config
const paymentStatusConfig: Record<string, { label: string; variant: any }> = {
  PENDING: { label: 'Pendente', variant: 'destructive' },
  PARTIALLY_PAID: { label: 'Parcialmente Pago', variant: 'secondary' },
}

// Order status config
const orderStatusConfig: Record<string, { label: string; variant: any }> = {
  PENDING: { label: 'Pendente', variant: 'secondary' },
  PREPARING: { label: 'A Preparar', variant: 'default' },
  READY: { label: 'Pronto', variant: 'default' },
  DELIVERED: { label: 'Entregue', variant: 'outline' },
}

// Fetch data
async function fetchData() {
  isLoading.value = true
  try {
    const [tablesData] = await Promise.all([
      tablesApi.getTables(),
      ordersStore.fetchOrders()
    ])

    if (!isMounted.value) return

    tables.value = tablesData
  } catch (error: any) {
    if (!isMounted.value) return
    showToast(error.message || 'Erro ao carregar dados', 'error')
  } finally {
    if (isMounted.value) {
      isLoading.value = false
    }
  }
}

onMounted(() => {
  ordersStore.initWebSocket()
  fetchData()
})

onUnmounted(() => {
  isMounted.value = false
  ordersStore.closeWebSocket()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      class="fixed top-4 right-4 z-50 rounded-lg border px-4 py-3 shadow-lg transition-all"
      :class="toastVariant === 'success' ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'"
    >
      {{ toastMessage }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">Pagamentos</h1>
        <p class="text-sm text-muted-foreground">Processar pagamentos de pedidos pendentes</p>
      </div>
      <Badge variant="secondary" class="text-lg px-4 py-2">
        {{ filteredOrders.length }} {{ filteredOrders.length === 1 ? 'Pedido' : 'Pedidos' }}
      </Badge>
    </div>

    <!-- Search Bar -->
    <div class="relative max-w-md">
      <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <Input
        v-model="searchQuery"
        placeholder="Buscar por nº pedido ou mesa..."
        class="pl-9"
      />
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <Skeleton v-for="i in 6" :key="i" class="h-48 w-full" />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredOrders.length === 0" class="flex-1 flex items-center justify-center">
      <Card class="w-full max-w-md">
        <CardContent class="pt-6">
          <div class="flex flex-col items-center text-center space-y-4">
            <div class="rounded-full bg-muted p-3">
              <CreditCard class="h-12 w-12 text-muted-foreground" />
            </div>
            <div>
              <h2 class="text-xl font-semibold mb-2">Nenhum Pagamento Pendente</h2>
              <p class="text-sm text-muted-foreground">
                {{ searchQuery ? 'Nenhum resultado encontrado para a sua busca.' : 'Todos os pedidos foram pagos.' }}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Orders Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-6">
      <Card
        v-for="order in filteredOrders"
        :key="order.orderID"
        class="hover:shadow-lg transition-shadow cursor-pointer"
        @click="processPayment(order)"
      >
        <CardHeader class="pb-3">
          <div class="flex items-start justify-between">
            <div>
              <CardTitle class="text-lg">Pedido #{{ order.orderID }}</CardTitle>
              <div class="flex items-center gap-2 mt-1">
                <Users class="h-4 w-4 text-muted-foreground" />
                <span class="text-sm text-muted-foreground">
                  Mesa {{ order.details?.table || 'N/A' }}
                </span>
              </div>
            </div>
            <Badge :variant="paymentStatusConfig[order.paymentStatus]?.variant">
              {{ paymentStatusConfig[order.paymentStatus]?.label }}
            </Badge>
          </div>
        </CardHeader>

        <CardContent class="space-y-3">
          <!-- Order Info -->
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-muted-foreground">Status:</span>
              <Badge :variant="orderStatusConfig[order.status]?.variant" class="text-xs">
                {{ orderStatusConfig[order.status]?.label }}
              </Badge>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-muted-foreground">Itens:</span>
              <span class="font-medium">{{ order.items.length }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <Clock class="h-3 w-3 text-muted-foreground" />
              <span class="text-muted-foreground">{{ timeElapsed(order.created_at) }}</span>
            </div>
          </div>

          <!-- Divider -->
          <div class="border-t pt-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium">Total a Pagar:</span>
              <span class="text-2xl font-bold text-primary">
                CVE{{ Number(order.grandTotal || 0).toFixed(2) }}
              </span>
            </div>
          </div>

          <!-- Action Button -->
          <Button class="w-full" size="lg">
            <CreditCard class="mr-2 h-4 w-4" />
            Processar Pagamento
          </Button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
