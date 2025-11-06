# Implementation Guide: Tables & Orders Views

This guide will help you implement the Tables Overview and Order Management views using the v0 prompts provided.

## 📁 Files in This Package

1. **`v0-prompt-tables-overview.md`** - Prompt for MesasView.vue (tables grid)
2. **`v0-prompt-table-order-details.md`** - Prompt for MesasPedidosView.vue (order management)
3. **`IMPLEMENTATION_GUIDE.md`** - This file (step-by-step instructions)

---

## 🎯 What You're Building

### View 1: Tables Overview (`/mesas`)
A responsive grid showing all restaurant tables with:
- Visual status indicators (Available/Occupied/Reserved)
- Real-time order information for occupied tables
- Filtering and search capabilities
- Click to navigate to order details

### View 2: Table Order Management (`/mesas/pedidos?table={id}`)
A comprehensive order management interface with:
- Three-column layout: Table info | Order items | Add items menu
- Full CRUD operations on order items
- Transfer items between tables
- Process payments and cancel orders

---

## 🚀 Step-by-Step Implementation

### Step 1: Prepare Your Backend API

Ensure your backend API services are updated:

**Update `restaurant-front-2/src/services/api/orders.ts`:**

```typescript
import { api } from './client'
import type { Order, CreateOrderPayload } from '@/types/models'

export const ordersApi = {
  async getOrders(): Promise<Order[]> {
    const response = await api.get('/orders/')
    return response.data
  },

  async getOrder(id: number): Promise<Order> {
    const response = await api.get(`/order/${id}/`)
    return response.data
  },

  async getOrdersByTable(tableId: number): Promise<Order[]> {
    const response = await api.get(`/order/?table=${tableId}`)
    return response.data
  },

  async createOrder(data: CreateOrderPayload): Promise<Order> {
    const payload = {
      ...data,
      model: 'order',
      operation: 'CREATE'
    }
    const response = await api.post('/order/register/', payload)
    return response.data
  },

  async updateOrder(id: number, data: Partial<Order>): Promise<Order> {
    const payload = {
      ...data,
      model: 'order',
      operation: 'UPDATE',
      object_id: String(id)
    }
    const response = await api.put(`/order/${id}/update/`, payload)
    return response.data
  },

  async updateOrderItems(id: number, items: Order['items']): Promise<Order> {
    const response = await api.patch(`/order/${id}/update/`, { items })
    return response.data
  },

  async transferItems(data: {
    source_order_id: number
    target_order_id: number
  }): Promise<Order> {
    const response = await api.post('/order/transfer/', data)
    return response.data
  },

  async deleteOrder(id: number): Promise<void> {
    await api.delete(`/order/${id}/delete/`)
  }
}
```

### Step 2: Create Orders Pinia Store (Optional but Recommended)

**Create `restaurant-front-2/src/stores/orders.ts`:**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ordersApi } from '@/services/api'
import type { Order } from '@/types/models'

export const useOrdersStore = defineStore('orders', () => {
  const orders = ref<Order[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchOrders(force = false) {
    if (!force && orders.value.length > 0) return

    isLoading.value = true
    error.value = null

    try {
      orders.value = await ordersApi.getOrders()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchOrdersByTable(tableId: number) {
    isLoading.value = true
    error.value = null

    try {
      const tableOrders = await ordersApi.getOrdersByTable(tableId)
      return tableOrders
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createOrder(data: any) {
    isLoading.value = true
    error.value = null

    try {
      const newOrder = await ordersApi.createOrder(data)
      orders.value.push(newOrder)
      return newOrder
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateOrder(id: number, data: any) {
    isLoading.value = true
    error.value = null

    try {
      const updated = await ordersApi.updateOrderItems(id, data)
      const index = orders.value.findIndex(o => o.orderID === id)
      if (index !== -1) {
        orders.value[index] = updated
      }
      return updated
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteOrder(id: number) {
    isLoading.value = true
    error.value = null

    try {
      await ordersApi.deleteOrder(id)
      orders.value = orders.value.filter(o => o.orderID !== id)
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    orders,
    isLoading,
    error,
    fetchOrders,
    fetchOrdersByTable,
    createOrder,
    updateOrder,
    deleteOrder
  }
})
```

### Step 3: Generate Components with v0

#### 3a. Generate Tables Overview

1. Go to **https://v0.dev**
2. Copy the entire contents of `v0-prompt-tables-overview.md`
3. Paste into v0's chat interface
4. Click "Generate"
5. Review the generated code
6. Click "Copy Code" or iterate with v0 if needed

**Tips:**
- If v0 generates something you don't like, ask it to refine: "Make the cards larger" or "Use a different color scheme"
- You can ask v0 to "make it more mobile-friendly" or "add better animations"
- Export the code and save to `restaurant-front-2/src/views/MesasView.vue`

#### 3b. Generate Table Order Details

1. Stay in v0.dev (or start a new chat)
2. Copy the entire contents of `v0-prompt-table-order-details.md`
3. Paste into v0's chat interface
4. Click "Generate"
5. Review the generated code
6. Export to `restaurant-front-2/src/views/MesasPedidosView.vue`

**Important:** This is a complex component. v0 might generate it in multiple parts. If so:
- Ask v0 to generate the template first
- Then ask for the script section
- Or ask v0 to "generate the complete component with all features"

### Step 4: Review and Adjust Generated Code

After getting code from v0, you'll need to:

1. **Check Imports:** Ensure all components are imported correctly
   ```typescript
   import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
   import { Badge } from '@/components/ui/badge'
   // etc.
   ```

2. **Verify Store Integration:**
   ```typescript
   import { useTablesStore } from '@/stores/tables'
   import { useOrdersStore } from '@/stores/orders'
   import { useMenuStore } from '@/stores/menu'
   ```

3. **Check API Imports:**
   ```typescript
   import { ordersApi } from '@/services/api'
   import { tablesApi } from '@/services/api'
   import { menuApi } from '@/services/api'
   ```

4. **Verify Type Imports:**
   ```typescript
   import type { Table, Order, OrderItem, MenuItem } from '@/types/models'
   ```

### Step 5: Test Functionality

#### Test MesasView:
1. Navigate to `/mesas`
2. Verify tables display correctly
3. Test filtering by status
4. Test search functionality
5. Click a table → should navigate to order details
6. Check auto-refresh (tables should update every 30s)

#### Test MesasPedidosView:
1. Navigate to `/mesas/pedidos?table=1`
2. If no order exists, add items from menu to create one
3. Test adding items to order
4. Test incrementing/decrementing quantities
5. Test deleting items
6. Test transfer dialog (if multiple tables available)
7. Test delete order confirmation

### Step 6: Add Missing Icons (if needed)

v0 might use icons not imported. Add them from lucide-vue-next:

```typescript
import {
  Users,
  Search,
  Plus,
  Minus,
  Trash2,
  ArrowRightLeft,
  CreditCard,
  ChefHat,
  Wine,
  Store,
  ShoppingCart,
  ShoppingBag
} from 'lucide-vue-next'
```

### Step 7: Style Adjustments (Optional)

If you need to adjust styles:

```vue
<style scoped>
/* Add custom styles here */
.table-card-occupied {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}
</style>
```

---

## 🔧 Troubleshooting

### Issue: "Cannot find module '@/components/ui/...'"
**Solution:** Ensure shadcn/vue components are installed:
```bash
cd restaurant-front-2
npx shadcn-vue@latest add card badge button input select dialog
```

### Issue: "API calls returning 404"
**Solution:** Check your API base URL in `restaurant-front-2/src/services/api/client.ts`

### Issue: "Order not updating after adding items"
**Solution:** Ensure you're calling `await` on async functions and refreshing the order data after mutations

### Issue: "Table status not changing to Occupied"
**Solution:** Backend automatically updates table status when order is created. If not working, check backend serializer.

### Issue: "Transfer not working"
**Solution:** Transfer API expects `source_order_id` and `target_order_id`. Ensure both exist.

---

## 🎨 Customization Ideas

### Add WebSocket Real-time Updates
Your backend has WebSocket support. You can add:

```typescript
import { onMounted, onUnmounted } from 'vue'

let ws: WebSocket | null = null

onMounted(() => {
  ws = new WebSocket('ws://localhost:8000/ws/orders/')

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    // Update order in real-time
    if (data.type === 'order_update') {
      // Refresh order data
      fetchData()
    }
  }
})

onUnmounted(() => {
  ws?.close()
})
```

### Add Toast Notifications
Using your existing toast pattern:

```typescript
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

function showToast(message: string, variant: 'success' | 'error') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

// Use it:
try {
  await ordersApi.deleteOrder(orderId)
  showToast('Pedido cancelado com sucesso', 'success')
} catch (error) {
  showToast('Erro ao cancelar pedido', 'error')
}
```

### Add Sound Notifications
For kitchen/bar notifications:

```typescript
function playNotificationSound() {
  const audio = new Audio('/sounds/notification.mp3')
  audio.play()
}

// When order status changes to "PREPARING"
if (newStatus === 'PREPARING') {
  playNotificationSound()
}
```

---

## 📊 Backend API Reference

### Tables API
- `GET /api/tables/` - List all tables
- `GET /api/tables/{id}/` - Get table details
- `POST /api/tables/register/` - Create table
- `PUT /api/tables/{id}/update/` - Update table
- `DELETE /api/tables/{id}/delete/` - Delete table

### Orders API
- `GET /api/orders/` - List all orders
- `GET /api/order/{id}/` - Get order by ID
- `GET /api/order/?table={tableId}` - Get orders by table (excludes PAID)
- `POST /api/order/register/` - Create order
- `PUT /api/order/{id}/update/` - Full update
- `PATCH /api/order/{id}/update/` - Partial update (items)
- `POST /api/order/transfer/` - Transfer items between orders
- `DELETE /api/order/{id}/delete/` - Delete order

### Menu API
- `GET /api/menu_item/` - List all menu items
- `GET /api/menu_category/` - List categories

---

## 🎯 Next Steps After Implementation

Once both views are working:

1. **Add Payment Processing** - Integrate with payments view
2. **Kitchen Display** - Create separate view for kitchen staff
3. **Bar Display** - Create separate view for bar staff
4. **Print Receipts** - Add receipt printing functionality
5. **QR Codes** - Generate QR codes for table ordering
6. **Analytics** - Add dashboard with order statistics
7. **Table Map** - Visual drag-and-drop table layout editor

---

## 🐛 Testing Checklist

### MesasView:
- [ ] Tables load and display correctly
- [ ] Status badges show correct colors
- [ ] Order info displays for occupied tables
- [ ] Filters work (Todas, Disponíveis, Ocupadas, Reservadas)
- [ ] Search filters by table number
- [ ] Sort works correctly
- [ ] Clicking table navigates to order details
- [ ] Auto-refresh works (30s interval)
- [ ] Loading state shows skeletons
- [ ] Empty state displays when no tables match

### MesasPedidosView:
- [ ] Table info loads correctly
- [ ] Order summary calculates totals properly (Subtotal, IVA 15%, Total)
- [ ] Order items display with correct status
- [ ] Can increment/decrement item quantities
- [ ] Can delete items from order
- [ ] Menu items load and filter by category
- [ ] Search menu items works
- [ ] Can add items to cart
- [ ] Can add cart to order (creates or updates)
- [ ] Transfer dialog lists available tables
- [ ] Transfer items works
- [ ] Delete order confirmation works
- [ ] Deleting order redirects to /mesas
- [ ] Breadcrumb navigation works
- [ ] Auto-refresh updates order status

---

## 📞 Support

If you encounter issues:

1. Check browser console for errors
2. Check network tab for failed API calls
3. Verify backend is running and accessible
4. Ensure all dependencies are installed
5. Check that all TypeScript types are correctly defined

## 🎉 You're Ready!

You now have everything you need to build the tables and orders management system. Good luck with the implementation!

---

**Created for Restaurant Management System**
**Stack:** Vue 3 + TypeScript + Pinia + shadcn/vue + Tailwind CSS
**Backend:** Django REST Framework + PostgreSQL
