<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Order } from '@/types/models/order'
import { useRouter } from 'vue-router'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Eye,
  CreditCard,
  Clock,
  Users,
  ShoppingBag,
  AlertCircle,
} from 'lucide-vue-next'

interface Props {
  order: Order
}

const props = defineProps<Props>()
const router = useRouter()

// Get time urgency class
const timeUrgencyClass = computed(() => {
  const date = new Date(props.order.created_at)
  const now = new Date()
  const diffMins = Math.floor((now.getTime() - date.getTime()) / 60000)

  if (diffMins > 30) return 'border-l-4 border-l-red-500 bg-red-50'
  if (diffMins > 15) return 'border-l-4 border-l-orange-500 bg-orange-50'
  return ''
})

// Time ago string
const timeAgo = computed(() => {
  const date = new Date(props.order.created_at)
  const now = new Date()
  const diffMins = Math.floor((now.getTime() - date.getTime()) / 60000)

  if (diffMins < 1) return 'agora'
  if (diffMins < 60) return `há ${diffMins}min`
  const diffHours = Math.floor(diffMins / 60)
  return `há ${diffHours}h`
})

// Payment status variant
const paymentStatusVariant = computed((): 'default' | 'secondary' | 'outline' | 'destructive' => {
  switch (props.order.paymentStatus) {
    case 'PAID': return 'default'
    case 'PARTIALLY_PAID': return 'outline'
    case 'PENDING': return 'secondary'
    case 'FAILED': return 'destructive'
    default: return 'secondary'
  }
})

const paymentStatusLabel = computed(() => {
  switch (props.order.paymentStatus) {
    case 'PAID': return 'Pago'
    case 'PARTIALLY_PAID': return 'Parcial'
    case 'PENDING': return 'Pendente'
    case 'FAILED': return 'Falhado'
    default: return props.order.paymentStatus
  }
})

// Item count
const itemCount = computed(() => {
  return props.order.items.reduce((sum, item) => sum + item.quantity, 0)
})

// Has pending items
const hasPendingItems = computed(() => {
  return props.order.items.some(item => item.status === '1')
})

// Navigate to details
function viewDetails() {
  router.push(`/pedidos/${props.order.orderID}`)
}

// Navigate to payment
function processPayment() {
  router.push(`/pagamentos/processar?order=${props.order.orderID}`)
}
</script>

<template>
  <Card :class="['hover:shadow-lg transition-shadow cursor-pointer', timeUrgencyClass]">
    <CardHeader class="pb-3">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <CardTitle class="text-lg flex items-center gap-2">
            <span>#{{ order.orderID }}</span>
            <AlertCircle v-if="hasPendingItems" class="h-4 w-4 text-orange-500" title="Items pendentes" />
          </CardTitle>
          <div class="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
            <Clock class="h-3 w-3" />
            <span :class="{ 'text-red-600 font-semibold': timeAgo.includes('há') && timeAgo.includes('h') }">
              {{ timeAgo }}
            </span>
          </div>
        </div>
        <Badge :variant="paymentStatusVariant" class="text-xs">
          {{ paymentStatusLabel }}
        </Badge>
      </div>
    </CardHeader>
    <CardContent class="space-y-3">
      <!-- Order Info -->
      <div class="space-y-2">
        <div class="flex items-center gap-2 text-sm">
          <Users class="h-4 w-4 text-muted-foreground" />
          <span class="font-medium">
            {{ order.orderType === 'ONLINE' ? 'Online' : `Mesa ${order.details?.table || '—'}` }}
          </span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <ShoppingBag class="h-4 w-4 text-muted-foreground" />
          <span>{{ itemCount }} {{ itemCount === 1 ? 'item' : 'items' }}</span>
        </div>
        <div class="text-lg font-bold">
          {{ Number(order.grandTotal).toFixed(2) }} CVE
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="flex gap-2 pt-2">
        <Button
          variant="outline"
          size="sm"
          class="flex-1"
          @click.stop="viewDetails"
        >
          <Eye class="mr-1 h-3 w-3" />
          Ver
        </Button>
        <Button
          v-if="order.paymentStatus !== 'PAID'"
          variant="default"
          size="sm"
          class="flex-1"
          @click.stop="processPayment"
        >
          <CreditCard class="mr-1 h-3 w-3" />
          Pagar
        </Button>
      </div>
    </CardContent>
  </Card>
</template>
