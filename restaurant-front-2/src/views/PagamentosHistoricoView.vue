<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { RouterLink } from 'vue-router'
import { paymentsApi } from '@/services/api/payments'
import type { Payment } from '@/types/models'
import type { ColumnDef } from '@tanstack/vue-table'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  CreditCard,
  Wallet,
  Globe,
  ArrowUpDown,
  RefreshCw,
  Filter,
} from 'lucide-vue-next'

// State
const payments = ref<Payment[]>([])
const isLoading = ref(true)
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

// Column definitions
const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: 'paymentID',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => [
        'ID',
        h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })
      ])
    },
    cell: ({ row }) => h('div', { class: 'font-medium' }, `#${row.getValue('paymentID')}`),
    meta: { label: 'ID' },
  },
  {
    accessorKey: 'order',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => [
        'Pedido',
        h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })
      ])
    },
    cell: ({ row }) => {
      const orderId = row.getValue('order') as number
      return h(RouterLink, {
        to: `/pedidos?order=${orderId}`,
        class: 'text-primary hover:underline'
      }, () => `Pedido #${orderId}`)
    },
    meta: { label: 'Pedido' },
  },
  {
    accessorKey: 'created_at',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => [
        'Data/Hora',
        h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })
      ])
    },
    cell: ({ row }) => formatDateTime(row.getValue('created_at')),
    meta: { label: 'Data/Hora' },
  },
  {
    accessorKey: 'payment_method',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => [
        'Método',
        h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })
      ])
    },
    cell: ({ row }) => {
      const method = row.getValue('payment_method') as string
      const Icon = getPaymentMethodIcon(method)
      return h('div', { class: 'flex items-center gap-2' }, [
        h(Icon, { class: 'h-4 w-4' }),
        h('span', getPaymentMethodLabel(method))
      ])
    },
    meta: { label: 'Método' },
  },
  {
    accessorKey: 'amount',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => [
        'Valor',
        h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })
      ])
    },
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue('amount'))
      return h('div', { class: 'font-semibold' }, `€${amount.toFixed(2)}`)
    },
    meta: { label: 'Valor' },
  },
  {
    accessorKey: 'payment_status',
    header: ({ column }) => {
      return h(Button, {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      }, () => [
        'Estado',
        h(ArrowUpDown, { class: 'ml-2 h-4 w-4' })
      ])
    },
    cell: ({ row }) => {
      const status = row.getValue('payment_status') as string
      return h(Badge, { variant: getStatusVariant(status) }, () => getStatusLabel(status))
    },
    meta: { label: 'Estado' },
  },
]

// Computed: Filtered payments
const filteredPayments = computed(() => {
  let result = payments.value

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

  return result
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
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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

    <!-- Advanced Data Table -->
    <Card class="flex-1 flex flex-col">
      <CardHeader>
        <CardTitle class="text-lg">Pagamentos</CardTitle>
      </CardHeader>
      <CardContent class="flex-1">
        <DataTableAdvanced
          v-if="!isLoading"
          :data="filteredPayments"
          :columns="columns"
          search-key="paymentID"
          search-placeholder="Pesquisar por ID de Pagamento..."
        />
        <div v-else class="flex items-center justify-center py-8">
          <p class="text-muted-foreground">A carregar pagamentos...</p>
        </div>
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
