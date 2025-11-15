<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { tablesApi, type Table } from '@/services/api'
import { useOrdersStore } from '@/stores/orders'
import { useTablePositions } from '@/composables/useTablePositions'
import DraggableTable from '@/components/tables/DraggableTable.vue'
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
  LayoutGrid,
  RefreshCw,
  RotateCcw,
  Lock,
  Unlock,
  Plus,
  Info,
} from 'lucide-vue-next'

const router = useRouter()
const ordersStore = useOrdersStore()

// State
const tables = ref<Table[]>([])
const isLoading = ref(true)
const isEditMode = ref(false)
const selectedTable = ref<Table | null>(null)
const showLegend = ref(true)

// Table positions
const { positions, getPosition, updatePosition, initializePositions, resetPositions } = useTablePositions()

// Statistics
const statistics = computed(() => {
  const total = tables.value.length
  const available = tables.value.filter(t => t.status === 'AV').length
  const occupied = tables.value.filter(t => t.status === 'OC').length
  const reserved = tables.value.filter(t => t.status === 'RE').length

  return {
    total,
    available,
    occupied,
    reserved,
  }
})

// Toast
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

function showToast(message: string, variant: 'success' | 'error' = 'success') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

// Fetch tables
async function fetchTables() {
  try {
    isLoading.value = true
    tables.value = await tablesApi.getTables()
    initializePositions(tables.value)
  } catch (error) {
    console.error('Error fetching tables:', error)
    showToast('Erro ao carregar mesas', 'error')
  } finally {
    isLoading.value = false
  }
}

// Fetch orders
async function fetchOrders() {
  try {
    await ordersStore.fetchOrders()
  } catch (error) {
    console.error('Error fetching orders:', error)
  }
}

// Handle table drag end
function handleTableDragEnd(tableId: number, x: number, y: number) {
  updatePosition(tableId, x, y)
  showToast('Posição da mesa atualizada')
}

// Handle table click
function handleTableClick(table: Table) {
  if (!isEditMode.value) {
    selectedTable.value = table
    // Navigate to orders for this table or show order assignment dialog
    router.push(`/mesas/pedidos?table=${table.tableid}`)
  }
}

// Toggle edit mode
function toggleEditMode() {
  isEditMode.value = !isEditMode.value
  if (isEditMode.value) {
    showToast('Modo de edição ativado - arraste as mesas para reposicionar')
  } else {
    showToast('Modo de edição desativado')
  }
}

// Reset layout to default grid
function handleResetLayout() {
  if (confirm('Tem certeza que deseja redefinir o layout das mesas para a grade padrão?')) {
    resetPositions(tables.value)
    showToast('Layout redefinido para o padrão')
  }
}

// Refresh all data
async function refreshData() {
  await Promise.all([fetchTables(), fetchOrders()])
  showToast('Dados atualizados')
}

// Lifecycle
onMounted(async () => {
  await Promise.all([fetchTables(), fetchOrders()])
  // Initialize WebSocket for real-time updates
  ordersStore.initWebSocket()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold flex items-center gap-2">
          <LayoutGrid class="h-8 w-8" />
          Layout das Mesas
        </h1>
        <p class="text-muted-foreground">Vista visual do salão do restaurante</p>
      </div>
      <div class="flex gap-2">
        <Button variant="outline" size="sm" @click="showLegend = !showLegend">
          <Info class="mr-2 h-4 w-4" />
          {{ showLegend ? 'Ocultar' : 'Mostrar' }} Legenda
        </Button>
        <Button variant="outline" @click="refreshData" :disabled="isLoading">
          <RefreshCw :class="['mr-2 h-4 w-4', { 'animate-spin': isLoading }]" />
          Atualizar
        </Button>
        <Button variant="outline" @click="handleResetLayout" :disabled="!isEditMode">
          <RotateCcw class="mr-2 h-4 w-4" />
          Resetar Layout
        </Button>
        <Button @click="toggleEditMode">
          <component :is="isEditMode ? Lock : Unlock" class="mr-2 h-4 w-4" />
          {{ isEditMode ? 'Bloquear' : 'Editar Layout' }}
        </Button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total de Mesas</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statistics.total }}</div>
          <p class="text-xs text-muted-foreground mt-1">No restaurante</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Disponíveis</CardTitle>
          <div class="w-3 h-3 rounded-full bg-green-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-green-600">{{ statistics.available }}</div>
          <p class="text-xs text-muted-foreground mt-1">Prontas para uso</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Ocupadas</CardTitle>
          <div class="w-3 h-3 rounded-full bg-red-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-red-600">{{ statistics.occupied }}</div>
          <p class="text-xs text-muted-foreground mt-1">Com clientes</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Reservadas</CardTitle>
          <div class="w-3 h-3 rounded-full bg-yellow-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-yellow-600">{{ statistics.reserved }}</div>
          <p class="text-xs text-muted-foreground mt-1">Reservas confirmadas</p>
        </CardContent>
      </Card>
    </div>

    <!-- Legend Card -->
    <Card v-if="showLegend" class="border-blue-200">
      <CardHeader class="pb-3">
        <CardTitle class="text-sm flex items-center gap-2">
          <Info class="h-4 w-4" />
          Instruções
        </CardTitle>
      </CardHeader>
      <CardContent class="space-y-2 text-sm">
        <div class="flex items-center gap-2">
          <Badge variant="outline">Clique</Badge>
          <span>numa mesa para ver/criar pedidos</span>
        </div>
        <div class="flex items-center gap-2">
          <Badge variant="outline">Editar Layout</Badge>
          <span>para arrastar e reorganizar as mesas</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 rounded-full bg-orange-500 border-2 border-white" />
          <span>Indica items pendentes na cozinha</span>
        </div>
      </CardContent>
    </Card>

    <!-- Floor Plan -->
    <Card class="flex-1 overflow-hidden">
      <CardContent class="h-full p-0 relative">
        <div
          v-if="!isLoading"
          class="relative w-full h-full overflow-auto"
          style="min-height: 600px;"
        >
          <!-- Draggable Tables -->
          <DraggableTable
            v-for="table in tables"
            :key="table.tableid"
            :table="table"
            :x="getPosition(table.tableid)?.x || 0"
            :y="getPosition(table.tableid)?.y || 0"
            :width="getPosition(table.tableid)?.width || 120"
            :height="getPosition(table.tableid)?.height || 120"
            :orders="ordersStore.orders"
            :is-draggable="isEditMode"
            @drag-end="handleTableDragEnd"
            @click="handleTableClick"
          />

          <!-- Edit Mode Overlay Message -->
          <div
            v-if="isEditMode"
            class="absolute top-4 left-1/2 transform -translate-x-1/2 z-40 pointer-events-none"
          >
            <Badge variant="default" class="text-sm py-2 px-4 shadow-lg">
              Modo de Edição: Arraste as mesas para reposicionar
            </Badge>
          </div>
        </div>

        <!-- Loading State -->
        <div v-else class="flex items-center justify-center h-full">
          <RefreshCw class="h-12 w-12 animate-spin text-muted-foreground" />
        </div>
      </CardContent>
    </Card>

    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      :class="[
        'fixed bottom-4 right-4 z-50 rounded-md px-6 py-4  shadow-lg transition-all',
        toastVariant === 'success' ? 'bg-green-600' : 'bg-red-600',
      ]"
    >
      {{ toastMessage }}
    </div>
  </div>
</template>
