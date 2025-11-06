<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ordersApi, menuApi, tablesApi } from '@/services/api'
import type { Order, OrderItem, MenuItem, MenuCategory, Table } from '@/types/models'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Users,
  CreditCard,
  ArrowRightLeft,
  Trash2,
  Minus,
  Plus,
  Search,
  ShoppingCart,
  ChefHat,
  Wine,
  Store,
  ArrowLeft,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

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

// Core data
const tableId = computed(() => Number(route.query.table))
const currentTable = ref<Table | null>(null)
const currentOrder = ref<Order | null>(null)
const menuItems = ref<MenuItem[]>([])
const categories = ref<MenuCategory[]>([])
const allTables = ref<Table[]>([])

// UI state
const isLoading = ref(false)
const isMounted = ref(true)
const selectedCategory = ref<number | null>(null)
const menuSearchQuery = ref('')
const cartItems = ref<Map<number, number>>(new Map()) // menuItemId -> quantity

// Dialogs
const showTransferDialog = ref(false)
const showDeleteDialog = ref(false)
const showPaymentDialog = ref(false)
const targetTableId = ref<string>('')

// Auto-refresh
let refreshInterval: NodeJS.Timeout | null = null

// Computed: Filtered menu items
const filteredMenuItems = computed(() => {
  if (!isMounted.value) return []

  let items = menuItems.value

  if (selectedCategory.value !== null) {
    items = items.filter(i => i.categoryID === selectedCategory.value)
  }

  if (menuSearchQuery.value) {
    items = items.filter(i =>
      i.name.toLowerCase().includes(menuSearchQuery.value.toLowerCase())
    )
  }

  return items
})

// Computed: Available tables for transfer (exclude current table and occupied tables)
const availableTables = computed(() => {
  if (!isMounted.value) return []
  return allTables.value.filter(t => t.tableid !== tableId.value)
})

// Computed: Cart total items
const cartTotalItems = computed(() => {
  if (!isMounted.value) return 0
  let total = 0
  cartItems.value.forEach(quantity => {
    total += quantity
  })
  return total
})

// Computed: Order totals
const orderTotals = computed(() => {
  if (!currentOrder.value || !isMounted.value) {
    return {
      totalAmount: 0,
      totalIva: 0,
      grandTotal: 0,
    }
  }
  return {
    totalAmount: Number(currentOrder.value.totalAmount || 0),
    totalIva: Number(currentOrder.value.totalIva || 0),
    grandTotal: Number(currentOrder.value.grandTotal || 0),
  }
})

// Status mappings
const paymentStatusConfig: Record<string, { label: string; variant: any }> = {
  PENDING: { label: 'Pagamento Pendente', variant: 'secondary' },
  PARTIALLY_PAID: { label: 'Parcialmente Pago', variant: 'default' },
  PAID: { label: 'Pago', variant: 'default' },
  FAILED: { label: 'Falhou', variant: 'destructive' },
}

const orderStatusConfig: Record<string, { label: string; variant: any }> = {
  PENDING: { label: 'Pendente', variant: 'secondary' },
  PREPARING: { label: 'A Preparar', variant: 'default' },
  READY: { label: 'Pronto', variant: 'default' },
  DELIVERED: { label: 'Entregue', variant: 'outline' },
  CANCELLED: { label: 'Cancelado', variant: 'destructive' },
}

const itemStatusConfig: Record<string, { label: string; variant: any }> = {
  '1': { label: 'Pendente', variant: 'secondary' },
  '2': { label: 'A Preparar', variant: 'default' },
  '3': { label: 'Pronto', variant: 'default' },
  '4': { label: 'Cancelado', variant: 'destructive' },
}

const preparedInConfig: Record<string, { label: string; icon: any }> = {
  '1': { label: 'Cozinha', icon: ChefHat },
  '2': { label: 'Bar', icon: Wine },
  '3': { label: 'Ambos', icon: Store },
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

// Fetch all initial data
async function fetchData() {
  if (!isMounted.value) return

  isLoading.value = true
  try {
    const [table, orders, items, cats, tables] = await Promise.all([
      tablesApi.getTable(tableId.value),
      ordersApi.getOrders(),
      menuApi.getItems(),
      menuApi.getCategories(),
      tablesApi.getTables(),
    ])

    if (!isMounted.value) return

    currentTable.value = table
    menuItems.value = items
    categories.value = cats
    allTables.value = tables

    // Find order for this table (exclude PAID orders)
    const tableOrder = orders.find(
      o => o.details.table === tableId.value && o.paymentStatus !== 'PAID'
    )
    currentOrder.value = tableOrder || null
  } catch (error: any) {
    if (!isMounted.value) return
    showToast(error.message || 'Erro ao carregar dados', 'error')
  } finally {
    if (isMounted.value) {
      isLoading.value = false
    }
  }
}

// Refresh order data
async function refreshOrder() {
  if (!currentOrder.value || !isMounted.value) return

  try {
    const updated = await ordersApi.getOrder(currentOrder.value.orderID)
    if (isMounted.value) {
      currentOrder.value = updated
    }
  } catch (error) {
    // Silent fail for auto-refresh
    console.error('Failed to refresh order:', error)
  }
}

// Create new order
async function createOrder() {
  if (!isMounted.value || cartItems.value.size === 0) return

  try {
    const payload = {
      items: Array.from(cartItems.value.entries()).map(([menu_item, quantity]) => ({
        menu_item,
        quantity,
      })),
      orderType: 'RESTAURANT' as const,
      details: { table: tableId.value },
    }

    const newOrder = await ordersApi.createOrder(payload)

    if (!isMounted.value) return

    currentOrder.value = newOrder
    cartItems.value.clear()

    showToast(`Pedido #${newOrder.orderID} criado com sucesso`, 'success')
  } catch (error: any) {
    if (!isMounted.value) return
    showToast(error.message || 'Erro ao criar pedido', 'error')
  }
}

// Add cart items to existing order
async function addCartToOrder() {
  if (!isMounted.value) return

  if (!currentOrder.value) {
    await createOrder()
    return
  }

  if (cartItems.value.size === 0) return

  try {
    const newItems = Array.from(cartItems.value.entries()).map(([menu_item, quantity]) => {
      const menuItem = menuItems.value.find(m => m.itemID === menu_item)
      const category = categories.value.find(c => c.categoryID === menuItem?.categoryID)

      return {
        menu_item,
        quantity,
        price: menuItem?.price || 0,
        status: '1' as const,
        to_be_prepared_in: category?.prepared_in || '1',
      }
    })

    const updated = await ordersApi.updateOrderItems(
      currentOrder.value.orderID,
      [...currentOrder.value.items, ...newItems]
    )

    if (!isMounted.value) return

    currentOrder.value = updated
    cartItems.value.clear()

    showToast(`${newItems.length} item(ns) adicionado(s) ao pedido`, 'success')
  } catch (error: any) {
    if (!isMounted.value) return
    showToast(error.message || 'Erro ao adicionar itens', 'error')
  }
}

// Update item quantity
async function updateItemQuantity(item: OrderItem, newQuantity: number) {
  if (!currentOrder.value || !isMounted.value) return

  try {
    const updatedItems = currentOrder.value.items.map(i =>
      i.menu_item === item.menu_item
        ? { ...i, quantity: newQuantity }
        : i
    )

    const updated = await ordersApi.updateOrderItems(
      currentOrder.value.orderID,
      updatedItems
    )

    if (!isMounted.value) return
    currentOrder.value = updated
  } catch (error: any) {
    if (!isMounted.value) return
    showToast(error.message || 'Erro ao atualizar quantidade', 'error')
  }
}

async function incrementQuantity(item: OrderItem) {
  await updateItemQuantity(item, item.quantity + 1)
}

async function decrementQuantity(item: OrderItem) {
  if (item.quantity > 1) {
    await updateItemQuantity(item, item.quantity - 1)
  }
}

// Delete item from order
async function deleteItem(item: OrderItem) {
  if (!currentOrder.value || !isMounted.value) return

  try {
    const updatedItems = currentOrder.value.items.filter(
      i => i.menu_item !== item.menu_item
    )

    if (updatedItems.length === 0) {
      // Delete entire order if no items left
      await ordersApi.deleteOrder(currentOrder.value.orderID)

      if (!isMounted.value) return

      currentOrder.value = null
      showToast('Pedido removido (sem itens)', 'success')
      router.push('/mesas')
    } else {
      const updated = await ordersApi.updateOrderItems(
        currentOrder.value.orderID,
        updatedItems
      )

      if (!isMounted.value) return

      currentOrder.value = updated
      showToast('Item removido do pedido', 'success')
    }
  } catch (error: any) {
    if (!isMounted.value) return
    showToast(error.message || 'Erro ao remover item', 'error')
  }
}

// Add to cart
function addToCart(menuItem: MenuItem) {
  const current = cartItems.value.get(menuItem.itemID) || 0
  cartItems.value.set(menuItem.itemID, current + 1)
}

// Transfer dialog
function openTransferDialog() {
  if (!currentOrder.value) return
  targetTableId.value = ''
  showTransferDialog.value = true
}

async function confirmTransfer() {
  if (!currentOrder.value || !targetTableId.value || !isMounted.value) return

  try {
    // Get or create target order
    const targetId = Number(targetTableId.value)
    const allOrders = await ordersApi.getOrders()
    let targetOrder = allOrders.find(
      o => o.details.table === targetId && o.paymentStatus !== 'PAID'
    )

    if (!targetOrder) {
      // Create new order for target table
      targetOrder = await ordersApi.createOrder({
        items: [],
        orderType: 'RESTAURANT',
        details: { table: targetId },
      })
    }

    // Transfer items
    await ordersApi.transferItems({
      source_order_id: currentOrder.value.orderID,
      target_order_id: targetOrder.orderID,
    })

    if (!isMounted.value) return

    showTransferDialog.value = false
    currentOrder.value = null

    showToast(`Pedido transferido para Mesa ${targetId}`, 'success')

    router.push('/mesas')
  } catch (error: any) {
    if (!isMounted.value) return
    showToast(error.message || 'Erro ao transferir pedido', 'error')
  }
}

// Delete order dialog
function openDeleteDialog() {
  if (!currentOrder.value) return
  showDeleteDialog.value = true
}

async function confirmDelete() {
  if (!currentOrder.value || !isMounted.value) return

  try {
    await ordersApi.deleteOrder(currentOrder.value.orderID)

    if (!isMounted.value) return

    showDeleteDialog.value = false
    currentOrder.value = null

    showToast('Pedido foi cancelado', 'success')

    router.push('/mesas')
  } catch (error: any) {
    if (!isMounted.value) return
    showToast(error.message || 'Erro ao cancelar pedido', 'error')
  }
}

// Payment dialog
function openPaymentDialog() {
  if (!currentOrder.value) return
  showPaymentDialog.value = true
  showToast('Funcionalidade de pagamento em breve', 'success')
}

// Get item name from menu
function getItemName(menuItemId: number): string {
  const item = menuItems.value.find(m => m.itemID === menuItemId)
  return item?.name || 'Item'
}

// Get item category
function getItemCategory(menuItemId: number): MenuCategory | undefined {
  const item = menuItems.value.find(m => m.itemID === menuItemId)
  if (!item) return undefined
  return categories.value.find(c => c.categoryID === item.categoryID)
}

// Back to tables
function goBack() {
  router.push('/mesas')
}

// Lifecycle
onMounted(() => {
  fetchData()

  // Auto-refresh every 15 seconds
  refreshInterval = setInterval(() => {
    if (isMounted.value) {
      refreshOrder()
    }
  }, 15000)
})

onUnmounted(() => {
  isMounted.value = false
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
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

    <!-- Breadcrumb / Header -->
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="icon" @click="goBack">
        <ArrowLeft class="h-5 w-5" />
      </Button>
      <div>
        <div class="text-sm text-muted-foreground">
          <span class="hover:underline cursor-pointer" @click="goBack">Mesas</span>
          <span class="mx-2">/</span>
          <span>Mesa {{ tableId }}</span>
        </div>
        <h1 class="text-3xl font-bold">Gestão de Pedidos</h1>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
      <div class="lg:col-span-3 space-y-4">
        <Skeleton class="h-48 w-full" />
        <Skeleton class="h-64 w-full" />
      </div>
      <div class="lg:col-span-6">
        <Skeleton class="h-96 w-full" />
      </div>
      <div class="lg:col-span-3">
        <Skeleton class="h-96 w-full" />
      </div>
    </div>

    <!-- Main Content: Three Column Layout -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 overflow-hidden">
      <!-- Column 1: Table Info & Summary (30%) -->
      <div class="lg:col-span-3 space-y-4 overflow-y-auto">
        <!-- Table Card -->
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <CardTitle>Mesa {{ tableId }}</CardTitle>
              <Badge :variant="currentTable?.status === 'OC' ? 'destructive' : 'secondary'">
                {{ currentTable?.status === 'OC' ? 'Ocupada' : currentTable?.status === 'RE' ? 'Reservada' : 'Disponível' }}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div class="space-y-2 text-sm">
              <div class="flex items-center gap-2">
                <Users class="h-4 w-4 text-muted-foreground" />
                <span>{{ currentTable?.capacity }} pessoas</span>
              </div>
              <Separator v-if="currentOrder" />
              <div v-if="currentOrder">
                <span class="text-muted-foreground">Pedido:</span>
                <span class="font-semibold"> #{{ currentOrder.orderID }}</span>
              </div>
              <div v-if="currentOrder">
                <span class="text-muted-foreground">Criado:</span>
                <span> {{ formatDateTime(currentOrder.created_at) }}</span>
              </div>
              <div v-if="currentOrder">
                <span class="text-muted-foreground">Atualizado:</span>
                <span> {{ formatDateTime(currentOrder.updated_at) }}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Order Summary Card -->
        <Card v-if="currentOrder">
          <CardHeader>
            <CardTitle class="text-lg">Resumo</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Subtotal:</span>
                <span>€{{ orderTotals.totalAmount.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">IVA (15%):</span>
                <span>€{{ orderTotals.totalIva.toFixed(2) }}</span>
              </div>
              <Separator />
              <div class="flex justify-between text-lg font-bold">
                <span>Total:</span>
                <span>€{{ orderTotals.grandTotal.toFixed(2) }}</span>
              </div>
              <div class="mt-2 space-y-1">
                <Badge :variant="paymentStatusConfig[currentOrder.paymentStatus]?.variant">
                  {{ paymentStatusConfig[currentOrder.paymentStatus]?.label }}
                </Badge>
                <br />
                <Badge :variant="orderStatusConfig[currentOrder.status]?.variant">
                  {{ orderStatusConfig[currentOrder.status]?.label }}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Action Buttons -->
        <div v-if="currentOrder" class="space-y-2">
          <Button class="w-full" size="lg" @click="openPaymentDialog">
            <CreditCard class="mr-2 h-4 w-4" />
            Processar Pagamento
          </Button>
          <Button class="w-full" variant="outline" @click="openTransferDialog">
            <ArrowRightLeft class="mr-2 h-4 w-4" />
            Transferir Pedido
          </Button>
          <Button class="w-full" variant="destructive" @click="openDeleteDialog">
            <Trash2 class="mr-2 h-4 w-4" />
            Cancelar Pedido
          </Button>
        </div>
      </div>

      <!-- Column 2: Order Items (45%) -->
      <div class="lg:col-span-6 flex flex-col overflow-hidden">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold flex items-center gap-2">
            Itens do Pedido
            <Badge v-if="currentOrder" variant="secondary">{{ currentOrder.items.length }}</Badge>
          </h2>
        </div>

        <div class="flex-1 overflow-y-auto space-y-3">
          <!-- No Order State -->
          <Card v-if="!currentOrder" class="border-dashed">
            <CardContent class="flex flex-col items-center justify-center py-12">
              <ShoppingCart class="h-12 w-12 text-muted-foreground mb-4" />
              <p class="text-lg font-semibold mb-2">Novo Pedido</p>
              <p class="text-sm text-muted-foreground">Adicione itens do menu para criar o pedido</p>
            </CardContent>
          </Card>

          <!-- Order Items -->
          <Card v-else v-for="item in currentOrder.items" :key="item.menu_item" class="mb-3">
            <CardContent class="p-4">
              <div class="flex items-start justify-between mb-2">
                <div class="flex-1">
                  <h3 class="font-semibold">{{ getItemName(item.menu_item) }}</h3>
                  <p class="text-sm text-muted-foreground">€{{ Number(item.price).toFixed(2) }}/un</p>
                </div>
                <div class="flex items-center gap-2">
                  <Badge variant="outline">
                    <component
                      :is="preparedInConfig[getItemCategory(item.menu_item)?.prepared_in || '1']?.icon"
                      class="h-3 w-3 mr-1"
                    />
                    {{ preparedInConfig[getItemCategory(item.menu_item)?.prepared_in || '1']?.label }}
                  </Badge>
                  <Button variant="ghost" size="icon" @click="deleteItem(item)">
                    <Trash2 class="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div class="flex items-center justify-between">
                <Badge :variant="itemStatusConfig[item.status]?.variant">
                  {{ itemStatusConfig[item.status]?.label }}
                </Badge>

                <div class="flex items-center gap-3">
                  <div class="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      @click="decrementQuantity(item)"
                      :disabled="item.quantity <= 1"
                    >
                      <Minus class="h-4 w-4" />
                    </Button>
                    <span class="w-8 text-center font-semibold">{{ item.quantity }}</span>
                    <Button variant="outline" size="icon" @click="incrementQuantity(item)">
                      <Plus class="h-4 w-4" />
                    </Button>
                  </div>

                  <div class="text-right min-w-[80px]">
                    <p class="text-xs text-muted-foreground">Subtotal</p>
                    <p class="font-semibold">€{{ (Number(item.price) * item.quantity).toFixed(2) }}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Sticky Footer: Totals -->
        <div v-if="currentOrder" class="border-t pt-4 mt-4 bg-background">
          <div class="flex justify-between text-sm mb-1">
            <span>Subtotal:</span>
            <span>€{{ orderTotals.totalAmount.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between text-sm mb-1">
            <span>IVA (15%):</span>
            <span>€{{ orderTotals.totalIva.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between font-bold text-lg">
            <span>Total:</span>
            <span>€{{ orderTotals.grandTotal.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Column 3: Add Items Menu (25%) -->
      <div class="lg:col-span-3 flex flex-col overflow-hidden">
        <div class="mb-4">
          <h2 class="text-xl font-bold mb-3">Adicionar Itens</h2>
          <div class="relative">
            <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input v-model="menuSearchQuery" placeholder="Buscar produtos..." class="pl-9" />
          </div>
        </div>

        <!-- Category Filter -->
        <div class="flex gap-2 overflow-x-auto pb-2 mb-4">
          <Button
            variant="outline"
            size="sm"
            :class="{ 'bg-primary text-primary-foreground': selectedCategory === null }"
            @click="selectedCategory = null"
          >
            Todas
          </Button>
          <Button
            v-for="category in categories"
            :key="category.categoryID"
            size="sm"
            :variant="selectedCategory === category.categoryID ? 'default' : 'outline'"
            @click="selectedCategory = category.categoryID"
          >
            {{ category.name }}
          </Button>
        </div>

        <!-- Menu Items List -->
        <div class="flex-1 overflow-y-auto space-y-2">
          <Card
            v-for="item in filteredMenuItems"
            :key="item.itemID"
            class="hover:bg-accent cursor-pointer transition-colors"
          >
            <CardContent class="p-3">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <h4 class="font-medium text-sm">{{ item.name }}</h4>
                  <p class="text-sm font-semibold text-primary">€{{ Number(item.price).toFixed(2) }}</p>
                </div>
                <Button
                  size="icon"
                  variant="ghost"
                  @click="addToCart(item)"
                  :disabled="!item.availability"
                >
                  <Plus class="h-4 w-4" />
                </Button>
              </div>
              <Badge v-if="!item.availability" variant="destructive" class="mt-1 text-xs">
                Indisponível
              </Badge>
            </CardContent>
          </Card>
        </div>

        <!-- Cart Summary (Sticky Bottom) -->
        <div class="border-t pt-4 mt-4 bg-background">
          <div v-if="cartTotalItems > 0" class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">No carrinho:</span>
              <span class="font-semibold">{{ cartTotalItems }} item(ns)</span>
            </div>
            <Button class="w-full" @click="addCartToOrder">
              <Plus class="mr-2 h-4 w-4" />
              Adicionar ao Pedido
            </Button>
          </div>
          <p v-else class="text-sm text-muted-foreground text-center py-2">Carrinho vazio</p>
        </div>
      </div>
    </div>

    <!-- Transfer Dialog -->
    <Dialog v-model:open="showTransferDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Transferir Todo o Pedido</DialogTitle>
          <DialogDescription>
            Selecione a mesa de destino. Todos os itens serão transferidos.
          </DialogDescription>
        </DialogHeader>

        <div class="space-y-4">
          <div>
            <Label>Mesa de Destino</Label>
            <Select v-model="targetTableId">
              <SelectTrigger>
                <SelectValue placeholder="Selecione a mesa" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="table in availableTables"
                  :key="table.tableid"
                  :value="String(table.tableid)"
                >
                  Mesa {{ table.tableid }} (👤 {{ table.capacity }})
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showTransferDialog = false">Cancelar</Button>
          <Button @click="confirmTransfer" :disabled="!targetTableId">Transferir</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete Order Dialog -->
    <Dialog v-model:open="showDeleteDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Cancelar Pedido?</DialogTitle>
          <DialogDescription>
            Esta ação não pode ser revertida. O pedido #{{ currentOrder?.orderID }} será cancelado.
          </DialogDescription>
        </DialogHeader>

        <div v-if="currentOrder" class="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
          <p class="text-sm font-semibold">Itens que serão removidos:</p>
          <ul class="text-sm mt-2 space-y-1">
            <li v-for="item in currentOrder.items" :key="item.menu_item">
              • {{ getItemName(item.menu_item) }} (x{{ item.quantity }})
            </li>
          </ul>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showDeleteDialog = false">Cancelar</Button>
          <Button variant="destructive" @click="confirmDelete">Sim, Cancelar Pedido</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
