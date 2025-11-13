<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useOrdersStore } from '@/stores/orders'
import type { Order, OrderItem } from '@/types/models/order'
import { ordersApi } from '@/services/api'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import {
  RefreshCw,
  ChefHat,
  Wine,
  Store,
  Clock,
  CheckCircle,
  Circle,
  Play,
  Check,
  AlertCircle,
} from 'lucide-vue-next'

// Initialize store
const ordersStore = useOrdersStore()

// State
const activeStation = ref<string>('1') // 1: Kitchen, 2: Bar, 3: Store
const isLoading = ref(false)
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

function showToast(message: string, variant: 'success' | 'error' = 'success') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

// Helper functions
function getStationLabel(station: string): string {
  switch (station) {
    case '1': return 'Cozinha'
    case '2': return 'Bar'
    case '3': return 'Balcão'
    default: return 'Desconhecido'
  }
}

function getStationIcon(station: string) {
  switch (station) {
    case '1': return ChefHat
    case '2': return Wine
    case '3': return Store
    default: return Store
  }
}

function getItemStatusLabel(status: string): string {
  switch (status) {
    case '1': return 'Pendente'
    case '2': return 'A Preparar'
    case '3': return 'Pronto'
    case '4': return 'Entregue'
    default: return status
  }
}

function getItemStatusIcon(status: string) {
  switch (status) {
    case '1': return Circle
    case '2': return Play
    case '3': return Check
    case '4': return CheckCircle
    default: return Circle
  }
}

function getItemStatusVariant(status: string): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case '1': return 'secondary'
    case '2': return 'outline'
    case '3': return 'default'
    case '4': return 'default'
    default: return 'secondary'
  }
}

// Computed: Active orders (not delivered or cancelled)
const activeOrders = computed(() => {
  return ordersStore.orders.filter(order =>
    order.status !== 'DELIVERED' &&
    order.status !== 'CANCELLED' &&
    order.items.length > 0
  )
})

// Computed: Orders grouped by station
const ordersByStation = computed(() => {
  return activeOrders.value.filter(order =>
    order.items.some(item => item.to_be_prepared_in === activeStation.value)
  )
})

// Computed: Statistics
const statistics = computed(() => {
  const stationOrders = ordersByStation.value

  // Count items by status for current station
  let pendingItems = 0
  let preparingItems = 0
  let readyItems = 0

  stationOrders.forEach(order => {
    order.items.forEach(item => {
      if (item.to_be_prepared_in === activeStation.value) {
        switch (item.status) {
          case '1': pendingItems++; break
          case '2': preparingItems++; break
          case '3': readyItems++; break
        }
      }
    })
  })

  return {
    totalOrders: stationOrders.length,
    pendingItems,
    preparingItems,
    readyItems,
  }
})

// Update order item status
async function updateItemStatus(item: OrderItem, newStatus: string) {
  try {
    // Debug: Log the item to see what we have
    console.log('Updating item:', item)

    if (!item.id) {
      console.error('Item sem ID:', item)
      showToast(`Item ID não encontrado. Item: ${item.name || item.menu_item}`, 'error')
      return
    }

    isLoading.value = true

    const updatedOrder = await ordersApi.updateOrderItemStatus(item.id, newStatus)
    console.log('Order atualizada:', updatedOrder)

    showToast('Estado atualizado com sucesso')
  } catch (error) {
    console.error('Error updating item status:', error)
    showToast('Erro ao atualizar estado', 'error')
  } finally {
    isLoading.value = false
  }
}

// Mark item as preparing (status 1 -> 2)
async function startPreparing(item: OrderItem) {
  await updateItemStatus(item, '2')
}

// Mark item as ready (status 2 -> 3)
async function markAsReady(item: OrderItem) {
  await updateItemStatus(item, '3')
}

// Mark item as delivered (status 3 -> 4)
async function markAsDelivered(item: OrderItem) {
  await updateItemStatus(item, '4')
}

// Format time
function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'agora mesmo'
  if (diffMins < 60) return `há ${diffMins}min`

  const diffHours = Math.floor(diffMins / 60)
  return `há ${diffHours}h ${diffMins % 60}min`
}

// Get time urgency class
function getTimeUrgencyClass(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMins = Math.floor((now.getTime() - date.getTime()) / 60000)

  if (diffMins > 30) return 'text-red-600 font-bold'
  if (diffMins > 15) return 'text-orange-600 font-semibold'
  return 'text-muted-foreground'
}

// Refresh orders
async function refreshOrders() {
  try {
    isLoading.value = true
    await ordersStore.fetchOrders()

    // Debug: Log orders to see if items have IDs
    console.log('Orders carregadas:', ordersStore.orders.length)
    if (ordersStore.orders.length > 0) {
      console.log('Exemplo de order com items:', ordersStore.orders[0])
      if (ordersStore.orders[0].items.length > 0) {
        console.log('Exemplo de item:', ordersStore.orders[0].items[0])
      }
    }

    showToast('Pedidos atualizados')
  } catch (error) {
    console.error('Error fetching orders:', error)
    showToast('Erro ao carregar pedidos', 'error')
  } finally {
    isLoading.value = false
  }
}

// Lifecycle hooks
onMounted(() => {
  // Initialize WebSocket for real-time updates
  ordersStore.initWebSocket()
  // Load initial orders
  refreshOrders()
})

onUnmounted(() => {
  // Close WebSocket connection
  ordersStore.closeWebSocket()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6 ">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold flex items-center gap-2">
          <ChefHat class="h-8 w-8" />
          Cozinha
        </h1>
        <p class="text-muted-foreground">Vista de preparação de pedidos em tempo real</p>
      </div>
      <Button @click="refreshOrders" :disabled="isLoading">
        <RefreshCw :class="['mr-2 h-4 w-4', { 'animate-spin': isLoading }]" />
        Atualizar
      </Button>
    </div>

    <!-- Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Pedidos Ativos</CardTitle>
          <AlertCircle class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statistics.totalOrders }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Na estação atual
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Pendentes</CardTitle>
          <Circle class="h-4 w-4 text-orange-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-orange-600">{{ statistics.pendingItems }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Aguardam preparação
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">A Preparar</CardTitle>
          <Play class="h-4 w-4 text-blue-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-blue-600">{{ statistics.preparingItems }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Em preparação
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Prontos</CardTitle>
          <Check class="h-4 w-4 text-green-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-green-600">{{ statistics.readyItems }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Prontos a servir
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Station Tabs -->
    <Tabs v-model="activeStation" class="flex-1 flex flex-col">
      <TabsList class="grid w-full grid-cols-3">
        <TabsTrigger value="1" class="flex items-center gap-2">
          <ChefHat class="h-4 w-4" />
          Cozinha
        </TabsTrigger>
        <TabsTrigger value="2" class="flex items-center gap-2">
          <Wine class="h-4 w-4" />
          Bar
        </TabsTrigger>
        <TabsTrigger value="3" class="flex items-center gap-2">
          <Store class="h-4 w-4" />
          Balcão
        </TabsTrigger>
      </TabsList>

      <TabsContent :value="activeStation" class="flex-1 mt-4">
        <!-- Orders Grid -->
        <div v-if="ordersByStation.length > 0" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <Card
            v-for="order in ordersByStation"
            :key="order.orderID"
            class="hover:shadow-lg transition-shadow"
          >
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-lg">Pedido #{{ order.orderID }}</CardTitle>
                <Badge variant="outline">
                  Mesa {{ order.details?.table || '—' }}
                </Badge>
              </div>
              <CardDescription class="flex items-center gap-2">
                <Clock class="h-3 w-3" />
                <span :class="getTimeUrgencyClass(order.created_at)">
                  {{ formatTime(order.created_at) }}
                </span>
              </CardDescription>
            </CardHeader>
            <CardContent class="space-y-3">
              <!-- Order Items -->
              <div
                v-for="(item, index) in order.items"
                :key="index"
                class="space-y-2"
              >
                <!-- Only show items for current station -->
                <template v-if="item.to_be_prepared_in === activeStation">
                  <div class="flex items-start justify-between gap-2">
                    <div class="flex-1">
                      <div class="font-medium">
                        {{ item.quantity }}x {{ item.name || `Item #${item.menu_item}` }}
                      </div>
                      <div class="flex items-center gap-2 mt-1">
                        <Badge :variant="getItemStatusVariant(item.status)" class="text-xs">
                          <component :is="getItemStatusIcon(item.status)" class="h-3 w-3 mr-1" />
                          {{ getItemStatusLabel(item.status) }}
                        </Badge>
                      </div>
                    </div>

                    <!-- Action Buttons -->
                    <div class="flex flex-col gap-1">
                      <Button
                        v-if="item.status === '1'"
                        size="sm"
                        variant="outline"
                        @click="startPreparing(item)"
                        :disabled="isLoading"
                        class="whitespace-nowrap"
                      >
                        <Play class="h-3 w-3 mr-1" />
                        Iniciar
                      </Button>

                      <Button
                        v-if="item.status === '2'"
                        size="sm"
                        variant="default"
                        @click="markAsReady(item)"
                        :disabled="isLoading"
                        class="whitespace-nowrap"
                      >
                        <Check class="h-3 w-3 mr-1" />
                        Pronto
                      </Button>

                      <Button
                        v-if="item.status === '3'"
                        size="sm"
                        variant="secondary"
                        @click="markAsDelivered(item)"
                        :disabled="isLoading"
                        class="whitespace-nowrap"
                      >
                        <CheckCircle class="h-3 w-3 mr-1" />
                        Entregar
                      </Button>
                    </div>
                  </div>
                  <Separator v-if="index < order.items.length - 1" />
                </template>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Empty State -->
        <Card v-else class="flex items-center justify-center py-12">
          <CardContent class="text-center">
            <component :is="getStationIcon(activeStation)" class="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p class="text-muted-foreground text-lg">
              Nenhum pedido pendente para {{ getStationLabel(activeStation) }}
            </p>
            <p class="text-sm text-muted-foreground mt-2">
              Os novos pedidos aparecerão aqui automaticamente
            </p>
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
