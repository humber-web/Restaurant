<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useOrdersStore } from '@/stores/orders'
import { ordersApi, paymentsApi, tablesApi, menuApi } from '@/services/api'
import type { Order } from '@/types/models/order'
import type { Payment } from '@/types/models/payment'
import type { Table } from '@/types/models/table'
import type { MenuItem } from '@/types/models/menu'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  RefreshCw,
  TrendingUp,
  DollarSign,
  ShoppingCart,
  Users,
  AlertCircle,
  Clock,
  CheckCircle,
  ChefHat,
  Award,
} from 'lucide-vue-next'

// Initialize store
const ordersStore = useOrdersStore()

// State
const orders = ref<Order[]>([])
const payments = ref<Payment[]>([])
const tables = ref<Table[]>([])
const menuItems = ref<MenuItem[]>([])
const isLoading = ref(false)

// Computed: Today's date range
const todayStart = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return today
})

const todayEnd = computed(() => {
  const today = new Date()
  today.setHours(23, 59, 59, 999)
  return today
})

// Computed: This month's date range
const monthStart = computed(() => {
  const today = new Date()
  return new Date(today.getFullYear(), today.getMonth(), 1)
})

// Computed: Today's statistics
const todayStats = computed(() => {
  // Orders today
  const todayOrders = orders.value.filter(o => {
    const orderDate = new Date(o.created_at)
    return orderDate >= todayStart.value && orderDate <= todayEnd.value
  })

  // Payments today (completed)
  const todayPayments = payments.value.filter(p => {
    const paymentDate = new Date(p.created_at)
    return p.payment_status === 'COMPLETED' &&
           paymentDate >= todayStart.value &&
           paymentDate <= todayEnd.value
  })

  // Revenue today
  const todayRevenue = todayPayments.reduce((sum, p) => sum + Number(p.amount), 0)

  // Active orders (not delivered/cancelled)
  const activeOrders = orders.value.filter(o =>
    o.status !== 'DELIVERED' && o.status !== 'CANCELLED'
  )

  // Orders being prepared
  const preparingOrders = activeOrders.filter(o => o.status === 'PREPARING')

  // Orders ready
  const readyOrders = activeOrders.filter(o => o.status === 'READY')

  return {
    totalOrders: todayOrders.length,
    totalRevenue: todayRevenue,
    activeOrders: activeOrders.length,
    preparingOrders: preparingOrders.length,
    readyOrders: readyOrders.length,
  }
})

// Computed: Month statistics
const monthStats = computed(() => {
  const monthPayments = payments.value.filter(p => {
    const paymentDate = new Date(p.created_at)
    return p.payment_status === 'COMPLETED' && paymentDate >= monthStart.value
  })

  return {
    revenue: monthPayments.reduce((sum, p) => sum + Number(p.amount), 0),
    ordersCount: orders.value.filter(o => {
      const orderDate = new Date(o.created_at)
      return orderDate >= monthStart.value
    }).length
  }
})

// Computed: Tables statistics
const tablesStats = computed(() => {
  const total = tables.value.length
  const occupied = tables.value.filter(t => t.status === 'OC').length
  const available = tables.value.filter(t => t.status === 'AV').length
  const reserved = tables.value.filter(t => t.status === 'RE').length

  return { total, occupied, available, reserved }
})

// Computed: Top 5 products today
const topProducts = computed(() => {
  // Get today's orders
  const todayOrders = orders.value.filter(o => {
    const orderDate = new Date(o.created_at)
    return orderDate >= todayStart.value && orderDate <= todayEnd.value
  })

  // Aggregate items
  const productMap = new Map<number, {
    id: number
    name: string
    quantity: number
    revenue: number
  }>()

  todayOrders.forEach(order => {
    order.items.forEach(item => {
      const existing = productMap.get(item.menu_item)
      if (existing) {
        existing.quantity += item.quantity
        existing.revenue += item.price * item.quantity
      } else {
        productMap.set(item.menu_item, {
          id: item.menu_item,
          name: item.name || `Produto #${item.menu_item}`,
          quantity: item.quantity,
          revenue: item.price * item.quantity
        })
      }
    })
  })

  // Sort by quantity and take top 5
  return Array.from(productMap.values())
    .sort((a, b) => b.quantity - a.quantity)
    .slice(0, 5)
})

// Computed: Recent orders (last 10)
const recentOrders = computed(() => {
  return [...orders.value]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 10)
})

// Computed: Sales by day (last 7 days)
const last7DaysSales = computed(() => {
  const days: { date: string; revenue: number; orders: number }[] = []

  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    date.setHours(0, 0, 0, 0)

    const nextDay = new Date(date)
    nextDay.setDate(nextDay.getDate() + 1)

    const dayPayments = payments.value.filter(p => {
      const paymentDate = new Date(p.created_at)
      return p.payment_status === 'COMPLETED' &&
             paymentDate >= date &&
             paymentDate < nextDay
    })

    const dayOrders = orders.value.filter(o => {
      const orderDate = new Date(o.created_at)
      return orderDate >= date && orderDate < nextDay
    })

    days.push({
      date: date.toLocaleDateString('pt-PT', { weekday: 'short', day: 'numeric' }),
      revenue: dayPayments.reduce((sum, p) => sum + Number(p.amount), 0),
      orders: dayOrders.length
    })
  }

  return days
})

// Computed: Max revenue for chart scaling
const maxRevenue = computed(() => {
  return Math.max(...last7DaysSales.value.map(d => d.revenue), 1)
})

// Computed: Alerts
const alerts = computed(() => {
  const alertsList: { type: 'warning' | 'error' | 'info'; message: string }[] = []

  // Old orders (waiting > 30 min)
  const now = new Date()
  const oldOrders = orders.value.filter(o => {
    if (o.status === 'DELIVERED' || o.status === 'CANCELLED') return false
    const orderDate = new Date(o.created_at)
    const diffMins = (now.getTime() - orderDate.getTime()) / 60000
    return diffMins > 30
  })

  if (oldOrders.length > 0) {
    alertsList.push({
      type: 'error',
      message: `${oldOrders.length} pedido(s) esperando há mais de 30 minutos!`
    })
  }

  // Pending orders
  const pendingOrders = orders.value.filter(o => o.status === 'PENDING')
  if (pendingOrders.length > 5) {
    alertsList.push({
      type: 'warning',
      message: `${pendingOrders.length} pedidos pendentes na cozinha`
    })
  }

  // Tables occupied
  if (tablesStats.value.occupied === tablesStats.value.total) {
    alertsList.push({
      type: 'warning',
      message: 'Todas as mesas estão ocupadas!'
    })
  }

  return alertsList
})

// Format currency
function formatCurrency(value: number): string {
  return `€${value.toFixed(2)}`
}

// Format time ago
function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMins = Math.floor((now.getTime() - date.getTime()) / 60000)

  if (diffMins < 1) return 'agora'
  if (diffMins < 60) return `há ${diffMins}min`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `há ${diffHours}h`

  return date.toLocaleDateString('pt-PT')
}

// Get order status label
function getOrderStatusLabel(status: string): string {
  switch (status) {
    case 'PENDING': return 'Pendente'
    case 'PREPARING': return 'Em Preparação'
    case 'READY': return 'Pronto'
    case 'DELIVERED': return 'Entregue'
    case 'CANCELLED': return 'Cancelado'
    default: return status
  }
}

// Get order status variant
function getOrderStatusVariant(status: string): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case 'PENDING': return 'secondary'
    case 'PREPARING': return 'outline'
    case 'READY': return 'default'
    case 'DELIVERED': return 'default'
    case 'CANCELLED': return 'destructive'
    default: return 'secondary'
  }
}

// Fetch all data
async function fetchData() {
  try {
    isLoading.value = true
    const [ordersData, paymentsData, tablesData, menuItemsData] = await Promise.all([
      ordersApi.getOrders(),
      paymentsApi.getPayments(),
      tablesApi.getTables(),
      menuApi.getMenuItems(),
    ])

    orders.value = ordersData
    payments.value = paymentsData
    tables.value = tablesData
    menuItems.value = menuItemsData
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
  } finally {
    isLoading.value = false
  }
}

// Lifecycle
onMounted(() => {
  ordersStore.initWebSocket()
  fetchData()

  // Refresh data every 30 seconds
  const interval = setInterval(fetchData, 30000)
  onUnmounted(() => {
    clearInterval(interval)
    ordersStore.closeWebSocket()
  })
})
</script>

<template>
  <div class="flex h-full flex-col gap-6 p-6 overflow-y-auto">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">Dashboard</h1>
        <p class="text-muted-foreground">Visão geral do restaurante em tempo real</p>
      </div>
      <Button @click="fetchData" :disabled="isLoading">
        <RefreshCw :class="['mr-2 h-4 w-4', { 'animate-spin': isLoading }]" />
        Atualizar
      </Button>
    </div>

    <!-- Alerts -->
    <div v-if="alerts.length > 0" class="space-y-2">
      <Card
        v-for="(alert, index) in alerts"
        :key="index"
        :class="[
          'border-l-4',
          alert.type === 'error' ? 'border-l-red-500 bg-red-50' : '',
          alert.type === 'warning' ? 'border-l-orange-500 bg-orange-50' : '',
          alert.type === 'info' ? 'border-l-blue-500 bg-blue-50' : '',
        ]"
      >
        <CardContent class="flex items-center gap-3 py-3">
          <AlertCircle :class="[
            'h-5 w-5',
            alert.type === 'error' ? 'text-red-600' : '',
            alert.type === 'warning' ? 'text-orange-600' : '',
            alert.type === 'info' ? 'text-blue-600' : '',
          ]" />
          <p :class="[
            'font-medium',
            alert.type === 'error' ? 'text-red-900' : '',
            alert.type === 'warning' ? 'text-orange-900' : '',
            alert.type === 'info' ? 'text-blue-900' : '',
          ]">
            {{ alert.message }}
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Main Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Vendas Hoje</CardTitle>
          <DollarSign class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-green-600">{{ formatCurrency(todayStats.totalRevenue) }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            {{ todayStats.totalOrders }} pedidos
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Pedidos Ativos</CardTitle>
          <ShoppingCart class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ todayStats.activeOrders }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            {{ todayStats.preparingOrders }} a preparar, {{ todayStats.readyOrders }} prontos
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Mesas</CardTitle>
          <Users class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ tablesStats.occupied }}/{{ tablesStats.total }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            {{ tablesStats.available }} disponíveis
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Receita do Mês</CardTitle>
          <TrendingUp class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ formatCurrency(monthStats.revenue) }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            {{ monthStats.ordersCount }} pedidos este mês
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Charts and Lists Row -->
    <div class="grid gap-4 md:grid-cols-2">
      <!-- Sales Chart (Last 7 Days) -->
      <Card>
        <CardHeader>
          <CardTitle class="text-lg">Vendas dos Últimos 7 Dias</CardTitle>
          <CardDescription>Receita diária</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div
              v-for="day in last7DaysSales"
              :key="day.date"
              class="flex items-center gap-2"
            >
              <div class="w-16 text-sm text-muted-foreground">{{ day.date }}</div>
              <div class="flex-1 flex items-center gap-2">
                <div class="flex-1 bg-muted rounded-full h-6 overflow-hidden">
                  <div
                    class="bg-green-500 h-full transition-all"
                    :style="{ width: `${(day.revenue / maxRevenue) * 100}%` }"
                  ></div>
                </div>
                <div class="w-24 text-sm font-medium text-right">
                  {{ formatCurrency(day.revenue) }}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Top 5 Products -->
      <Card>
        <CardHeader>
          <div class="flex items-center gap-2">
            <Award class="h-5 w-5 text-yellow-500" />
            <CardTitle class="text-lg">Top 5 Produtos Hoje</CardTitle>
          </div>
          <CardDescription>Mais vendidos</CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="topProducts.length > 0" class="space-y-3">
            <div
              v-for="(product, index) in topProducts"
              :key="product.id"
              class="flex items-center justify-between"
            >
              <div class="flex items-center gap-3">
                <div class="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold">
                  {{ index + 1 }}
                </div>
                <div>
                  <div class="font-medium">{{ product.name }}</div>
                  <div class="text-xs text-muted-foreground">
                    {{ formatCurrency(product.revenue) }}
                  </div>
                </div>
              </div>
              <Badge variant="outline">{{ product.quantity }} vendidos</Badge>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground">Sem vendas hoje</p>
        </CardContent>
      </Card>
    </div>

    <!-- Recent Orders -->
    <Card>
      <CardHeader>
        <div class="flex items-center gap-2">
          <Clock class="h-5 w-5 text-muted-foreground" />
          <CardTitle class="text-lg">Pedidos Recentes</CardTitle>
        </div>
        <CardDescription>Últimos 10 pedidos</CardDescription>
      </CardHeader>
      <CardContent>
        <div v-if="recentOrders.length > 0" class="space-y-2">
          <div
            v-for="order in recentOrders"
            :key="order.orderID"
            class="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
          >
            <div class="flex items-center gap-3">
              <ChefHat class="h-4 w-4 text-muted-foreground" />
              <div>
                <div class="font-medium">Pedido #{{ order.orderID }}</div>
                <div class="text-xs text-muted-foreground">
                  Mesa {{ order.details?.table || '—' }} • {{ formatTimeAgo(order.created_at) }}
                </div>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="text-right">
                <div class="font-semibold">{{ formatCurrency(order.grandTotal) }}</div>
                <div class="text-xs text-muted-foreground">
                  {{ order.items.reduce((sum, item) => sum + item.quantity, 0) }} items
                </div>
              </div>
              <Badge :variant="getOrderStatusVariant(order.status)">
                {{ getOrderStatusLabel(order.status) }}
              </Badge>
            </div>
          </div>
        </div>
        <p v-else class="text-sm text-muted-foreground">Sem pedidos recentes</p>
      </CardContent>
    </Card>
  </div>
</template>
