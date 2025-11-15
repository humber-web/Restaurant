<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useOrdersStore } from '@/stores/orders'
import type { Order } from '@/types/models/order'
import OrderCard from '@/components/orders/OrderCard.vue'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  RefreshCw,
  Search,
  ShoppingCart,
  Clock,
  ChefHat,
  CheckCircle,
  Package,
  X,
  LayoutGrid,
  LayoutList,
} from 'lucide-vue-next'

// Store
const ordersStore = useOrdersStore()

// State
const searchQuery = ref('')
const filterPaymentStatus = ref<string>('ALL')
const filterOrderType = ref<string>('ALL')
const viewMode = ref<'kanban' | 'list'>('kanban')
const isLoading = ref(false)

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

// Computed: Filtered orders
const filteredOrders = computed(() => {
  let result = ordersStore.orders

  // Search by order ID or table
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(o =>
      o.orderID.toString().includes(query) ||
      o.details?.table?.toString().includes(query)
    )
  }

  // Filter by payment status
  if (filterPaymentStatus.value !== 'ALL') {
    result = result.filter(o => o.paymentStatus === filterPaymentStatus.value)
  }

  // Filter by order type
  if (filterOrderType.value !== 'ALL') {
    result = result.filter(o => o.orderType === filterOrderType.value)
  }

  return result
})

// Computed: Orders by status (for Kanban)
const ordersByStatus = computed(() => {
  return {
    PENDING: filteredOrders.value.filter(o => o.status === 'PENDING'),
    PREPARING: filteredOrders.value.filter(o => o.status === 'PREPARING'),
    READY: filteredOrders.value.filter(o => o.status === 'READY'),
    DELIVERED: filteredOrders.value.filter(o => o.status === 'DELIVERED'),
  }
})

// Computed: Statistics
const statistics = computed(() => {
  const total = ordersStore.orders.length
  const active = ordersStore.orders.filter(o =>
    ['PENDING', 'PREPARING', 'READY'].includes(o.status)
  ).length
  const pending = ordersByStatus.value.PENDING.length
  const preparing = ordersByStatus.value.PREPARING.length
  const ready = ordersByStatus.value.READY.length
  const totalRevenue = ordersStore.orders
    .filter(o => o.paymentStatus === 'PAID')
    .reduce((sum, o) => sum + Number(o.grandTotal), 0)

  return {
    total,
    active,
    pending,
    preparing,
    ready,
    totalRevenue,
  }
})

// Column configuration
const columns = [
  {
    id: 'PENDING',
    title: 'Pendente',
    icon: Clock,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
  },
  {
    id: 'PREPARING',
    title: 'Em Preparação',
    icon: ChefHat,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
  },
  {
    id: 'READY',
    title: 'Pronto',
    icon: CheckCircle,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
  },
  {
    id: 'DELIVERED',
    title: 'Entregue',
    icon: Package,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
  },
]

// Refresh data
async function refreshOrders() {
  try {
    isLoading.value = true
    await ordersStore.fetchOrders()
    showToast('Pedidos atualizados')
  } catch (error) {
    console.error('Error refreshing orders:', error)
    showToast('Erro ao atualizar pedidos', 'error')
  } finally {
    isLoading.value = false
  }
}

// Clear filters
function clearFilters() {
  searchQuery.value = ''
  filterPaymentStatus.value = 'ALL'
  filterOrderType.value = 'ALL'
}

// Lifecycle
onMounted(async () => {
  // Initialize WebSocket
  ordersStore.initWebSocket()
  // Load orders
  await refreshOrders()
})

onUnmounted(() => {
  ordersStore.closeWebSocket()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      :class="[
        'fixed bottom-4 right-4 z-50 rounded-md px-6 py-4 text-white shadow-lg transition-all',
        toastVariant === 'success' ? 'bg-green-600' : 'bg-red-600',
      ]"
    >
      {{ toastMessage }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold flex items-center gap-2">
          <ShoppingCart class="h-8 w-8" />
          Pedidos
        </h1>
        <p class="text-muted-foreground">Gestão de pedidos em tempo real</p>
      </div>
      <div class="flex gap-2">
        <!-- View Mode Toggle -->
        <div class="flex gap-1 border rounded-md p-1">
          <Button
            variant="ghost"
            size="sm"
            :class="{ 'bg-accent': viewMode === 'kanban' }"
            @click="viewMode = 'kanban'"
          >
            <LayoutGrid class="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            :class="{ 'bg-accent': viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            <LayoutList class="h-4 w-4" />
          </Button>
        </div>
        <Button @click="refreshOrders" :disabled="isLoading">
          <RefreshCw :class="['mr-2 h-4 w-4', { 'animate-spin': isLoading }]" />
          Atualizar
        </Button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total de Pedidos</CardTitle>
          <ShoppingCart class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statistics.total }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            {{ statistics.active }} ativos
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Pendentes</CardTitle>
          <Clock class="h-4 w-4 text-orange-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-orange-600">{{ statistics.pending }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Aguardam preparação
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Em Preparação</CardTitle>
          <ChefHat class="h-4 w-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-blue-600">{{ statistics.preparing }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Na cozinha
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Prontos</CardTitle>
          <CheckCircle class="h-4 w-4 text-green-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-green-600">{{ statistics.ready }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Para entregar
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Filters -->
    <Card>
      <CardContent class="pt-6">
        <div class="flex flex-wrap gap-4">
          <!-- Search -->
          <div class="flex-1 min-w-[200px]">
            <div class="relative">
              <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                v-model="searchQuery"
                placeholder="Pesquisar por ID ou Mesa..."
                class="pl-10"
              />
            </div>
          </div>

          <!-- Payment Status Filter -->
          <Select v-model="filterPaymentStatus">
            <SelectTrigger class="w-[180px]">
              <SelectValue placeholder="Estado de Pagamento" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Todos os Pagamentos</SelectItem>
              <SelectItem value="PENDING">Pendente</SelectItem>
              <SelectItem value="PARTIALLY_PAID">Parcial</SelectItem>
              <SelectItem value="PAID">Pago</SelectItem>
            </SelectContent>
          </Select>

          <!-- Order Type Filter -->
          <Select v-model="filterOrderType">
            <SelectTrigger class="w-[180px]">
              <SelectValue placeholder="Tipo de Pedido" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Todos os Tipos</SelectItem>
              <SelectItem value="RESTAURANT">Restaurante</SelectItem>
              <SelectItem value="ONLINE">Online</SelectItem>
            </SelectContent>
          </Select>

          <!-- Clear Filters -->
          <Button
            variant="outline"
            @click="clearFilters"
            v-if="searchQuery || filterPaymentStatus !== 'ALL' || filterOrderType !== 'ALL'"
          >
            <X class="mr-2 h-4 w-4" />
            Limpar
          </Button>
        </div>
      </CardContent>
    </Card>

    <!-- Kanban View -->
    <div v-if="viewMode === 'kanban'" class="grid gap-4 md:grid-cols-4 flex-1 overflow-hidden">
      <div
        v-for="column in columns"
        :key="column.id"
        class="flex flex-col"
      >
        <!-- Column Header -->
        <div :class="['rounded-t-lg p-4 border-b-2', column.bgColor, column.borderColor]">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <component :is="column.icon" :class="['h-5 w-5', column.color]" />
              <h3 class="font-semibold">{{ column.title }}</h3>
            </div>
            <Badge variant="secondary">
              {{ ordersByStatus[column.id as keyof typeof ordersByStatus].length }}
            </Badge>
          </div>
        </div>

        <!-- Column Content -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50/50 rounded-b-lg border border-t-0">
          <OrderCard
            v-for="order in ordersByStatus[column.id as keyof typeof ordersByStatus]"
            :key="order.orderID"
            :order="order"
          />

          <!-- Empty State -->
          <div
            v-if="ordersByStatus[column.id as keyof typeof ordersByStatus].length === 0"
            class="flex flex-col items-center justify-center py-8 text-center"
          >
            <component :is="column.icon" class="h-12 w-12 text-muted-foreground/50 mb-2" />
            <p class="text-sm text-muted-foreground">
              Nenhum pedido {{ column.title.toLowerCase() }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-else class="flex-1 overflow-hidden">
      <Card class="h-full">
        <CardContent class="p-6 h-full overflow-y-auto">
          <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            <OrderCard
              v-for="order in filteredOrders"
              :key="order.orderID"
              :order="order"
            />
          </div>

          <!-- Empty State -->
          <div
            v-if="filteredOrders.length === 0"
            class="flex flex-col items-center justify-center h-full min-h-[400px]"
          >
            <ShoppingCart class="h-16 w-16 text-muted-foreground/50 mb-4" />
            <h3 class="text-lg font-semibold mb-2">Nenhum pedido encontrado</h3>
            <p class="text-sm text-muted-foreground mb-4">
              Não há pedidos que correspondam aos filtros aplicados
            </p>
            <Button variant="outline" @click="clearFilters">
              Limpar Filtros
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
