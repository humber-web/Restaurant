<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ordersApi } from '@/services/api'
import type { Order } from '@/types/models/order'
import OrdersTableAdvanced from '@/components/orders/OrdersTableAdvanced.vue'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  RefreshCw,
  Filter,
  ShoppingCart,
  CreditCard,
  CheckCircle,
  Clock,
} from 'lucide-vue-next'

// State
const orders = ref<Order[]>([])
const isLoading = ref(true)

// Filters
const filterOrderStatus = ref<string>('ALL')
const filterPaymentStatus = ref<string>('ALL')
const filterOrderType = ref<string>('ALL')
const filterDateFrom = ref<string>('')
const filterDateTo = ref<string>('')

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
  let result = orders.value

  // Filter by order status
  if (filterOrderStatus.value !== 'ALL') {
    result = result.filter(o => o.status === filterOrderStatus.value)
  }

  // Filter by payment status
  if (filterPaymentStatus.value !== 'ALL') {
    result = result.filter(o => o.paymentStatus === filterPaymentStatus.value)
  }

  // Filter by order type
  if (filterOrderType.value !== 'ALL') {
    result = result.filter(o => o.orderType === filterOrderType.value)
  }

  // Filter by date range
  if (filterDateFrom.value) {
    const fromDate = new Date(filterDateFrom.value)
    fromDate.setHours(0, 0, 0, 0)
    result = result.filter(o => new Date(o.created_at) >= fromDate)
  }

  if (filterDateTo.value) {
    const toDate = new Date(filterDateTo.value)
    toDate.setHours(23, 59, 59, 999)
    result = result.filter(o => new Date(o.created_at) <= toDate)
  }

  return result
})

// Computed: Statistics
const statistics = computed(() => {
  const total = filteredOrders.value.length
  const totalRevenue = filteredOrders.value
    .filter(o => o.paymentStatus === 'PAID')
    .reduce((sum, o) => sum + Number(o.grandTotal), 0)

  const byOrderStatus = {
    PENDING: filteredOrders.value.filter(o => o.status === 'PENDING').length,
    PREPARING: filteredOrders.value.filter(o => o.status === 'PREPARING').length,
    READY: filteredOrders.value.filter(o => o.status === 'READY').length,
    DELIVERED: filteredOrders.value.filter(o => o.status === 'DELIVERED').length,
    CANCELLED: filteredOrders.value.filter(o => o.status === 'CANCELLED').length,
  }

  const byPaymentStatus = {
    PAID: filteredOrders.value.filter(o => o.paymentStatus === 'PAID').length,
    PARTIALLY_PAID: filteredOrders.value.filter(o => o.paymentStatus === 'PARTIALLY_PAID').length,
    PENDING: filteredOrders.value.filter(o => o.paymentStatus === 'PENDING').length,
    FAILED: filteredOrders.value.filter(o => o.paymentStatus === 'FAILED').length,
  }

  const averageOrderValue = total > 0 ? totalRevenue / byPaymentStatus.PAID : 0

  return {
    total,
    totalRevenue,
    byOrderStatus,
    byPaymentStatus,
    averageOrderValue,
  }
})

// Fetch orders
async function fetchOrders() {
  try {
    isLoading.value = true
    orders.value = await ordersApi.getOrders()
  } catch (error) {
    console.error('Error fetching orders:', error)
    showToast('Erro ao carregar pedidos', 'error')
  } finally {
    isLoading.value = false
  }
}

// Clear filters
function clearFilters() {
  filterOrderStatus.value = 'ALL'
  filterPaymentStatus.value = 'ALL'
  filterOrderType.value = 'ALL'
  filterDateFrom.value = ''
  filterDateTo.value = ''
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">Pedidos</h1>
        <p class="text-muted-foreground">Gestão de todos os pedidos do restaurante</p>
      </div>
      <Button @click="fetchOrders" :disabled="isLoading">
        <RefreshCw :class="['mr-2 h-4 w-4', { 'animate-spin': isLoading }]" />
        Atualizar
      </Button>
    </div>

    <!-- Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total de Pedidos</CardTitle>
          <ShoppingCart class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statistics.total }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            {{ statistics.byOrderStatus.PENDING }} pendentes
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Receita Total</CardTitle>
          <CreditCard class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">€{{ statistics.totalRevenue.toFixed(2) }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Pedidos pagos: {{ statistics.byPaymentStatus.PAID }}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Valor Médio</CardTitle>
          <CheckCircle class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">€{{ statistics.averageOrderValue.toFixed(2) }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Por pedido pago
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Em Preparação</CardTitle>
          <Clock class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statistics.byOrderStatus.PREPARING }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            {{ statistics.byOrderStatus.READY }} prontos
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Filters -->
    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <div>
            <CardTitle class="text-lg">Filtros</CardTitle>
            <CardDescription>Filtrar pedidos por estado, tipo e data</CardDescription>
          </div>
          <Button variant="outline" size="sm" @click="clearFilters">
            <Filter class="mr-2 h-4 w-4" />
            Limpar Filtros
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <!-- Order Status Filter -->
          <div class="space-y-2">
            <Label>Estado do Pedido</Label>
            <Select v-model="filterOrderStatus">
              <SelectTrigger>
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                <SelectItem value="PENDING">Pendente</SelectItem>
                <SelectItem value="PREPARING">Em Preparação</SelectItem>
                <SelectItem value="READY">Pronto</SelectItem>
                <SelectItem value="DELIVERED">Entregue</SelectItem>
                <SelectItem value="CANCELLED">Cancelado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Payment Status Filter -->
          <div class="space-y-2">
            <Label>Estado do Pagamento</Label>
            <Select v-model="filterPaymentStatus">
              <SelectTrigger>
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                <SelectItem value="PAID">Pago</SelectItem>
                <SelectItem value="PARTIALLY_PAID">Parcialmente Pago</SelectItem>
                <SelectItem value="PENDING">Pendente</SelectItem>
                <SelectItem value="FAILED">Falhado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Order Type Filter -->
          <div class="space-y-2">
            <Label>Tipo de Pedido</Label>
            <Select v-model="filterOrderType">
              <SelectTrigger>
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                <SelectItem value="RESTAURANT">Restaurante</SelectItem>
                <SelectItem value="ONLINE">Online</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Date From Filter -->
          <div class="space-y-2">
            <Label>Data Início</Label>
            <Input
              v-model="filterDateFrom"
              type="date"
              placeholder="Data início"
            />
          </div>

          <!-- Date To Filter -->
          <div class="space-y-2">
            <Label>Data Fim</Label>
            <Input
              v-model="filterDateTo"
              type="date"
              placeholder="Data fim"
            />
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Orders Table -->
    <Card class="flex-1 flex flex-col">
      <CardHeader>
        <div class="flex items-center justify-between">
          <CardTitle class="text-lg">Pedidos ({{ filteredOrders.length }})</CardTitle>
        </div>
      </CardHeader>
      <CardContent class="flex-1">
        <OrdersTableAdvanced
          v-if="!isLoading"
          :orders="filteredOrders"
        />
        <div v-else class="flex items-center justify-center py-8">
          <p class="text-muted-foreground">A carregar pedidos...</p>
        </div>
      </CardContent>
    </Card>

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
  </div>
</template>
