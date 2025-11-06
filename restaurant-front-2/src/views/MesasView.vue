<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Users, Search, Clock } from 'lucide-vue-next'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useTablesStore } from '@/stores/tables'
import { ordersApi } from '@/services/api'
import type { Table, Order } from '@/types/models'

const router = useRouter()
const tablesStore = useTablesStore()

// State
const isLoading = ref(false)
const orders = ref<Order[]>([])
const searchQuery = ref('')
const statusFilter = ref<'ALL' | 'AV' | 'OC' | 'RE'>('ALL')
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

// Cleanup flags
const isMounted = ref(true)
let refreshInterval: NodeJS.Timeout | null = null

// Status configuration
const statusConfig = {
  AV: {
    label: 'Disponível',
    cardClass: 'bg-green-50 dark:bg-green-950 border-l-4 border-green-500 hover:shadow-lg hover:scale-[1.02] transition-all cursor-pointer',
    badgeClass: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  },
  OC: {
    label: 'Ocupada',
    cardClass: 'bg-red-50 dark:bg-red-950 border-l-4 border-red-500 hover:shadow-lg hover:scale-[1.02] transition-all cursor-pointer',
    badgeClass: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  },
  RE: {
    label: 'Reservada',
    cardClass: 'bg-yellow-50 dark:bg-yellow-950 border-l-4 border-yellow-500 hover:shadow-lg hover:scale-[1.02] transition-all cursor-pointer',
    badgeClass: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  },
}

// Interface for table with order
interface TableWithOrder extends Table {
  currentOrder?: Order
}

// Computed: tables with their orders
const tablesWithOrders = computed<TableWithOrder[]>(() => {
  if (!isMounted.value) return []

  try {
    return tablesStore.tables.map(table => {
      // Find active order for this table (not PAID)
      const order = orders.value.find(
        o => o?.details?.table === table.tableid && o?.paymentStatus !== 'PAID'
      )
      return { ...table, currentOrder: order }
    })
  } catch (error) {
    console.error('Error computing tables with orders:', error)
    return []
  }
})

// Computed: filtered tables
const filteredTables = computed(() => {
  if (!isMounted.value) return []

  try {
    let result = tablesWithOrders.value

    // Filter by status
    if (statusFilter.value !== 'ALL') {
      result = result.filter(t => t.status === statusFilter.value)
    }

    // Filter by search
    if (searchQuery.value) {
      result = result.filter(t =>
        t.tableid.toString().includes(searchQuery.value)
      )
    }

    // Sort by table number
    result = [...result].sort((a, b) => a.tableid - b.tableid)

    return result
  } catch (error) {
    console.error('Error filtering tables:', error)
    return []
  }
})

// Computed: statistics
const stats = computed(() => {
  if (!isMounted.value) return { total: 0, available: 0, occupied: 0, reserved: 0 }

  try {
    const all = tablesStore.tables || []
    return {
      total: all.length,
      available: all.filter(t => t.status === 'AV').length,
      occupied: all.filter(t => t.status === 'OC').length,
      reserved: all.filter(t => t.status === 'RE').length,
    }
  } catch (error) {
    console.error('Error computing stats:', error)
    return { total: 0, available: 0, occupied: 0, reserved: 0 }
  }
})

// Methods
async function fetchData() {
  if (!isMounted.value) return

  isLoading.value = true
  try {
    // Fetch tables and orders in parallel
    await Promise.all([
      tablesStore.fetchTables(true),
      fetchOrders()
    ])
  } catch (error: any) {
    if (!isMounted.value) return // Don't update state if unmounted
    console.error('Error fetching data:', error)
    showToast('Erro ao carregar dados: ' + (error?.message || 'Erro desconhecido'), 'error')
  } finally {
    if (isMounted.value) {
      isLoading.value = false
    }
  }
}

async function fetchOrders() {
  if (!isMounted.value) return

  try {
    const fetchedOrders = await ordersApi.getOrders()
    if (isMounted.value) {
      orders.value = fetchedOrders
    }
  } catch (error: any) {
    console.error('Error fetching orders:', error)
    // Don't show error for orders - tables can still be displayed without orders
    if (isMounted.value) {
      orders.value = []
    }
  }
}

function getTimeElapsed(createdAt: string): string {
  try {
    const now = new Date()
    const created = new Date(createdAt)
    const diffMinutes = Math.floor((now.getTime() - created.getTime()) / 60000)

    if (diffMinutes < 60) return `há ${diffMinutes} min`
    const hours = Math.floor(diffMinutes / 60)
    return `há ${hours}h`
  } catch (error) {
    return 'há -- min'
  }
}

function navigateToTable(tableId: number) {
  try {
    router.push({ path: '/mesas/pedidos', query: { table: tableId } })
  } catch (error) {
    console.error('Navigation error:', error)
  }
}

function setStatusFilter(status: typeof statusFilter.value) {
  if (!isMounted.value) return
  statusFilter.value = status
}

function showToast(message: string, variant: 'success' | 'error') {
  if (!isMounted.value) return
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    if (isMounted.value) {
      toastMessage.value = null
    }
  }, 3000)
}

// Lifecycle
onMounted(async () => {
  isMounted.value = true

  try {
    await fetchData()

    // Auto-refresh every 30 seconds
    refreshInterval = setInterval(() => {
      if (isMounted.value) {
        fetchData()
      }
    }, 30000)
  } catch (error) {
    console.error('Mount error:', error)
  }
})

onUnmounted(() => {
  // Mark as unmounted first to prevent any state updates
  isMounted.value = false

  // Clear interval
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
})
</script>

<template>
  <div class="flex flex-col gap-6 p-6">
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
        <h1 class="text-3xl font-bold tracking-tight">Mesas</h1>
        <p class="text-muted-foreground mt-1">Visão geral das mesas do restaurante</p>
      </div>
      <Badge variant="secondary" class="text-lg px-4 py-2">
        {{ stats.total }} mesas
      </Badge>
    </div>

    <!-- Filters and Search -->
    <div class="flex flex-col sm:flex-row gap-4">
      <!-- Status Filter Buttons -->
      <div class="flex gap-2 flex-wrap">
        <Button
          :variant="statusFilter === 'ALL' ? 'default' : 'outline'"
          size="sm"
          @click="setStatusFilter('ALL')"
        >
          Todas ({{ stats.total }})
        </Button>
        <Button
          :variant="statusFilter === 'AV' ? 'default' : 'outline'"
          size="sm"
          @click="setStatusFilter('AV')"
        >
          Disponíveis ({{ stats.available }})
        </Button>
        <Button
          :variant="statusFilter === 'OC' ? 'default' : 'outline'"
          size="sm"
          @click="setStatusFilter('OC')"
        >
          Ocupadas ({{ stats.occupied }})
        </Button>
        <Button
          :variant="statusFilter === 'RE' ? 'default' : 'outline'"
          size="sm"
          @click="setStatusFilter('RE')"
        >
          Reservadas ({{ stats.reserved }})
        </Button>
      </div>

      <!-- Search -->
      <div class="relative flex-1 max-w-sm">
        <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          v-model="searchQuery"
          placeholder="Pesquisar por número de mesa..."
          class="pl-9"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card v-for="i in 8" :key="i" class="h-48">
        <CardContent class="p-6">
          <Skeleton class="h-8 w-24 mb-4" />
          <Skeleton class="h-4 w-32 mb-2" />
          <Skeleton class="h-4 w-24" />
        </CardContent>
      </Card>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredTables.length === 0" class="text-center py-12 border rounded-lg">
      <p class="text-muted-foreground text-lg">Nenhuma mesa encontrada</p>
      <p class="text-sm text-muted-foreground mt-2">
        {{ statusFilter !== 'ALL' ? 'Tente ajustar os filtros' : 'Adicione mesas nas configurações' }}
      </p>
    </div>

    <!-- Tables Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card
        v-for="table in filteredTables"
        :key="table.tableid"
        :class="statusConfig[table.status]?.cardClass || 'border'"
        @click="navigateToTable(table.tableid)"
      >
        <CardHeader class="pb-3">
          <div class="flex items-start justify-between">
            <CardTitle class="text-2xl font-bold">Mesa {{ table.tableid }}</CardTitle>
            <Badge :class="statusConfig[table.status]?.badgeClass || ''">
              {{ statusConfig[table.status]?.label || table.status }}
            </Badge>
          </div>
        </CardHeader>
        <CardContent class="space-y-3">
          <!-- Capacity -->
          <div class="flex items-center gap-2 text-sm">
            <Users class="h-4 w-4 text-muted-foreground" />
            <span>{{ table.capacity }} pessoas</span>
          </div>

          <!-- Order Info (only for occupied tables) -->
          <div v-if="table.currentOrder" class="space-y-2 pt-2 border-t">
            <div class="flex items-center justify-between text-sm">
              <span class="text-muted-foreground">Pedido:</span>
              <span class="font-semibold">#{{ table.currentOrder.orderID }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-muted-foreground">Total:</span>
              <span class="font-bold text-lg">€{{ table.currentOrder.grandTotal?.toFixed(2) || '0.00' }}</span>
            </div>
            <div class="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock class="h-3 w-3" />
              <span>{{ getTimeElapsed(table.currentOrder.created_at) }}</span>
            </div>
          </div>

          <!-- Empty message for available tables -->
          <div v-else-if="table.status === 'AV'" class="pt-2 border-t">
            <p class="text-xs text-muted-foreground text-center">Clique para criar pedido</p>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

