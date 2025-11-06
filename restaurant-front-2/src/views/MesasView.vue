<<<<<<< HEAD
<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950">
    <!-- Header with Stats -->
    <div class="sticky top-0 z-40 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 backdrop-blur">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <!-- Title -->
        <div class="mb-4">
          <h1 class="text-3xl font-bold text-slate-900 dark:text-white">Tables</h1>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-3 gap-4 mb-6">
          <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
            <div class="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <div>
              <p class="text-xs font-medium text-slate-600 dark:text-slate-400">Available</p>
              <p class="text-xl font-bold text-slate-900 dark:text-white">{{ availableCount }}</p>
            </div>
          </div>

          <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
            <div class="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="text-xs font-medium text-slate-600 dark:text-slate-400">Occupied</p>
              <p class="text-xl font-bold text-slate-900 dark:text-white">{{ occupiedCount }}</p>
            </div>
          </div>

          <div class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
            <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <p class="text-xs font-medium text-slate-600 dark:text-slate-400">Reserved</p>
              <p class="text-xl font-bold text-slate-900 dark:text-white">{{ reservedCount }}</p>
            </div>
          </div>
        </div>

        <!-- Search and Filter -->
        <div class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
          <div class="flex-1 relative">
            <svg class="absolute left-3 top-3 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search table or customer..."
              class="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <!-- Filter Buttons -->
          <div class="flex gap-2">
            <button
              @click="selectedStatus = null"
              :class="[
                'px-4 py-2 rounded-lg font-medium text-sm transition-colors',
                !selectedStatus
                  ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900'
                  : 'bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-100 hover:bg-slate-300 dark:hover:bg-slate-600'
              ]"
            >
              All
            </button>
            <button
              v-for="status in statusOptions"
              :key="status.value"
              @click="selectedStatus = selectedStatus === status.value ? null : status.value"
              :class="[
                'px-4 py-2 rounded-lg font-medium text-sm transition-colors',
                selectedStatus === status.value
                  ? `${status.bgActive} ${status.textActive}`
                  : `${status.bgInactive} ${status.textInactive} hover:opacity-80`
              ]"
            >
              {{ status.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tables Grid -->
    <div class="max-w-7xl mx-auto px-6 py-8">
      <div v-if="filteredTables.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div
          v-for="table in filteredTables"
          :key="table.id"
          @click="selectTable(table)"
          :class="[
            'group cursor-pointer rounded-xl border-2 transition-all duration-200',
            table.status === 'available'
              ? 'border-emerald-200 dark:border-emerald-900 bg-white dark:bg-slate-900 hover:border-emerald-400 dark:hover:border-emerald-700 hover:shadow-lg'
              : table.status === 'occupied'
              ? 'border-orange-200 dark:border-orange-900 bg-white dark:bg-slate-900 hover:border-orange-400 dark:hover:border-orange-700 hover:shadow-lg'
              : 'border-blue-200 dark:border-blue-900 bg-white dark:bg-slate-900 hover:border-blue-400 dark:hover:border-blue-700 hover:shadow-lg'
          ]"
        >
          <!-- Card Header -->
          <div class="p-4 border-b border-slate-200 dark:border-slate-700 flex items-start justify-between">
            <div>
              <p class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">Table</p>
              <h3 class="text-2xl font-bold text-slate-900 dark:text-white">{{ table.number }}</h3>
            </div>
            <span :class="[
              'px-2 py-1 rounded-full text-xs font-semibold',
              table.status === 'available'
                ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300'
                : table.status === 'occupied'
                ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300'
                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
            ]">
              {{ getStatusLabel(table.status) }}
            </span>
          </div>

          <!-- Card Body -->
          <div class="p-4 space-y-3">
            <!-- Capacity -->
            <div class="flex items-center gap-2 text-sm">
              <svg class="w-4 h-4 text-slate-500 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span class="text-slate-600 dark:text-slate-400">{{ table.capacity }} seats</span>
            </div>

            <!-- Customer Info -->
            <div v-if="table.status !== 'available'" class="bg-slate-50 dark:bg-slate-800 rounded-lg p-3">
              <p class="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase mb-1">Customer</p>
              <p class="text-sm font-semibold text-slate-900 dark:text-white">{{ table.customerName }}</p>
              <p v-if="table.checkInTime" class="text-xs text-slate-500 dark:text-slate-400 mt-1">
                {{ formatTime(table.checkInTime) }}
              </p>
            </div>

            <!-- Notes -->
            <div v-if="table.notes" class="text-sm text-slate-600 dark:text-slate-300 italic">
              "{{ table.notes }}"
            </div>
          </div>

          <!-- Card Footer - Actions -->
          <div class="p-4 border-t border-slate-200 dark:border-slate-700 flex gap-2">
            <button
              v-if="table.status === 'available'"
              @click.stop="startReservation(table)"
              class="flex-1 px-3 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Reserve
            </button>
            <button
              v-else-if="table.status === 'occupied'"
              @click.stop="requestBill(table)"
              class="flex-1 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Bill
            </button>
            <button
              v-if="table.status !== 'available'"
              @click.stop="freeTable(table)"
              class="flex-1 px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              Clear
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <svg class="w-16 h-16 mx-auto text-slate-400 dark:text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p class="text-slate-600 dark:text-slate-400 text-lg font-medium">No tables found</p>
      </div>
    </div>

    <!-- Reserve Modal -->
    <div v-if="showReserveModal && selectedTableData" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-6 w-full max-w-md shadow-xl">
        <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6">Reserve Table {{ selectedTableData.number }}</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Customer Name</label>
            <input
              v-model="reservationData.customerName"
              type="text"
              placeholder="Enter customer name"
              class="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Notes (Optional)</label>
            <textarea
              v-model="reservationData.notes"
              placeholder="Special requests or allergies..."
              class="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
            ></textarea>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              @click="confirmReservation"
              class="flex-1 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium transition-colors"
            >
              Confirm
            </button>
            <button
              @click="showReserveModal = false"
              class="flex-1 px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white rounded-lg font-medium hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
=======
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
  return tablesStore.tables.map(table => {
    // Find active order for this table (not PAID)
    const order = orders.value.find(
      o => o.details.table === table.tableid && o.paymentStatus !== 'PAID'
    )
    return { ...table, currentOrder: order }
  })
})

// Computed: filtered tables
const filteredTables = computed(() => {
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
})

// Computed: statistics
const stats = computed(() => {
  const all = tablesStore.tables
  return {
    total: all.length,
    available: all.filter(t => t.status === 'AV').length,
    occupied: all.filter(t => t.status === 'OC').length,
    reserved: all.filter(t => t.status === 'RE').length,
  }
})

// Methods
async function fetchData() {
  isLoading.value = true
  try {
    // Fetch tables and orders in parallel
    await Promise.all([
      tablesStore.fetchTables(true),
      fetchOrders()
    ])
  } catch (error: any) {
    showToast('Erro ao carregar dados', 'error')
    console.error('Error fetching data:', error)
  } finally {
    isLoading.value = false
  }
}

async function fetchOrders() {
  try {
    orders.value = await ordersApi.getOrders()
  } catch (error) {
    console.error('Error fetching orders:', error)
  }
}

function getTimeElapsed(createdAt: string): string {
  const now = new Date()
  const created = new Date(createdAt)
  const diffMinutes = Math.floor((now.getTime() - created.getTime()) / 60000)

  if (diffMinutes < 60) return `há ${diffMinutes} min`
  const hours = Math.floor(diffMinutes / 60)
  return `há ${hours}h`
}

function navigateToTable(tableId: number) {
  router.push({ path: '/mesas/pedidos', query: { table: tableId } })
}

function setStatusFilter(status: typeof statusFilter.value) {
  statusFilter.value = status
}

function showToast(message: string, variant: 'success' | 'error') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

// Lifecycle
onMounted(async () => {
  await fetchData()

  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(fetchData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
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
        :class="statusConfig[table.status].cardClass"
        @click="navigateToTable(table.tableid)"
      >
        <CardHeader class="pb-3">
          <div class="flex items-start justify-between">
            <CardTitle class="text-2xl font-bold">Mesa {{ table.tableid }}</CardTitle>
            <Badge :class="statusConfig[table.status].badgeClass">
              {{ statusConfig[table.status].label }}
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
              <span class="font-bold text-lg">€{{ table.currentOrder.grandTotal.toFixed(2) }}</span>
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
>>>>>>> a6637d53ad48b50e95f116d28f52da53aa7f3c28
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// State
const tables = ref([
  { id: 1, number: 1, capacity: 4, status: 'available', customerName: '', checkInTime: null, notes: '' },
  { id: 2, number: 2, capacity: 6, status: 'occupied', customerName: 'John Smith', checkInTime: new Date(Date.now() - 45 * 60000), notes: 'Window seat preference' },
  { id: 3, number: 3, capacity: 2, status: 'reserved', customerName: 'Sarah Johnson', checkInTime: null, notes: '' },
  { id: 4, number: 4, capacity: 4, status: 'available', customerName: '', checkInTime: null, notes: '' },
  { id: 5, number: 5, capacity: 8, status: 'occupied', customerName: 'Michael Brown', checkInTime: new Date(Date.now() - 20 * 60000), notes: 'Birthday celebration' },
  { id: 6, number: 6, capacity: 4, status: 'available', customerName: '', checkInTime: null, notes: '' },
])

const searchQuery = ref('')
const selectedStatus = ref(null)
const selectedTableData = ref(null)
const showReserveModal = ref(false)

const reservationData = ref({ customerName: '', notes: '' })

const statusOptions = [
  { value: 'available', label: 'Available', bgActive: 'bg-emerald-500', textActive: 'text-white', bgInactive: 'bg-emerald-100 dark:bg-emerald-900/30', textInactive: 'text-emerald-700 dark:text-emerald-300' },
  { value: 'occupied', label: 'Occupied', bgActive: 'bg-orange-500', textActive: 'text-white', bgInactive: 'bg-orange-100 dark:bg-orange-900/30', textInactive: 'text-orange-700 dark:text-orange-300' },
  { value: 'reserved', label: 'Reserved', bgActive: 'bg-blue-500', textActive: 'text-white', bgInactive: 'bg-blue-100 dark:bg-blue-900/30', textInactive: 'text-blue-700 dark:text-blue-300' },
]

// Computed
const filteredTables = computed(() => {
  return tables.value.filter(table => {
    const matchesSearch =
      table.number.toString().includes(searchQuery.value) ||
      table.customerName.toLowerCase().includes(searchQuery.value.toLowerCase())

    const matchesStatus = !selectedStatus.value || table.status === selectedStatus.value

    return matchesSearch && matchesStatus
  })
})

const availableCount = computed(() => tables.value.filter(t => t.status === 'available').length)
const occupiedCount = computed(() => tables.value.filter(t => t.status === 'occupied').length)
const reservedCount = computed(() => tables.value.filter(t => t.status === 'reserved').length)

// Methods
const getStatusLabel = status => {
  const labels = { available: 'Available', occupied: 'Occupied', reserved: 'Reserved' }
  return labels[status] || status
}

const formatTime = date => {
  return new Date(date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

const selectTable = table => {
  selectedTableData.value = table
}

const startReservation = table => {
  selectedTableData.value = table
  reservationData.value = { customerName: '', notes: '' }
  showReserveModal.value = true
}

const confirmReservation = () => {
  if (selectedTableData.value && reservationData.value.customerName) {
    selectedTableData.value.status = 'occupied'
    selectedTableData.value.customerName = reservationData.value.customerName
    selectedTableData.value.notes = reservationData.value.notes
    selectedTableData.value.checkInTime = new Date()
    showReserveModal.value = false
  }
}

const requestBill = table => {
  alert(`Bill requested for Table ${table.number}`)
}

const freeTable = table => {
  table.status = 'available'
  table.customerName = ''
  table.checkInTime = null
  table.notes = ''
}
</script>
