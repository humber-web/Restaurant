<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ordersApi, paymentsApi, menuApi } from '@/services/api'
import type { Order } from '@/types/models/order'
import type { Payment } from '@/types/models/payment'
import type { MenuItem, MenuCategory } from '@/types/models/menu'
import ReportsSalesTable, { type ProductSalesData } from '@/components/reports/ReportsSalesTable.vue'
import ReportsCategoriesTable, { type CategorySalesData } from '@/components/reports/ReportsCategoriesTable.vue'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  RefreshCw,
  Download,
  TrendingUp,
  DollarSign,
  ShoppingBag,
  Package,
  CreditCard,
  Wallet,
  Globe,
  Award,
  AlertCircle,
} from 'lucide-vue-next'

// State
const orders = ref<Order[]>([])
const payments = ref<Payment[]>([])
const menuItems = ref<MenuItem[]>([])
const categories = ref<MenuCategory[]>([])
const isLoading = ref(true)

// Filters
const filterDateFrom = ref<string>('')
const filterDateTo = ref<string>('')
const activeTab = ref('overview')

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
  let result = orders.value.filter(o => o.paymentStatus === 'PAID' || o.paymentStatus === 'PARTIALLY_PAID')

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

// Computed: Filtered payments
const filteredPayments = computed(() => {
  let result = payments.value.filter(p => p.payment_status === 'COMPLETED')

  if (filterDateFrom.value) {
    const fromDate = new Date(filterDateFrom.value)
    fromDate.setHours(0, 0, 0, 0)
    result = result.filter(p => new Date(p.created_at) >= fromDate)
  }

  if (filterDateTo.value) {
    const toDate = new Date(filterDateTo.value)
    toDate.setHours(23, 59, 59, 999)
    result = result.filter(p => new Date(p.created_at) <= toDate)
  }

  return result
})

// Computed: Product sales data
const productSalesData = computed((): ProductSalesData[] => {
  const salesMap = new Map<number, {
    itemID: number
    name: string
    category: string
    quantitySold: number
    revenue: number
    prices: number[]
    orders: Set<number>
  }>()

  // Aggregate data from filtered orders
  filteredOrders.value.forEach(order => {
    order.items.forEach(item => {
      const existing = salesMap.get(item.menu_item)
      if (existing) {
        existing.quantitySold += item.quantity
        existing.revenue += item.price * item.quantity
        existing.prices.push(item.price)
        existing.orders.add(order.orderID)
      } else {
        // Find menu item details
        const menuItem = menuItems.value.find(mi => mi.itemID === item.menu_item)
        const category = categories.value.find(c => c.categoryID === menuItem?.categoryID)

        salesMap.set(item.menu_item, {
          itemID: item.menu_item,
          name: item.name || menuItem?.name || `Produto #${item.menu_item}`,
          category: category?.name || 'Sem Categoria',
          quantitySold: item.quantity,
          revenue: item.price * item.quantity,
          prices: [item.price],
          orders: new Set([order.orderID])
        })
      }
    })
  })

  // Convert to array and calculate averages
  return Array.from(salesMap.values()).map(item => ({
    itemID: item.itemID,
    name: item.name,
    category: item.category,
    quantitySold: item.quantitySold,
    revenue: item.revenue,
    averagePrice: item.prices.reduce((a, b) => a + b, 0) / item.prices.length,
    orderCount: item.orders.size
  })).sort((a, b) => b.revenue - a.revenue)
})

// Computed: Category sales data
const categorySalesData = computed((): CategorySalesData[] => {
  const categoryMap = new Map<string, {
    categoryID: number
    name: string
    products: Set<number>
    totalQuantitySold: number
    revenue: number
    orders: Set<number>
  }>()

  // Aggregate from product sales data
  productSalesData.value.forEach(product => {
    const category = categories.value.find(c => c.name === product.category)
    const categoryID = category?.categoryID || 0
    const categoryName = product.category

    const existing = categoryMap.get(categoryName)
    if (existing) {
      existing.products.add(product.itemID)
      existing.totalQuantitySold += product.quantitySold
      existing.revenue += product.revenue
      // orders are already counted in product data
    } else {
      categoryMap.set(categoryName, {
        categoryID,
        name: categoryName,
        products: new Set([product.itemID]),
        totalQuantitySold: product.quantitySold,
        revenue: product.revenue,
        orders: new Set() // Will calculate from orders
      })
    }
  })

  // Calculate order counts per category
  filteredOrders.value.forEach(order => {
    order.items.forEach(item => {
      const product = productSalesData.value.find(p => p.itemID === item.menu_item)
      if (product) {
        const category = categoryMap.get(product.category)
        if (category) {
          category.orders.add(order.orderID)
        }
      }
    })
  })

  return Array.from(categoryMap.values()).map(cat => ({
    categoryID: cat.categoryID,
    name: cat.name,
    productCount: cat.products.size,
    totalQuantitySold: cat.totalQuantitySold,
    revenue: cat.revenue,
    orderCount: cat.orders.size,
    averageOrderValue: cat.orders.size > 0 ? cat.revenue / cat.orders.size : 0
  })).sort((a, b) => b.revenue - a.revenue)
})

// Computed: Overview statistics
const statistics = computed(() => {
  const totalOrders = filteredOrders.value.length
  const totalRevenue = filteredPayments.value.reduce((sum, p) => sum + Number(p.amount), 0)
  const totalProductsSold = productSalesData.value.reduce((sum, p) => sum + p.quantitySold, 0)
  const uniqueProductsSold = productSalesData.value.length

  // Payment methods breakdown
  const paymentMethods = {
    cash: filteredPayments.value
      .filter(p => p.payment_method === 'CASH')
      .reduce((sum, p) => sum + Number(p.amount), 0),
    card: filteredPayments.value
      .filter(p => ['CREDIT_CARD', 'DEBIT_CARD'].includes(p.payment_method))
      .reduce((sum, p) => sum + Number(p.amount), 0),
    online: filteredPayments.value
      .filter(p => p.payment_method === 'ONLINE')
      .reduce((sum, p) => sum + Number(p.amount), 0),
  }

  // Best seller
  const bestSeller = productSalesData.value[0] || null

  // Slow movers (bottom 5)
  const slowMovers = productSalesData.value.slice(-5).reverse()

  // Average order value
  const averageOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0

  // Daily average (if date range is set)
  let dailyAverage = 0
  if (filterDateFrom.value && filterDateTo.value) {
    const days = Math.ceil((new Date(filterDateTo.value).getTime() - new Date(filterDateFrom.value).getTime()) / (1000 * 60 * 60 * 24)) + 1
    dailyAverage = days > 0 ? totalRevenue / days : 0
  }

  return {
    totalOrders,
    totalRevenue,
    totalProductsSold,
    uniqueProductsSold,
    paymentMethods,
    bestSeller,
    slowMovers,
    averageOrderValue,
    dailyAverage
  }
})

// Fetch all data
async function fetchData() {
  try {
    isLoading.value = true
    const [ordersData, paymentsData, menuItemsData, categoriesData] = await Promise.all([
      ordersApi.getOrders(),
      paymentsApi.getPayments(),
      menuApi.getItems(),
      menuApi.getCategories(),
    ])
    orders.value = ordersData
    payments.value = paymentsData
    menuItems.value = menuItemsData
    categories.value = categoriesData
    showToast('Dados carregados com sucesso')
  } catch (error) {
    console.error('Error fetching data:', error)
    showToast('Erro ao carregar dados', 'error')
  } finally {
    isLoading.value = false
  }
}

// Export to CSV
function exportToCSV(data: any[], filename: string) {
  if (data.length === 0) {
    showToast('Sem dados para exportar', 'error')
    return
  }

  // Get headers from first object
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(header => {
      const value = row[header]
      // Escape commas and quotes
      if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
        return `"${value.replace(/"/g, '""')}"`
      }
      return value
    }).join(','))
  ].join('\n')

  // Download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${filename}_${new Date().toISOString().split('T')[0]}.csv`
  link.click()

  showToast('Relatório exportado com sucesso')
}

// Set default date range (last 30 days)
function setDefaultDateRange() {
  const today = new Date()
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(today.getDate() - 30)

  const fromIso = thirtyDaysAgo.toISOString()
  const toIso = today.toISOString()

  // Use a safe fallback in case split returns undefined
  filterDateFrom.value = (fromIso.split('T')[0]) || ''
  filterDateTo.value = (toIso.split('T')[0]) || ''
}

// Clear filters
function clearFilters() {
  filterDateFrom.value = ''
  filterDateTo.value = ''
}

onMounted(() => {
  setDefaultDateRange()
  fetchData()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">Relatórios</h1>
        <p class="text-muted-foreground">Análise de vendas e desempenho financeiro</p>
      </div>
      <Button @click="fetchData" :disabled="isLoading">
        <RefreshCw :class="['mr-2 h-4 w-4', { 'animate-spin': isLoading }]" />
        Atualizar
      </Button>
    </div>

    <!-- Date Range Filter -->
    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <div>
            <CardTitle class="text-lg">Período de Análise</CardTitle>
            <CardDescription>Selecione o intervalo de datas para os relatórios</CardDescription>
          </div>
          <div class="flex gap-2">
            <Button variant="outline" size="sm" @click="setDefaultDateRange">
              Últimos 30 Dias
            </Button>
            <Button variant="outline" size="sm" @click="clearFilters">
              Limpar
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <Label>Data Início</Label>
            <Input
              v-model="filterDateFrom"
              type="date"
              placeholder="Data início"
            />
          </div>
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

    <!-- Tabs for different reports -->
    <Tabs v-model="activeTab" class="flex-1 flex flex-col">
      <TabsList class="grid w-full grid-cols-3">
        <TabsTrigger value="overview">Visão Geral</TabsTrigger>
        <TabsTrigger value="products">Produtos</TabsTrigger>
        <TabsTrigger value="categories">Categorias</TabsTrigger>
      </TabsList>

      <!-- Overview Tab -->
      <TabsContent value="overview" class="flex-1 space-y-4">
        <!-- Main Statistics Cards -->
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium">Receita Total</CardTitle>
              <DollarSign class="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-bold text-green-600">€{{ statistics.totalRevenue.toFixed(2) }}</div>
              <p class="text-xs text-muted-foreground mt-1">
                {{ statistics.totalOrders }} pedidos pagos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium">Produtos Vendidos</CardTitle>
              <Package class="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-bold">{{ statistics.totalProductsSold }}</div>
              <p class="text-xs text-muted-foreground mt-1">
                {{ statistics.uniqueProductsSold }} produtos únicos
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium">Valor Médio/Pedido</CardTitle>
              <ShoppingBag class="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-bold">€{{ statistics.averageOrderValue.toFixed(2) }}</div>
              <p class="text-xs text-muted-foreground mt-1">
                Ticket médio
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle class="text-sm font-medium">Média Diária</CardTitle>
              <TrendingUp class="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-bold">€{{ statistics.dailyAverage.toFixed(2) }}</div>
              <p class="text-xs text-muted-foreground mt-1">
                Receita por dia
              </p>
            </CardContent>
          </Card>
        </div>

        <!-- Payment Methods Breakdown -->
        <Card>
          <CardHeader>
            <CardTitle class="text-lg">Métodos de Pagamento</CardTitle>
            <CardDescription>Distribuição de receita por método</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="grid gap-4 md:grid-cols-3">
              <div class="flex items-center gap-4 p-4 border rounded-lg">
                <Wallet class="h-8 w-8 text-green-600" />
                <div>
                  <p class="text-sm text-muted-foreground">Dinheiro</p>
                  <p class="text-2xl font-bold">€{{ statistics.paymentMethods.cash.toFixed(2) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-4 p-4 border rounded-lg">
                <CreditCard class="h-8 w-8 text-blue-600" />
                <div>
                  <p class="text-sm text-muted-foreground">Cartão</p>
                  <p class="text-2xl font-bold">€{{ statistics.paymentMethods.card.toFixed(2) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-4 p-4 border rounded-lg">
                <Globe class="h-8 w-8 text-purple-600" />
                <div>
                  <p class="text-sm text-muted-foreground">Online</p>
                  <p class="text-2xl font-bold">€{{ statistics.paymentMethods.online.toFixed(2) }}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Best Seller & Slow Movers -->
        <div class="grid gap-4 md:grid-cols-2">
          <!-- Best Seller -->
          <Card>
            <CardHeader>
              <div class="flex items-center gap-2">
                <Award class="h-5 w-5 text-yellow-500" />
                <CardTitle class="text-lg">Mais Vendido</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div v-if="statistics.bestSeller" class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="font-semibold text-lg">{{ statistics.bestSeller.name }}</span>
                  <Badge>{{ statistics.bestSeller.category }}</Badge>
                </div>
                <div class="grid grid-cols-3 gap-2 text-sm">
                  <div>
                    <p class="text-muted-foreground">Vendidos</p>
                    <p class="font-bold">{{ statistics.bestSeller.quantitySold }}</p>
                  </div>
                  <div>
                    <p class="text-muted-foreground">Receita</p>
                    <p class="font-bold text-green-600">€{{ statistics.bestSeller.revenue.toFixed(2) }}</p>
                  </div>
                  <div>
                    <p class="text-muted-foreground">Pedidos</p>
                    <p class="font-bold">{{ statistics.bestSeller.orderCount }}</p>
                  </div>
                </div>
              </div>
              <p v-else class="text-muted-foreground">Sem dados disponíveis</p>
            </CardContent>
          </Card>

          <!-- Slow Movers -->
          <Card>
            <CardHeader>
              <div class="flex items-center gap-2">
                <AlertCircle class="h-5 w-5 text-orange-500" />
                <CardTitle class="text-lg">Produtos com Baixa Venda</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div v-if="statistics.slowMovers.length > 0" class="space-y-2">
                <div
                  v-for="product in statistics.slowMovers"
                  :key="product.itemID"
                  class="flex items-center justify-between text-sm border-b pb-2 last:border-0"
                >
                  <span class="font-medium">{{ product.name }}</span>
                  <span class="text-muted-foreground">{{ product.quantitySold }} vendidos</span>
                </div>
              </div>
              <p v-else class="text-muted-foreground">Sem dados disponíveis</p>
            </CardContent>
          </Card>
        </div>
      </TabsContent>

      <!-- Products Tab -->
      <TabsContent value="products" class="flex-1 flex flex-col space-y-4">
        <Card class="flex-1 flex flex-col">
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle class="text-lg">Vendas por Produto</CardTitle>
                <CardDescription>Desempenho detalhado de cada produto ({{ productSalesData.length }} produtos)</CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                @click="exportToCSV(productSalesData, 'relatorio_produtos')"
                :disabled="productSalesData.length === 0"
              >
                <Download class="mr-2 h-4 w-4" />
                Exportar CSV
              </Button>
            </div>
          </CardHeader>
          <CardContent class="flex-1">
            <ReportsSalesTable
              v-if="!isLoading && productSalesData.length > 0"
              :products="productSalesData"
            />
            <div v-else-if="isLoading" class="flex items-center justify-center py-8">
              <p class="text-muted-foreground">A carregar dados...</p>
            </div>
            <div v-else class="flex items-center justify-center py-8">
              <p class="text-muted-foreground">Sem dados para o período selecionado</p>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      <!-- Categories Tab -->
      <TabsContent value="categories" class="flex-1 flex flex-col space-y-4">
        <Card class="flex-1 flex flex-col">
          <CardHeader>
            <div class="flex items-center justify-between">
              <div>
                <CardTitle class="text-lg">Vendas por Categoria</CardTitle>
                <CardDescription>Performance agregada por categoria de produto ({{ categorySalesData.length }} categorias)</CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                @click="exportToCSV(categorySalesData, 'relatorio_categorias')"
                :disabled="categorySalesData.length === 0"
              >
                <Download class="mr-2 h-4 w-4" />
                Exportar CSV
              </Button>
            </div>
          </CardHeader>
          <CardContent class="flex-1">
            <ReportsCategoriesTable
              v-if="!isLoading && categorySalesData.length > 0"
              :categories="categorySalesData"
            />
            <div v-else-if="isLoading" class="flex items-center justify-center py-8">
              <p class="text-muted-foreground">A carregar dados...</p>
            </div>
            <div v-else class="flex items-center justify-center py-8">
              <p class="text-muted-foreground">Sem dados para o período selecionado</p>
            </div>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>

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
