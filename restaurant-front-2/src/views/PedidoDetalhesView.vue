<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ordersApi } from '@/services/api'
import { paymentsApi } from '@/services/api/payments'
import type { Order, Payment } from '@/types/models'
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
import { Skeleton } from '@/components/ui/skeleton'
import PrintReceipt from '@/components/print/PrintReceipt.vue'
import { usePrint } from '@/composables/usePrint'
import {
  ArrowLeft,
  CreditCard,
  Printer,
  ShoppingBag,
  Calendar,
  User,
  MapPin,
  DollarSign,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const { printElement } = usePrint()

// State
const orderID = computed(() => Number(route.params.id))
const order = ref<Order | null>(null)
const payments = ref<Payment[]>([])
const isLoading = ref(true)

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

// Order status helpers
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

function getOrderStatusIcon(status: string) {
  switch (status) {
    case 'PENDING': return Clock
    case 'PREPARING': return ShoppingBag
    case 'READY': return CheckCircle
    case 'DELIVERED': return CheckCircle
    case 'CANCELLED': return XCircle
    default: return AlertCircle
  }
}

function getPaymentStatusVariant(status: string): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case 'PAID': return 'default'
    case 'PARTIALLY_PAID': return 'outline'
    case 'PENDING': return 'secondary'
    case 'FAILED': return 'destructive'
    default: return 'secondary'
  }
}

function getPaymentStatusLabel(status: string): string {
  switch (status) {
    case 'PAID': return 'Pago'
    case 'PARTIALLY_PAID': return 'Parcialmente Pago'
    case 'PENDING': return 'Pendente'
    case 'FAILED': return 'Falhado'
    default: return status
  }
}

function getItemStatusLabel(status: string): string {
  switch (status) {
    case '1': return 'Pendente'
    case '2': return 'Preparando'
    case '3': return 'Pronto'
    case '4': return 'Entregue'
    default: return status
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

function getStationLabel(station: string): string {
  switch (station) {
    case '1': return 'Cozinha'
    case '2': return 'Bar'
    case '3': return 'Balcão'
    default: return 'Desconhecido'
  }
}

function getPaymentMethodLabel(method: string): string {
  switch (method) {
    case 'CASH': return 'Dinheiro'
    case 'CREDIT_CARD': return 'Cartão de Crédito'
    case 'DEBIT_CARD': return 'Cartão de Débito'
    case 'ONLINE': return 'Pagamento Online'
    default: return method
  }
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatCurrency(value: number | string): string {
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return `${numValue.toFixed(2)} CVE`
}

// Computed: Total paid
const totalPaid = computed(() => {
  return payments.value
    .filter(p => p.payment_status === 'COMPLETED')
    .reduce((sum, p) => sum + Number(p.amount), 0)
})

// Computed: Remaining amount
const remainingAmount = computed(() => {
  if (!order.value) return 0
  return Number(order.value.grandTotal) - totalPaid.value
})

// Fetch data
async function fetchData() {
  try {
    isLoading.value = true
    const [orderData, paymentsData] = await Promise.all([
      ordersApi.getOrder(orderID.value),
      paymentsApi.getPaymentsByOrder(orderID.value).catch(() => [])
    ])
    order.value = orderData
    payments.value = paymentsData
  } catch (error: any) {
    showToast(error.message || 'Erro ao carregar pedido', 'error')
    router.push('/pedidos')
  } finally {
    isLoading.value = false
  }
}

// Navigate to payment processing
function processPayment() {
  router.push(`/pagamentos/processar?order=${orderID.value}`)
}

// Print receipt
function printReceipt() {
  if (!order.value) return

  const elementId = `receipt-${order.value.orderID}`
  printElement(elementId, {
    title: `Recibo - Pedido #${order.value.orderID}`,
    onBeforePrint: () => {
      console.log('Imprimindo recibo...')
    },
    onAfterPrint: () => {
      showToast('Recibo impresso com sucesso')
    },
  })
}

// Go back
function goBack() {
  router.back()
}

// Lifecycle
onMounted(() => {
  if (!orderID.value) {
    showToast('ID do pedido não fornecido', 'error')
    router.push('/pedidos')
    return
  }
  fetchData()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
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

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" @click="goBack">
          <ArrowLeft class="h-5 w-5" />
        </Button>
        <div>
          <h1 class="text-3xl font-bold">Detalhes do Pedido #{{ orderID }}</h1>
          <p class="text-muted-foreground">Informação completa do pedido</p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button
          v-if="order && order.paymentStatus !== 'PAID'"
          @click="processPayment"
        >
          <CreditCard class="mr-2 h-4 w-4" />
          Processar Pagamento
        </Button>
        <Button
          v-if="order"
          variant="outline"
          @click="printReceipt"
        >
          <Printer class="mr-2 h-4 w-4" />
          Imprimir Recibo
        </Button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid gap-4 md:grid-cols-2">
      <Skeleton class="h-64 w-full" />
      <Skeleton class="h-64 w-full" />
    </div>

    <!-- Content -->
    <div v-else-if="order" class="grid gap-4 md:grid-cols-2">
      <!-- Left Column -->
      <div class="space-y-4">
        <!-- Order Information Card -->
        <Card>
          <CardHeader>
            <CardTitle>Informação do Pedido</CardTitle>
            <CardDescription>Detalhes gerais</CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Estado do Pedido:</span>
              <Badge :variant="getOrderStatusVariant(order.status)">
                <component :is="getOrderStatusIcon(order.status)" class="mr-1 h-3 w-3" />
                {{ getOrderStatusLabel(order.status) }}
              </Badge>
            </div>

            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Estado de Pagamento:</span>
              <Badge :variant="getPaymentStatusVariant(order.paymentStatus)">
                {{ getPaymentStatusLabel(order.paymentStatus) }}
              </Badge>
            </div>

            <Separator />

            <div class="flex items-center gap-2">
              <Calendar class="h-4 w-4 text-muted-foreground" />
              <div class="flex-1">
                <div class="text-sm font-medium">Data/Hora</div>
                <div class="text-sm text-muted-foreground">{{ formatDateTime(order.created_at) }}</div>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <MapPin class="h-4 w-4 text-muted-foreground" />
              <div class="flex-1">
                <div class="text-sm font-medium">Local</div>
                <div class="text-sm text-muted-foreground">
                  {{ order.orderType === 'ONLINE' ? 'Pedido Online' : `Mesa ${order.details?.table || '—'}` }}
                </div>
              </div>
            </div>

            <div v-if="order.customer" class="flex items-center gap-2">
              <User class="h-4 w-4 text-muted-foreground" />
              <div class="flex-1">
                <div class="text-sm font-medium">Cliente</div>
                <div class="text-sm text-muted-foreground">{{ order.customer }}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Financial Summary Card -->
        <Card>
          <CardHeader>
            <CardTitle>Resumo Financeiro</CardTitle>
            <CardDescription>Valores e totais</CardDescription>
          </CardHeader>
          <CardContent class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm">Subtotal:</span>
              <span class="font-medium">{{ formatCurrency(order.totalAmount) }}</span>
            </div>

            <div class="flex items-center justify-between">
              <span class="text-sm">IVA (15%):</span>
              <span class="font-medium">{{ formatCurrency(order.totalIva) }}</span>
            </div>

            <Separator />

            <div class="flex items-center justify-between text-lg">
              <span class="font-semibold">Total:</span>
              <span class="font-bold">{{ formatCurrency(order.grandTotal) }}</span>
            </div>

            <template v-if="payments.length > 0">
              <Separator />

              <div class="flex items-center justify-between">
                <span class="text-sm text-muted-foreground">Total Pago:</span>
                <span class="font-medium text-green-600">{{ formatCurrency(totalPaid) }}</span>
              </div>

              <div v-if="remainingAmount > 0" class="flex items-center justify-between">
                <span class="text-sm text-muted-foreground">Restante:</span>
                <span class="font-medium text-orange-600">{{ formatCurrency(remainingAmount) }}</span>
              </div>
            </template>
          </CardContent>
        </Card>
      </div>

      <!-- Right Column -->
      <div class="space-y-4">
        <!-- Order Items Card -->
        <Card>
          <CardHeader>
            <CardTitle>Items do Pedido</CardTitle>
            <CardDescription>{{ order.items.length }} {{ order.items.length === 1 ? 'item' : 'items' }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-3">
            <div
              v-for="(item, index) in order.items"
              :key="index"
              class="space-y-2 pb-3"
              :class="{ 'border-b': index < order.items.length - 1 }"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="font-medium">
                    {{ item.quantity }}x {{ item.name || `Item #${item.menu_item}` }}
                  </div>
                  <div class="flex items-center gap-2 mt-1">
                    <Badge :variant="getItemStatusVariant(item.status)" class="text-xs">
                      {{ getItemStatusLabel(item.status) }}
                    </Badge>
                    <span class="text-xs text-muted-foreground">
                      {{ getStationLabel(item.to_be_prepared_in) }}
                    </span>
                  </div>
                </div>
                <div class="text-right">
                  <div class="font-medium">{{ formatCurrency(Number(item.price) * item.quantity) }}</div>
                  <div class="text-xs text-muted-foreground">{{ formatCurrency(item.price) }}/un</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Payment History Card -->
        <Card v-if="payments.length > 0">
          <CardHeader>
            <CardTitle>Histórico de Pagamentos</CardTitle>
            <CardDescription>{{ payments.length }} {{ payments.length === 1 ? 'pagamento' : 'pagamentos' }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-3">
            <div
              v-for="(payment, index) in payments"
              :key="payment.paymentID"
              class="space-y-1 pb-3"
              :class="{ 'border-b': index < payments.length - 1 }"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <DollarSign class="h-4 w-4 text-muted-foreground" />
                  <span class="text-sm font-medium">{{ getPaymentMethodLabel(payment.payment_method) }}</span>
                </div>
                <span class="font-semibold">{{ formatCurrency(payment.amount) }}</span>
              </div>
              <div class="flex items-center justify-between text-xs text-muted-foreground ml-6">
                <span>{{ formatDateTime(payment.created_at) }}</span>
                <Badge
                  :variant="payment.payment_status === 'COMPLETED' ? 'default' : 'secondary'"
                  class="text-xs"
                >
                  {{ payment.payment_status === 'COMPLETED' ? 'Concluído' : 'Pendente' }}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card v-else>
          <CardHeader>
            <CardTitle>Histórico de Pagamentos</CardTitle>
            <CardDescription>Nenhum pagamento registado</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="flex flex-col items-center justify-center py-8 text-center">
              <CreditCard class="h-12 w-12 text-muted-foreground mb-2" />
              <p class="text-sm text-muted-foreground">
                Este pedido ainda não tem pagamentos registados.
              </p>
              <Button
                v-if="order.paymentStatus !== 'PAID'"
                @click="processPayment"
                class="mt-4"
                size="sm"
              >
                Processar Pagamento
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Hidden Print Template -->
    <PrintReceipt v-if="order" :order="order" :payments="payments" />
  </div>
</template>
