<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus, Package, TrendingUp, Clock, CheckCircle } from 'lucide-vue-next'
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
import type { PurchaseOrder } from '@/types/models'
import { purchasesApi } from '@/services/api'

const purchaseOrders = ref<PurchaseOrder[]>([])
const isLoading = ref(false)
const statusFilter = ref<string>('ALL')
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

// Status badge styling
const statusColors = {
  DRAFT: 'bg-gray-100 text-gray-800 border-gray-300',
  SUBMITTED: 'bg-blue-100 text-blue-800 border-blue-300',
  PARTIALLY_RECEIVED: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  RECEIVED: 'bg-green-100 text-green-800 border-green-300',
  INVOICED: 'bg-purple-100 text-purple-800 border-purple-300',
  PAID: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  CANCELLED: 'bg-red-100 text-red-800 border-red-300',
}

const statusLabels = {
  DRAFT: 'Rascunho',
  SUBMITTED: 'Enviado',
  PARTIALLY_RECEIVED: 'Parcialmente Recebido',
  RECEIVED: 'Recebido',
  INVOICED: 'Faturado',
  PAID: 'Pago',
  CANCELLED: 'Cancelado',
}

onMounted(async () => {
  await fetchPurchaseOrders()
})

async function fetchPurchaseOrders() {
  isLoading.value = true
  try {
    const params: any = {}
    if (statusFilter.value !== 'ALL') {
      params.status = statusFilter.value
    }
    purchaseOrders.value = await purchasesApi.getPurchaseOrders(params)
  } catch (error) {
    showToast('Erro ao carregar ordens de compra', 'error')
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

// Statistics
const stats = computed(() => {
  const total = purchaseOrders.value.length
  const draft = purchaseOrders.value.filter(po => po.status === 'DRAFT').length
  const pending = purchaseOrders.value.filter(po =>
    ['SUBMITTED', 'PARTIALLY_RECEIVED'].includes(po.status)
  ).length
  const received = purchaseOrders.value.filter(po =>
    ['RECEIVED', 'INVOICED', 'PAID'].includes(po.status)
  ).length
  const totalAmount = purchaseOrders.value
    .filter(po => po.status !== 'CANCELLED')
    .reduce((sum, po) => sum + parseFloat(po.total_amount), 0)

  return { total, draft, pending, received, totalAmount }
})

async function handleStatusFilterChange(value: string) {
  statusFilter.value = value
  await fetchPurchaseOrders()
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
        <h1 class="text-3xl font-bold tracking-tight">Ordens de Compra</h1>
        <p class="text-muted-foreground mt-1">Gerir compras a fornecedores</p>
      </div>
      <Button size="default">
        <Plus class="mr-2 h-4 w-4" />
        Nova Ordem de Compra
      </Button>
    </div>

    <!-- Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total de Ordens</CardTitle>
          <Package class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stats.total }}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Rascunhos</CardTitle>
          <Clock class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stats.draft }}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Pendentes</CardTitle>
          <TrendingUp class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ stats.pending }}</div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Valor Total</CardTitle>
          <CheckCircle class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ formatCurrency(stats.totalAmount.toString()) }}</div>
        </CardContent>
      </Card>
    </div>

    <!-- Filters -->
    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <CardTitle>Filtros</CardTitle>
        </div>
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
                <SelectItem value="DRAFT">Rascunho</SelectItem>
                <SelectItem value="SUBMITTED">Enviado</SelectItem>
                <SelectItem value="PARTIALLY_RECEIVED">Parcialmente Recebido</SelectItem>
                <SelectItem value="RECEIVED">Recebido</SelectItem>
                <SelectItem value="INVOICED">Faturado</SelectItem>
                <SelectItem value="PAID">Pago</SelectItem>
                <SelectItem value="CANCELLED">Cancelado</SelectItem>
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
        <p class="text-muted-foreground">A carregar ordens de compra...</p>
      </div>
    </div>

    <!-- Purchase Orders Table -->
    <Card v-else>
      <CardHeader>
        <CardTitle>Ordens de Compra</CardTitle>
        <CardDescription>
          {{ purchaseOrders.length }} ordem(ns) encontrada(s)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nº Ordem</TableHead>
              <TableHead>Fornecedor</TableHead>
              <TableHead>Data</TableHead>
              <TableHead>Entrega Prevista</TableHead>
              <TableHead>Estado</TableHead>
              <TableHead class="text-right">Valor Total</TableHead>
              <TableHead>Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-if="purchaseOrders.length === 0">
              <TableCell colspan="7" class="text-center text-muted-foreground py-8">
                Nenhuma ordem de compra encontrada
              </TableCell>
            </TableRow>
            <TableRow v-for="po in purchaseOrders" :key="po.purchaseOrderID">
              <TableCell class="font-medium">{{ po.po_number }}</TableCell>
              <TableCell>{{ po.supplier_name || `Fornecedor #${po.supplier}` }}</TableCell>
              <TableCell>{{ formatDate(po.order_date) }}</TableCell>
              <TableCell>
                {{ po.expected_delivery_date ? formatDate(po.expected_delivery_date) : '-' }}
              </TableCell>
              <TableCell>
                <Badge :class="statusColors[po.status]" variant="outline">
                  {{ statusLabels[po.status] }}
                </Badge>
              </TableCell>
              <TableCell class="text-right font-medium">
                {{ formatCurrency(po.total_amount) }}
              </TableCell>
              <TableCell>
                <Button variant="ghost" size="sm">Ver Detalhes</Button>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  </div>
</template>
