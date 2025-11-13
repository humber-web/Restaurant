<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { paymentsApi } from '@/services/api/payments'
import { ordersApi } from '@/services/api'
import type { Payment } from '@/types/models'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import {
  CreditCard,
  Wallet,
  Globe,
  Search,
  Filter,
  Calendar,
  RefreshCw,
} from 'lucide-vue-next'

// State
const payments = ref<Payment[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const filterMethod = ref<string>('ALL')
const filterStatus = ref<string>('ALL')
const filterDateFrom = ref('')
const filterDateTo = ref('')

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

// Computed: Filtered payments
const filteredPayments = computed(() => {
  let result = payments.value

  // Filter by search query (order ID)
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(payment =>
      payment.order.toString().includes(query) ||
      payment.paymentID.toString().includes(query)
    )
  }

  // Filter by payment method
  if (filterMethod.value !== 'ALL') {
    result = result.filter(payment => payment.payment_method === filterMethod.value)
  }

  // Filter by status
  if (filterStatus.value !== 'ALL') {
    result = result.filter(payment => payment.payment_status === filterStatus.value)
  }

  // Filter by date range
  if (filterDateFrom.value) {
    const fromDate = new Date(filterDateFrom.value)
    result = result.filter(payment => new Date(payment.created_at) >= fromDate)
  }

  if (filterDateTo.value) {
    const toDate = new Date(filterDateTo.value)
    toDate.setHours(23, 59, 59, 999) // End of day
    result = result.filter(payment => new Date(payment.created_at) <= toDate)
  }

  // Sort by most recent first
  return result.sort((a, b) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
})

// Computed: Statistics
const statistics = computed(() => {
  const total = filteredPayments.value.length
  const completed = filteredPayments.value.filter(p => p.payment_status === 'COMPLETED').length
  const totalAmount = filteredPayments.value
    .filter(p => p.payment_status === 'COMPLETED')
    .reduce((sum, p) => sum + Number(p.amount), 0)

  const byMethod = {
    CASH: filteredPayments.value.filter(p => p.payment_method === 'CASH' && p.payment_status === 'COMPLETED').reduce((sum, p) => sum + Number(p.amount), 0),
    CARD: filteredPayments.value.filter(p => ['CREDIT_CARD', 'DEBIT_CARD'].includes(p.payment_method) && p.payment_status === 'COMPLETED').reduce((sum, p) => sum + Number(p.amount), 0),
    ONLINE: filteredPayments.value.filter(p => p.payment_method === 'ONLINE' && p.payment_status === 'COMPLETED').reduce((sum, p) => sum + Number(p.amount), 0),
  }

  return {
    total,
    completed,
    totalAmount,
    byMethod
  }
})

// Fetch payments
async function fetchPayments() {
  isLoading.value = true
  try {
    payments.value = await paymentsApi.getPayments()
  } catch (error: any) {
    showToast(error.message || 'Erro ao carregar pagamentos', 'error')
  } finally {
    isLoading.value = false
  }
}

// Clear filters
function clearFilters() {
  searchQuery.value = ''
  filterMethod.value = 'ALL'
  filterStatus.value = 'ALL'
  filterDateFrom.value = ''
  filterDateTo.value = ''
}

// Get payment method icon
function getPaymentMethodIcon(method: string) {
  switch (method) {
    case 'CASH':
      return Wallet
    case 'CREDIT_CARD':
    case 'DEBIT_CARD':
      return CreditCard
    case 'ONLINE':
      return Globe
    default:
      return CreditCard
  }
}

// Get payment method label
function getPaymentMethodLabel(method: string) {
  switch (method) {
    case 'CASH':
      return 'Dinheiro'
    case 'CREDIT_CARD':
      return 'Cartão de Crédito'
    case 'DEBIT_CARD':
      return 'Cartão de Débito'
    case 'ONLINE':
      return 'Online'
    default:
      return method
  }
}

// Get status badge variant
function getStatusVariant(status: string): 'default' | 'secondary' | 'destructive' {
  switch (status) {
    case 'COMPLETED':
      return 'default'
    case 'PENDING':
      return 'secondary'
    case 'FAILED':
      return 'destructive'
    default:
      return 'secondary'
  }
}

// Get status label
function getStatusLabel(status: string) {
  switch (status) {
    case 'COMPLETED':
      return 'Concluído'
    case 'PENDING':
      return 'Pendente'
    case 'FAILED':
      return 'Falhado'
    default:
      return status
  }
}

// Format date/time
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

// Format date
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

onMounted(() => {
  fetchPayments()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold">Histórico de Pagamentos</h1>
      <Button @click="fetchPayments" variant="outline" size="sm">
        <RefreshCw class="mr-2 h-4 w-4" />
        Atualizar
      </Button>
    </div>

    <!-- Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader class="pb-2">
          <CardDescription>Total de Pagamentos</CardDescription>
          <CardTitle class="text-3xl">{{ statistics.total }}</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader class="pb-2">
          <CardDescription>Valor Total</CardDescription>
          <CardTitle class="text-3xl text-green-600">€{{ statistics.totalAmount.toFixed(2) }}</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader class="pb-2">
          <CardDescription>Dinheiro</CardDescription>
          <CardTitle class="text-2xl">€{{ statistics.byMethod.CASH.toFixed(2) }}</CardTitle>
        </CardHeader>
      </Card>
      <Card>
        <CardHeader class="pb-2">
          <CardDescription>Cartão</CardDescription>
          <CardTitle class="text-2xl">€{{ statistics.byMethod.CARD.toFixed(2) }}</CardTitle>
        </CardHeader>
      </Card>
    </div>

    <!-- Filters -->
    <Card>
      <CardHeader>
        <CardTitle class="text-lg flex items-center gap-2">
          <Filter class="h-4 w-4" />
          Filtros
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <!-- Search -->
          <div class="space-y-2">
            <Label for="search">Pesquisar</Label>
            <div class="relative">
              <Search class="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                id="search"
                v-model="searchQuery"
                placeholder="ID Pedido ou Pagamento"
                class="pl-8"
              />
            </div>
          </div>

          <!-- Payment Method Filter -->
          <div class="space-y-2">
            <Label for="filter-method">Método de Pagamento</Label>
            <Select v-model="filterMethod">
              <SelectTrigger id="filter-method">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                <SelectItem value="CASH">Dinheiro</SelectItem>
                <SelectItem value="CREDIT_CARD">Cartão de Crédito</SelectItem>
                <SelectItem value="DEBIT_CARD">Cartão de Débito</SelectItem>
                <SelectItem value="ONLINE">Online</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Status Filter -->
          <div class="space-y-2">
            <Label for="filter-status">Estado</Label>
            <Select v-model="filterStatus">
              <SelectTrigger id="filter-status">
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                <SelectItem value="COMPLETED">Concluído</SelectItem>
                <SelectItem value="PENDING">Pendente</SelectItem>
                <SelectItem value="FAILED">Falhado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Date From -->
          <div class="space-y-2">
            <Label for="filter-date-from">Data Início</Label>
            <Input
              id="filter-date-from"
              v-model="filterDateFrom"
              type="date"
            />
          </div>

          <!-- Date To -->
          <div class="space-y-2">
            <Label for="filter-date-to">Data Fim</Label>
            <Input
              id="filter-date-to"
              v-model="filterDateTo"
              type="date"
            />
          </div>
        </div>

        <div class="mt-4">
          <Button @click="clearFilters" variant="outline" size="sm">
            Limpar Filtros
          </Button>
        </div>
      </CardContent>
    </Card>

    <!-- Payments Table -->
    <Card class="flex-1 flex flex-col">
      <CardHeader>
        <CardTitle class="text-lg">
          Pagamentos ({{ filteredPayments.length }})
        </CardTitle>
      </CardHeader>
      <CardContent class="flex-1 overflow-auto">
        <!-- Loading State -->
        <div v-if="isLoading" class="space-y-2">
          <Skeleton class="h-12 w-full" />
          <Skeleton class="h-12 w-full" />
          <Skeleton class="h-12 w-full" />
        </div>

        <!-- No Data State -->
        <div v-else-if="filteredPayments.length === 0" class="text-center py-8">
          <p class="text-muted-foreground">Nenhum pagamento encontrado</p>
        </div>

        <!-- Table -->
        <Table v-else>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Pedido</TableHead>
              <TableHead>Data/Hora</TableHead>
              <TableHead>Método</TableHead>
              <TableHead>Valor</TableHead>
              <TableHead>Estado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="payment in filteredPayments" :key="payment.paymentID">
              <TableCell class="font-medium">#{{ payment.paymentID }}</TableCell>
              <TableCell>
                <router-link
                  :to="`/pedidos?order=${payment.order}`"
                  class="text-primary hover:underline"
                >
                  Pedido #{{ payment.order }}
                </router-link>
              </TableCell>
              <TableCell>{{ formatDateTime(payment.created_at) }}</TableCell>
              <TableCell>
                <div class="flex items-center gap-2">
                  <component :is="getPaymentMethodIcon(payment.payment_method)" class="h-4 w-4" />
                  <span>{{ getPaymentMethodLabel(payment.payment_method) }}</span>
                </div>
              </TableCell>
              <TableCell class="font-semibold">€{{ Number(payment.amount).toFixed(2) }}</TableCell>
              <TableCell>
                <Badge :variant="getStatusVariant(payment.payment_status)">
                  {{ getStatusLabel(payment.payment_status) }}
                </Badge>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>

    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      class="fixed bottom-4 right-4 z-50 rounded-lg border px-4 py-3 shadow-lg"
      :class="toastVariant === 'success' ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'"
    >
      {{ toastMessage }}
    </div>
  </div>
</template>
