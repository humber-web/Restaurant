<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus, FileText, AlertCircle, CheckCircle2, Clock } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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
import type { SupplierInvoice } from '@/types/models'
import { purchasesApi } from '@/services/api'

const invoices = ref<SupplierInvoice[]>([])
const isLoading = ref(false)
const statusFilter = ref<string>('ALL')
const overdueFilter = ref<boolean | undefined>(undefined)
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

// Status badge styling
const statusColors = {
  RECEIVED: 'bg-blue-100 text-blue-800 border-blue-300',
  APPROVED: 'bg-purple-100 text-purple-800 border-purple-300',
  SCHEDULED_PAYMENT: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  PAID: 'bg-green-100 text-green-800 border-green-300',
  CANCELLED: 'bg-red-100 text-red-800 border-red-300',
}

const statusLabels = {
  RECEIVED: 'Recebida',
  APPROVED: 'Aprovada',
  SCHEDULED_PAYMENT: 'Pagamento Agendado',
  PAID: 'Paga',
  CANCELLED: 'Cancelada',
}

onMounted(async () => {
  await fetchInvoices()
})

async function fetchInvoices() {
  isLoading.value = true
  try {
    const params: any = {}
    if (statusFilter.value !== 'ALL') {
      params.status = statusFilter.value
    }
    if (overdueFilter.value !== undefined) {
      params.overdue = overdueFilter.value
    }
    invoices.value = await purchasesApi.getSupplierInvoices(params)
  } catch (error) {
    showToast('Erro ao carregar faturas de fornecedor', 'error')
  } finally {
    isLoading.value = false
  }
}

function showToast(message: string, variant: 'success' | 'error') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('pt-PT')
}

function formatCurrency(amount: string) {
  return new Intl.NumberFormat('pt-PT', {
    style: 'currency',
    currency: 'CVE',
  }).format(parseFloat(amount))
}

function isOverdue(invoice: SupplierInvoice): boolean {
  if (!invoice.due_date || invoice.status === 'PAID' || invoice.status === 'CANCELLED') {
    return false
  }
  return invoice.days_until_due !== null && invoice.days_until_due < 0
}

// Statistics
const stats = computed(() => {
  const total = invoices.value.length
  const pending = invoices.value.filter(inv =>
    ['RECEIVED', 'APPROVED', 'SCHEDULED_PAYMENT'].includes(inv.status)
  ).length
  const overdue = invoices.value.filter(inv => isOverdue(inv)).length
  const paid = invoices.value.filter(inv => inv.status === 'PAID').length
  const totalAmount = invoices.value
    .filter(inv => inv.status !== 'CANCELLED')
    .reduce((sum, inv) => sum + parseFloat(inv.total_amount), 0)
  const totalPending = invoices.value
    .filter(inv => ['RECEIVED', 'APPROVED', 'SCHEDULED_PAYMENT'].includes(inv.status))
    .reduce((sum, inv) => sum + parseFloat(inv.total_amount), 0)

  return { total, pending, overdue, paid, totalAmount, totalPending }
})

async function handleStatusFilterChange(value: string) {
  statusFilter.value = value
  await fetchInvoices()
}

async function handleOverdueFilterChange(value: string) {
  if (value === 'ALL') {
    overdueFilter.value = undefined
  } else if (value === 'OVERDUE') {
    overdueFilter.value = true
  } else if (value === 'NOT_OVERDUE') {
    overdueFilter.value = false
  }
  await fetchInvoices()
}

async function markAsPaid(invoiceId: number) {
  try {
    await purchasesApi.markInvoiceAsPaid(invoiceId)
    showToast('Fatura marcada como paga com sucesso', 'success')
    await fetchInvoices()
  } catch (error) {
    showToast('Erro ao marcar fatura como paga', 'error')
  }
}
</script>

<template>
  <div class="flex flex-col gap-6 p-6">
    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      class="fixed top-4 right-4 z-50 rounded-lg border px-4 py-3 shadow-lg transition-all"
      :class="toastVariant === 'success' ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'"
    >
      {{ toastMessage }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">Faturas de Fornecedor</h1>
        <p class="text-muted-foreground mt-1">Gerir faturas recebidas de fornecedores</p>
      </div>
      <Button size="default">
        <Plus class="mr-2 h-4 w-4" />
        Nova Fatura
      </Button>
    </div>

    <!-- Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-5">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total de Faturas</CardTitle>
          <FileText class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stats.total }}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Pendentes</CardTitle>
          <Clock class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stats.pending }}</div>
          <p class="text-xs text-muted-foreground">
            {{ formatCurrency(stats.totalPending.toString()) }}
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Vencidas</CardTitle>
          <AlertCircle class="h-4 w-4 text-red-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-red-600">{{ stats.overdue }}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Pagas</CardTitle>
          <CheckCircle2 class="h-4 w-4 text-green-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stats.paid }}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Valor Total</CardTitle>
          <FileText class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ formatCurrency(stats.totalAmount.toString()) }}</div>
        </CardContent>
      </Card>
    </div>

    <!-- Filters -->
    <Card>
      <CardHeader>
        <CardTitle>Filtros</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="flex gap-4">
          <div class="flex-1">
            <label class="text-sm font-medium mb-2 block">Estado</label>
            <Select :model-value="statusFilter" @update:model-value="handleStatusFilterChange">
              <SelectTrigger>
                <SelectValue placeholder="Todos os estados" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos os estados</SelectItem>
                <SelectItem value="RECEIVED">Recebida</SelectItem>
                <SelectItem value="APPROVED">Aprovada</SelectItem>
                <SelectItem value="SCHEDULED_PAYMENT">Pagamento Agendado</SelectItem>
                <SelectItem value="PAID">Paga</SelectItem>
                <SelectItem value="CANCELLED">Cancelada</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="flex-1">
            <label class="text-sm font-medium mb-2 block">Vencimento</label>
            <Select
              :model-value="overdueFilter === true ? 'OVERDUE' : overdueFilter === false ? 'NOT_OVERDUE' : 'ALL'"
              @update:model-value="handleOverdueFilterChange"
            >
              <SelectTrigger>
                <SelectValue placeholder="Todas" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todas</SelectItem>
                <SelectItem value="OVERDUE">Apenas Vencidas</SelectItem>
                <SelectItem value="NOT_OVERDUE">Não Vencidas</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex min-h-[400px] items-center justify-center">
      <div class="text-center">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4" />
        <p class="text-muted-foreground">A carregar faturas...</p>
      </div>
    </div>

    <!-- Invoices Table -->
    <Card v-else>
      <CardHeader>
        <CardTitle>Faturas de Fornecedor</CardTitle>
        <CardDescription>
          {{ invoices.length }} fatura(s) encontrada(s)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nº Fatura</TableHead>
              <TableHead>Fornecedor</TableHead>
              <TableHead>Data Fatura</TableHead>
              <TableHead>Vencimento</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead class="text-right">Valor</TableHead>
              <TableHead class="text-right">Total</TableHead>
              <TableHead>Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-if="invoices.length === 0">
              <TableCell colspan="8" class="text-center text-muted-foreground py-8">
                Nenhuma fatura encontrada
              </TableCell>
            </TableRow>
            <TableRow
              v-for="invoice in invoices"
              :key="invoice.supplierInvoiceID"
              :class="{ 'bg-red-50': isOverdue(invoice) }"
            >
              <TableCell class="font-medium">{{ invoice.invoice_number }}</TableCell>
              <TableCell>{{ invoice.supplier_name || `Fornecedor #${invoice.supplier}` }}</TableCell>
              <TableCell>{{ formatDate(invoice.invoice_date) }}</TableCell>
              <TableCell>
                <div class="flex items-center gap-2">
                  {{ invoice.due_date ? formatDate(invoice.due_date) : '-' }}
                  <Badge v-if="isOverdue(invoice)" variant="destructive" class="text-xs">
                    Vencida
                  </Badge>
                  <span
                    v-else-if="invoice.days_until_due !== null && invoice.days_until_due >= 0 && invoice.status !== 'PAID'"
                    class="text-xs text-muted-foreground"
                  >
                    ({{ invoice.days_until_due }} dias)
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <Badge :class="statusColors[invoice.status]" variant="outline">
                  {{ statusLabels[invoice.status] }}
                </Badge>
              </TableCell>
              <TableCell class="text-right">
                {{ formatCurrency(invoice.amount) }}
              </TableCell>
              <TableCell class="text-right font-medium">
                {{ formatCurrency(invoice.total_amount) }}
              </TableCell>
              <TableCell>
                <div class="flex gap-2">
                  <Button variant="ghost" size="sm">Ver</Button>
                  <Button
                    v-if="invoice.status !== 'PAID' && invoice.status !== 'CANCELLED'"
                    variant="outline"
                    size="sm"
                    @click="markAsPaid(invoice.supplierInvoiceID)"
                  >
                    Marcar Paga
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  </div>
</template>
