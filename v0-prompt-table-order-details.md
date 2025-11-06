# v0 Prompt: Table Order Management (MesasPedidosView.vue)

## Stack & Context
- **Framework:** Vue 3 with Composition API + TypeScript
- **UI Components:** shadcn/vue (Card, Badge, Button, Input, Select, Dialog, Separator, Skeleton)
- **Icons:** Lucide Vue Next
- **Styling:** Tailwind CSS
- **State Management:** Pinia stores
- **Routing:** Vue Router

## Project Context
This is the order management page for a specific restaurant table. Users land here after clicking a table card from the tables overview. The page allows full order management: viewing, adding items, updating quantities, deleting items, and transferring between tables.

## Backend API Available

**Orders API:**
- `GET /api/order/?table={tableId}` - Get order for table (excludes PAID orders)
- `GET /api/order/{orderId}/` - Get order by ID
- `POST /api/order/register/` - Create new order
- `PATCH /api/order/{orderId}/update/` - Update order items (add/remove/change quantity)
- `POST /api/order/transfer/` - Transfer all items between orders
- `DELETE /api/order/{orderId}/delete/` - Delete order

**Menu API:**
- `GET /api/menu_item/` - Get all menu items
- `GET /api/menu_category/` - Get categories

**Tables API:**
- `GET /api/tables/{tableId}/` - Get table details

---

## Objective

Create a comprehensive order management interface with a three-column layout:
1. **Left:** Table info + Order summary + Action buttons
2. **Center:** Current order items with inline editing
3. **Right:** Menu browser to add new items

---

## Design Requirements

### Page Layout (Three Columns)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ← Mesas / Mesa 5                                                             │
├─────────────┬──────────────────────────────────┬─────────────────────────────┤
│ LEFT (30%)  │ CENTER (45%)                     │ RIGHT (25%)                 │
├─────────────┼──────────────────────────────────┼─────────────────────────────┤
│ ┌─────────┐ │ Itens do Pedido [5]              │ Adicionar Itens             │
│ │ Mesa 5  │ │ ┌──────────────────────────────┐ │ ┌─────────────────────────┐ │
│ │ [Ocupada]│ │ │ 🍔 Hambúrguer Clássico  [×] │ │ │ [Buscar...]             │ │
│ │ 👤 4     │ │ │ €12.50/un         [Pronto]  │ │ ├─────────────────────────┤ │
│ └─────────┘ │ │ [-] [2] [+]    Total: €25.00│ │ │ [Todas] [Entradas]      │ │
│             │ └──────────────────────────────┘ │ ├─────────────────────────┤ │
│ ┌─────────┐ │ ┌──────────────────────────────┐ │ │ ┌─────────────────────┐ │ │
│ │ Resumo  │ │ │ 🥤 Coca-Cola           [×]  │ │ │ │ Batatas Fritas  [+] │ │ │
│ │ Sub: €40│ │ │ €2.50/un       [Pendente]   │ │ │ │ €3.50               │ │ │
│ │ IVA: €6 │ │ │ [-] [3] [+]    Total: €7.50 │ │ │ └─────────────────────┘ │ │
│ │ ────────│ │ └──────────────────────────────┘ │ └─────────────────────────┘ │
│ │ Total:  │ │                                  │                             │
│ │ €46.00  │ │ Subtotal: €32.50                │ Cart: 2 items               │
│ └─────────┘ │ IVA (15%): €4.88                 │ [Adicionar ao Pedido]       │
│             │ Total: €37.38                    │                             │
│ [Pagamento] │                                  │                             │
│ [Transferir]│                                  │                             │
│ [Cancelar]  │                                  │                             │
└─────────────┴──────────────────────────────────┴─────────────────────────────┘
```

### Responsive Behavior
- **Desktop (lg):** Three columns as shown above
- **Tablet (md):** Two columns - Left+Center stacked, Right sidebar
- **Mobile (sm):** Single column, tabs to switch between "Pedido" / "Adicionar"

---

## Column 1: Table Info & Summary (Left - 30%)

### Table Card
```vue
<Card>
  <CardHeader>
    <div class="flex items-center justify-between">
      <CardTitle>Mesa {tableId}</CardTitle>
      <Badge variant="destructive">Ocupada</Badge>
    </div>
  </CardHeader>
  <CardContent>
    <div class="space-y-2 text-sm">
      <div class="flex items-center gap-2">
        <Users class="h-4 w-4 text-muted-foreground" />
        <span>{capacity} pessoas</span>
      </div>
      <Separator />
      <div>
        <span class="text-muted-foreground">Pedido:</span>
        <span class="font-semibold"> #{orderID}</span>
      </div>
      <div>
        <span class="text-muted-foreground">Criado:</span>
        <span> {formatDateTime(created_at)}</span>
      </div>
      <div>
        <span class="text-muted-foreground">Atualizado:</span>
        <span> {formatDateTime(updated_at)}</span>
      </div>
    </div>
  </CardContent>
</Card>
```

### Order Summary Card
```vue
<Card class="mt-4">
  <CardHeader>
    <CardTitle class="text-lg">Resumo</CardTitle>
  </CardHeader>
  <CardContent>
    <div class="space-y-2">
      <div class="flex justify-between text-sm">
        <span class="text-muted-foreground">Subtotal:</span>
        <span>€{totalAmount.toFixed(2)}</span>
      </div>
      <div class="flex justify-between text-sm">
        <span class="text-muted-foreground">IVA (15%):</span>
        <span>€{totalIva.toFixed(2)}</span>
      </div>
      <Separator />
      <div class="flex justify-between text-lg font-bold">
        <span>Total:</span>
        <span>€{grandTotal.toFixed(2)}</span>
      </div>
      <div class="mt-2">
        <Badge :variant="paymentStatusVariant">{paymentStatusLabel}</Badge>
      </div>
      <div>
        <Badge :variant="orderStatusVariant">{orderStatusLabel}</Badge>
      </div>
    </div>
  </CardContent>
</Card>
```

### Action Buttons
```vue
<div class="mt-4 space-y-2">
  <Button class="w-full" size="lg" @click="openPaymentDialog">
    <CreditCard class="mr-2 h-4 w-4" />
    Processar Pagamento
  </Button>
  <Button class="w-full" variant="outline" @click="openTransferDialog">
    <ArrowRightLeft class="mr-2 h-4 w-4" />
    Transferir Itens
  </Button>
  <Button class="w-full" variant="destructive" @click="openDeleteDialog">
    <Trash2 class="mr-2 h-4 w-4" />
    Cancelar Pedido
  </Button>
</div>
```

### Status Badge Mappings

**Payment Status:**
```typescript
const paymentStatusConfig = {
  PENDING: { label: 'Pagamento Pendente', variant: 'secondary' },
  PARTIALLY_PAID: { label: 'Parcialmente Pago', variant: 'default' },
  PAID: { label: 'Pago', variant: 'default' }, // Green
  FAILED: { label: 'Falhou', variant: 'destructive' }
}
```

**Order Status:**
```typescript
const orderStatusConfig = {
  PENDING: { label: 'Pendente', variant: 'secondary' },
  PREPARING: { label: 'A Preparar', variant: 'default' }, // Yellow/Orange
  READY: { label: 'Pronto', variant: 'default' }, // Green
  DELIVERED: { label: 'Entregue', variant: 'outline' },
  CANCELLED: { label: 'Cancelado', variant: 'destructive' }
}
```

---

## Column 2: Order Items (Center - 45%)

### Header
```vue
<div class="flex items-center justify-between mb-4">
  <h2 class="text-2xl font-bold">
    Itens do Pedido
    <Badge variant="secondary" class="ml-2">{order.items.length}</Badge>
  </h2>
</div>
```

### Order Item Card

Each item displays:
```vue
<Card class="mb-3">
  <CardContent class="p-4">
    <div class="flex items-start justify-between mb-2">
      <div class="flex-1">
        <h3 class="font-semibold">{item.name}</h3>
        <p class="text-sm text-muted-foreground">€{item.price}/un</p>
      </div>
      <div class="flex items-center gap-2">
        <Badge :variant="preparedInVariant">
          {preparedInLabel} <!-- Kitchen/Bar icon -->
        </Badge>
        <Button variant="ghost" size="icon" @click="deleteItem(item)">
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>
    </div>

    <div class="flex items-center justify-between">
      <Badge :variant="itemStatusVariant">{itemStatusLabel}</Badge>

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
          <span class="w-8 text-center font-semibold">{item.quantity}</span>
          <Button
            variant="outline"
            size="icon"
            @click="incrementQuantity(item)"
          >
            <Plus class="h-4 w-4" />
          </Button>
        </div>

        <div class="text-right min-w-[80px]">
          <p class="text-sm text-muted-foreground">Subtotal</p>
          <p class="font-semibold">€{(item.price * item.quantity).toFixed(2)}</p>
        </div>
      </div>
    </div>
  </CardContent>
</Card>
```

### Item Status Mappings
```typescript
const itemStatusConfig = {
  '1': { label: 'Pendente', variant: 'secondary' },
  '2': { label: 'A Preparar', variant: 'default' }, // Yellow
  '3': { label: 'Pronto', variant: 'default' }, // Green
  '4': { label: 'Cancelado', variant: 'destructive' }
}
```

### Prepared In Mappings
```typescript
const preparedInConfig = {
  '1': { label: 'Cozinha', icon: ChefHat },
  '2': { label: 'Bar', icon: Wine },
  '3': { label: 'Ambos', icon: Store }
}
```

### Empty State (No Items)
```vue
<Card class="border-dashed">
  <CardContent class="flex flex-col items-center justify-center py-12">
    <ShoppingCart class="h-12 w-12 text-muted-foreground mb-4" />
    <p class="text-lg text-muted-foreground">Pedido vazio</p>
    <p class="text-sm text-muted-foreground">Adicione itens do menu</p>
  </CardContent>
</Card>
```

### Sticky Footer (Totals Recap)
```vue
<div class="sticky bottom-0 bg-background border-t p-4 mt-4">
  <div class="flex justify-between text-sm mb-1">
    <span>Subtotal:</span>
    <span>€{totalAmount.toFixed(2)}</span>
  </div>
  <div class="flex justify-between text-sm mb-1">
    <span>IVA (15%):</span>
    <span>€{totalIva.toFixed(2)}</span>
  </div>
  <div class="flex justify-between font-bold text-lg">
    <span>Total:</span>
    <span>€{grandTotal.toFixed(2)}</span>
  </div>
</div>
```

---

## Column 3: Add Items Menu (Right - 25%)

### Header & Search
```vue
<div class="mb-4">
  <h2 class="text-xl font-bold mb-3">Adicionar Itens</h2>
  <div class="relative">
    <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
    <Input
      v-model="menuSearchQuery"
      placeholder="Buscar produtos..."
      class="pl-9"
    />
  </div>
</div>
```

### Category Filter Tabs
```vue
<div class="flex gap-2 overflow-x-auto pb-2 mb-4">
  <Button
    v-for="category in categories"
    :key="category.categoryID"
    :variant="selectedCategory === category.categoryID ? 'default' : 'outline'"
    size="sm"
    @click="selectedCategory = category.categoryID"
  >
    {category.name}
  </Button>
  <Button
    :variant="selectedCategory === null ? 'default' : 'outline'"
    size="sm"
    @click="selectedCategory = null"
  >
    Todas
  </Button>
</div>
```

### Menu Items List
```vue
<div class="space-y-2 max-h-[500px] overflow-y-auto">
  <Card
    v-for="item in filteredMenuItems"
    :key="item.itemID"
    class="hover:bg-accent cursor-pointer transition-colors"
  >
    <CardContent class="p-3">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <h4 class="font-medium text-sm">{item.name}</h4>
          <p class="text-sm font-semibold text-primary">€{item.price.toFixed(2)}</p>
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
      <Badge v-if="!item.availability" variant="destructive" class="mt-1">
        Indisponível
      </Badge>
    </CardContent>
  </Card>
</div>
```

### Cart Summary (Sticky Bottom)
```vue
<div class="sticky bottom-0 bg-background border-t p-4 mt-4">
  <div v-if="cartItems.size > 0" class="space-y-2">
    <div class="flex justify-between text-sm">
      <span class="text-muted-foreground">No carrinho:</span>
      <span class="font-semibold">{cartItems.size} itens</span>
    </div>
    <Button class="w-full" @click="addCartToOrder">
      <Plus class="mr-2 h-4 w-4" />
      Adicionar ao Pedido
    </Button>
  </div>
  <p v-else class="text-sm text-muted-foreground text-center">
    Carrinho vazio
  </p>
</div>
```

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
  customer?: number | null
  items: OrderItem[]
  status: 'PENDING' | 'PREPARING' | 'READY' | 'DELIVERED' | 'CANCELLED'
  totalAmount: number
  totalIva: number
  grandTotal: number
  paymentStatus: 'PENDING' | 'PARTIALLY_PAID' | 'PAID' | 'FAILED'
  orderType: 'RESTAURANT' | 'ONLINE'
  created_at: string
  updated_at: string
  details: {
    table?: number | null
  }
}

interface OrderItem {
  menu_item: number
  name?: string
  quantity: number
  price: number
  status: '1' | '2' | '3' | '4'
  to_be_prepared_in: string
}

interface MenuItem {
  itemID: number
  name: string
  description: string
  price: number
  categoryID: number
  availability: boolean
  is_quantifiable: boolean
}

interface MenuCategory {
  categoryID: number
  name: string
  prepared_in: '1' | '2' | '3'
}
```

### Component State

```typescript
const route = useRoute()
const router = useRouter()

// Core data
const tableId = computed(() => Number(route.query.table))
const currentTable = ref<Table | null>(null)
const currentOrder = ref<Order | null>(null)
const menuItems = ref<MenuItem[]>([])
const categories = ref<MenuCategory[]>([])

// UI state
const isLoading = ref(false)
const selectedCategory = ref<number | null>(null)
const menuSearchQuery = ref('')
const cartItems = ref<Map<number, number>>(new Map()) // menuItemId -> quantity

// Dialogs
const showTransferDialog = ref(false)
const showDeleteDialog = ref(false)
const showPaymentDialog = ref(false)

// Computed
const filteredMenuItems = computed(() => {
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
```

### Key Methods

```typescript
// Fetch initial data
async function fetchData() {
  isLoading.value = true
  try {
    const [table, orders, items, cats] = await Promise.all([
      tablesApi.getTable(tableId.value),
      ordersApi.getOrders(),
      menuApi.getItems(),
      menuApi.getCategories()
    ])

    currentTable.value = table
    menuItems.value = items
    categories.value = cats

    // Find order for this table
    const tableOrder = orders.find(
      o => o.details.table === tableId.value && o.paymentStatus !== 'PAID'
    )
    currentOrder.value = tableOrder || null
  } finally {
    isLoading.value = false
  }
}

// Create order if none exists
async function createOrder() {
  if (!currentOrder.value && cartItems.value.size > 0) {
    const payload = {
      items: Array.from(cartItems.value.entries()).map(([menu_item, quantity]) => ({
        menu_item,
        quantity
      })),
      orderType: 'RESTAURANT' as const,
      details: { table: tableId.value }
    }

    currentOrder.value = await ordersApi.createOrder(payload)
    cartItems.value.clear()
  }
}

// Add items to existing order
async function addCartToOrder() {
  if (!currentOrder.value) {
    await createOrder()
    return
  }

  // Add cart items to existing order
  const newItems = Array.from(cartItems.value.entries()).map(([menu_item, quantity]) => ({
    menu_item,
    quantity
  }))

  currentOrder.value = await ordersApi.updateOrderItems(
    currentOrder.value.orderID,
    [...currentOrder.value.items, ...newItems]
  )

  cartItems.value.clear()
}

// Update item quantity
async function updateItemQuantity(item: OrderItem, newQuantity: number) {
  if (!currentOrder.value) return

  const updatedItems = currentOrder.value.items.map(i =>
    i.menu_item === item.menu_item
      ? { ...i, quantity: newQuantity }
      : i
  )

  currentOrder.value = await ordersApi.updateOrderItems(
    currentOrder.value.orderID,
    updatedItems
  )
}

async function incrementQuantity(item: OrderItem) {
  await updateItemQuantity(item, item.quantity + 1)
}

async function decrementQuantity(item: OrderItem) {
  if (item.quantity > 1) {
    await updateItemQuantity(item, item.quantity - 1)
  }
}

// Delete item
async function deleteItem(item: OrderItem) {
  if (!currentOrder.value) return

  const updatedItems = currentOrder.value.items.filter(
    i => i.menu_item !== item.menu_item
  )

  if (updatedItems.length === 0) {
    // Delete entire order if no items left
    await ordersApi.deleteOrder(currentOrder.value.orderID)
    currentOrder.value = null
    router.push('/mesas')
  } else {
    currentOrder.value = await ordersApi.updateOrderItems(
      currentOrder.value.orderID,
      updatedItems
    )
  }
}

// Add to cart
function addToCart(menuItem: MenuItem) {
  const current = cartItems.value.get(menuItem.itemID) || 0
  cartItems.value.set(menuItem.itemID, current + 1)
}

// Format helpers
function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
```

---

## Dialogs

### Transfer Items Dialog

```vue
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
              Mesa {table.tableid} (👤 {table.capacity})
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>

    <DialogFooter>
      <Button variant="outline" @click="showTransferDialog = false">
        Cancelar
      </Button>
      <Button @click="confirmTransfer" :disabled="!targetTableId">
        Transferir
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Delete Order Dialog

```vue
<Dialog v-model:open="showDeleteDialog">
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Cancelar Pedido?</DialogTitle>
      <DialogDescription>
        Esta ação não pode ser revertida. O pedido #{currentOrder?.orderID} será cancelado.
      </DialogDescription>
    </DialogHeader>

    <div class="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
      <p class="text-sm font-semibold">Itens que serão removidos:</p>
      <ul class="text-sm mt-2 space-y-1">
        <li v-for="item in currentOrder?.items" :key="item.menu_item">
          • {item.name} (x{item.quantity})
        </li>
      </ul>
    </div>

    <DialogFooter>
      <Button variant="outline" @click="showDeleteDialog = false">
        Cancelar
      </Button>
      <Button variant="destructive" @click="confirmDelete">
        Sim, Cancelar Pedido
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

## Additional Features

### Loading States
- Show skeletons for all three columns during initial load
- Disable buttons during API operations
- Show loading spinner on action buttons

### Error Handling
- Toast notifications for all errors
- Graceful degradation if API fails
- Retry mechanism for failed requests

### Auto-refresh
- Poll order status every 15 seconds
- Highlight items that changed status
- Show notification when status changes

### Breadcrumb Navigation
```vue
<div class="mb-6">
  <Breadcrumb>
    <BreadcrumbList>
      <BreadcrumbItem>
        <BreadcrumbLink href="/mesas">Mesas</BreadcrumbLink>
      </BreadcrumbItem>
      <BreadcrumbSeparator />
      <BreadcrumbItem>
        <BreadcrumbPage>Mesa {tableId}</BreadcrumbPage>
      </BreadcrumbItem>
    </BreadcrumbList>
  </Breadcrumb>
</div>
```

### No Order State
If table has no active order, show a welcome card:
```vue
<Card v-if="!currentOrder" class="col-span-2">
  <CardContent class="flex flex-col items-center justify-center py-12">
    <ShoppingBag class="h-16 w-16 text-muted-foreground mb-4" />
    <h3 class="text-xl font-semibold mb-2">Novo Pedido</h3>
    <p class="text-muted-foreground mb-4">Adicione itens para criar o pedido</p>
  </CardContent>
</Card>
```

---

## Expected Output

Please generate a complete Vue 3 Single File Component (.vue) with:
- `<script setup lang="ts">` section with all logic
- `<template>` section with the three-column responsive layout
- All necessary imports from shadcn/vue and lucide-vue-next
- Proper TypeScript types and interfaces
- Error handling and loading states
- Dialog components for transfer and delete
- Comments explaining complex logic

The component should be production-ready, follow Vue 3 best practices, and integrate seamlessly with the existing Pinia stores and API services.
