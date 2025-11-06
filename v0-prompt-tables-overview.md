# v0 Prompt: Restaurant Tables Overview (MesasView.vue)

## Stack & Context
- **Framework:** Vue 3 with Composition API + TypeScript
- **UI Components:** shadcn/vue (Card, Badge, Button, Input, Select, Skeleton)
- **Icons:** Lucide Vue Next
- **Styling:** Tailwind CSS
- **State Management:** Pinia stores
- **Routing:** Vue Router

## Project Context
This is for a restaurant management system. We already have:
- Pinia stores for `tables` and `orders` with CRUD operations
- API services at `@/services/api` (tablesApi, ordersApi)
- Type definitions at `@/types/models` (Table, Order, OrderItem)
- Existing pattern: fetch data in `onMounted`, show loading states, use toast notifications

## Objective
Create a comprehensive tables overview page that displays all restaurant tables in a grid layout. Tables should show their current status (Available/Occupied/Reserved) and order information if occupied.

---

## Design Requirements

### Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│  Mesas                              [12 mesas]              │
│                                                             │
│  [Todas] [Disponíveis] [Ocupadas] [Reservadas]  [Search]  │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ Mesa 1  │  │ Mesa 2  │  │ Mesa 3  │  │ Mesa 4  │      │
│  │ [Disp.] │  │ [Ocup.] │  │ [Disp.] │  │ [Rese.] │      │
│  │ 👤 4    │  │ 👤 2    │  │ 👤 6    │  │ 👤 4    │      │
│  │         │  │ #123    │  │         │  │         │      │
│  │         │  │ €45.50  │  │         │  │         │      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Grid Layout
- **Desktop (lg):** 4 columns
- **Tablet (md):** 2 columns
- **Mobile (sm):** 1 column
- Use CSS Grid with gap-4
- Cards should have equal height

### Table Card Design

Each card must display:

1. **Header:**
   - Table number (large, bold): "Mesa {tableid}"
   - Status badge (top-right corner)

2. **Content:**
   - Capacity icon + number: Use `Users` icon from lucide-vue-next + text
   - For **OCCUPIED** tables only:
     - Order ID: "Pedido #123"
     - Grand total: "€45.50" (from order.grandTotal)
     - Time elapsed: "há 25 min" (calculated from order.created_at)

3. **Visual States:**
   - **Available (AV):**
     - Background: `bg-green-50 dark:bg-green-950`
     - Border: `border-l-4 border-green-500`
     - Badge: `bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200`
     - Text: "Disponível"

   - **Occupied (OC):**
     - Background: `bg-red-50 dark:bg-red-950`
     - Border: `border-l-4 border-red-500`
     - Badge: `bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200`
     - Text: "Ocupada"
     - Add subtle pulse animation: `animate-pulse` (slow)

   - **Reserved (RE):**
     - Background: `bg-yellow-50 dark:bg-yellow-950`
     - Border: `border-l-4 border-yellow-500`
     - Badge: `bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200`
     - Text: "Reservada"

4. **Interactions:**
   - Hover: Add shadow and subtle scale effect `hover:shadow-lg hover:scale-105 transition-all`
   - Click: Navigate to `/mesas/pedidos?table={tableId}` using `router.push()`
   - Cursor: `cursor-pointer`

### Top Bar Filters

1. **Status Filter Buttons:**
   - "Todas", "Disponíveis", "Ocupadas", "Reservadas"
   - Use Button component with variant="outline"
   - Active button: variant="default"
   - Clicking filters the displayed tables

2. **Search Input:**
   - Placeholder: "Pesquisar por número de mesa..."
   - Use Input component
   - Filters tables by tableid
   - Icon: `Search` from lucide-vue-next

3. **Sort Dropdown:**
   - Options: "Número ↑", "Número ↓", "Capacidade ↑", "Capacidade ↓"
   - Use Select component
   - Default: "Número ↑"

4. **Stats Badge:**
   - Show total table count: "12 mesas"
   - Use Badge component with variant="secondary"

---

## Technical Implementation

### TypeScript Interfaces

```typescript
interface Table {
  tableid: number
  capacity: number
  status: 'AV' | 'OC' | 'RE'
}

interface Order {
  orderID: number
  totalAmount: number
  totalIva: number
  grandTotal: number
  paymentStatus: 'PENDING' | 'PARTIALLY_PAID' | 'PAID' | 'FAILED'
  created_at: string
  items: OrderItem[]
  details: {
    table?: number | null
  }
}

interface TableWithOrder extends Table {
  currentOrder?: Order
}
```

### Component Structure

```vue
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Users, Search } from 'lucide-vue-next'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { useTablesStore } from '@/stores/tables'
import { useOrdersStore } from '@/stores/orders'
import type { Table, Order, TableWithOrder } from '@/types/models'

const router = useRouter()
const tablesStore = useTablesStore()
const ordersStore = useOrdersStore()

// State
const isLoading = ref(false)
const searchQuery = ref('')
const statusFilter = ref<'ALL' | 'AV' | 'OC' | 'RE'>('ALL')
const sortBy = ref<'number-asc' | 'number-desc' | 'capacity-asc' | 'capacity-desc'>('number-asc')
const tablesWithOrders = ref<TableWithOrder[]>([])
let refreshInterval: NodeJS.Timeout | null = null

// Computed
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

  // Sort
  result = [...result].sort((a, b) => {
    switch (sortBy.value) {
      case 'number-asc': return a.tableid - b.tableid
      case 'number-desc': return b.tableid - a.tableid
      case 'capacity-asc': return a.capacity - b.capacity
      case 'capacity-desc': return b.capacity - a.capacity
      default: return 0
    }
  })

  return result
})

// Methods
async function fetchData() {
  isLoading.value = true
  try {
    // Fetch tables and orders in parallel
    await Promise.all([
      tablesStore.fetchTables(),
      ordersApi.getOrders() // Or use ordersStore if you have one
    ])

    // Match tables with their orders
    const orders = await ordersApi.getOrders()
    const activeOrders = orders.filter(o => o.paymentStatus !== 'PAID')

    tablesWithOrders.value = tablesStore.tables.map(table => {
      const order = activeOrders.find(o => o.details.table === table.tableid)
      return { ...table, currentOrder: order }
    })
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    isLoading.value = false
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
```

### Loading State

Show 8 skeleton cards in grid layout:
```vue
<div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  <Card v-for="i in 8" :key="i" class="h-48">
    <CardContent class="p-6">
      <Skeleton class="h-8 w-24 mb-4" />
      <Skeleton class="h-4 w-32 mb-2" />
      <Skeleton class="h-4 w-24" />
    </CardContent>
  </Card>
</div>
```

### Empty State

```vue
<div v-if="!isLoading && filteredTables.length === 0" class="text-center py-12">
  <p class="text-muted-foreground text-lg">Nenhuma mesa encontrada</p>
  <p class="text-sm text-muted-foreground mt-2">
    {{ statusFilter !== 'ALL' ? 'Tente ajustar os filtros' : 'Adicione mesas nas configurações' }}
  </p>
</div>
```

---

## Color Palette Reference

```typescript
const statusConfig = {
  AV: {
    label: 'Disponível',
    cardBg: 'bg-green-50 dark:bg-green-950',
    border: 'border-l-4 border-green-500',
    badge: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  },
  OC: {
    label: 'Ocupada',
    cardBg: 'bg-red-50 dark:bg-red-950',
    border: 'border-l-4 border-red-500',
    badge: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    animation: 'animate-pulse'
  },
  RE: {
    label: 'Reservada',
    cardBg: 'bg-yellow-50 dark:bg-yellow-950',
    border: 'border-l-4 border-yellow-500',
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  }
}
```

---

## Additional Requirements

1. **Responsive Design:**
   - Mobile-first approach
   - Touch-friendly tap targets (min 44px)
   - Horizontal scroll for filter buttons on mobile

2. **Accessibility:**
   - Proper ARIA labels
   - Keyboard navigation support
   - Screen reader friendly

3. **Performance:**
   - Lazy load table cards if list is very long
   - Debounce search input

4. **Animations:**
   - Smooth transitions on filter/sort changes
   - Fade-in for cards on load
   - Gentle pulse for occupied tables

5. **Error Handling:**
   - Show error toast if fetch fails
   - Retry button on error state

---

## Expected Output

Please generate a complete Vue 3 Single File Component (.vue) with:
- `<script setup lang="ts">` section with all logic
- `<template>` section with complete markup
- Use only the shadcn/vue components and patterns mentioned
- Follow the existing project structure and naming conventions
- Include proper TypeScript types
- Add comments for complex logic

The component should be production-ready and follow Vue 3 best practices.
