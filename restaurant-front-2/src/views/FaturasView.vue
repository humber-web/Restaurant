<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { paymentsApi, type ListInvoicesParams } from '@/services/api/payments'
import type { Payment } from '@/types/models/payment'
import InvoicesTableAdvanced from '@/components/invoices/InvoicesTableAdvanced.vue'
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  FileText,
  Download,
  Search,
  Filter,
} from 'lucide-vue-next'

// Toast notifications
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

function showToast(message: string, variant: 'success' | 'error' = 'success') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

// State
const invoices = ref<Payment[]>([])
const isLoading = ref(false)
const totalCount = ref(0)

// Filters
const searchQuery = ref('')
const invoiceTypeFilter = ref<string>('ALL')
const startDate = ref('')
const endDate = ref('')

// Detail dialog
const showDetailDialog = ref(false)
const selectedInvoice = ref<Payment | null>(null)

// Load invoices
async function loadInvoices() {
  try {
    isLoading.value = true

    const params: ListInvoicesParams = {
      page_size: 100, // Load a large batch for client-side pagination
    }

    if (searchQuery.value) params.search = searchQuery.value
    if (invoiceTypeFilter.value && invoiceTypeFilter.value !== 'ALL') params.invoice_type = invoiceTypeFilter.value as any
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value

    const response = await paymentsApi.getInvoices(params)

    invoices.value = response.results
    totalCount.value = response.count
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao carregar faturas', 'error')
  } finally {
    isLoading.value = false
  }
}

// Filters actions
function applyFilters() {
  loadInvoices()
}

function clearFilters() {
  searchQuery.value = ''
  invoiceTypeFilter.value = 'ALL'
  startDate.value = ''
  endDate.value = ''
  loadInvoices()
}

// Actions
function viewDetails(invoice: Payment) {
  selectedInvoice.value = invoice
  showDetailDialog.value = true
}

async function downloadXML(invoice: Payment) {
  if (!invoice.paymentID) return

  try {
    const blob = await paymentsApi.downloadEFaturaXML(invoice.paymentID)

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const invoiceNo = invoice.invoice_no || 'fatura'
    link.download = `efatura_${invoiceNo.replace(/\//g, '_')}.xml`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    showToast('XML descarregado com sucesso!', 'success')
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao descarregar XML', 'error')
  }
}

// Helpers
function getInvoiceTypeBadge(type?: string) {
  switch (type) {
    case 'FT': return { class: 'bg-blue-100 text-blue-800', label: 'Fatura' }
    case 'FR': return { class: 'bg-green-100 text-green-800', label: 'Fatura Recibo' }
    case 'NC': return { class: 'bg-red-100 text-red-800', label: 'Nota Crédito' }
    case 'TV': return { class: 'bg-purple-100 text-purple-800', label: 'Talão Venda' }
    default: return { class: 'bg-gray-100 text-gray-800', label: type || 'N/A' }
  }
}

function formatDate(dateStr?: string) {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('pt-PT')
}

function formatCurrency(value?: number | string) {
  if (!value) return 'CVE 0.00'
  return `CVE ${Number(value).toFixed(2)}`
}

onMounted(() => {
  loadInvoices()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      class="fixed top-4 right-4 z-50 rounded-lg border px-4 py-3 shadow-lg transition-all"
      :class="toastVariant === 'success' ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'"
    >
      {{ toastMessage }}
    </div>

    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold">Gestão de Faturas</h1>
      <p class="text-sm text-muted-foreground">
        Visualize, pesquise e exporte todas as faturas eletrónicas (e-Fatura CV)
      </p>
    </div>

    <!-- Filters -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Filter class="h-5 w-5" />
          Filtros
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="space-y-2">
            <Label for="search">Pesquisar</Label>
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                id="search"
                v-model="searchQuery"
                placeholder="Nº fatura, NIF, nome..."
                class="pl-9"
                @keyup.enter="applyFilters"
              />
            </div>
          </div>

          <div class="space-y-2">
            <Label for="invoice-type">Tipo de Documento</Label>
            <Select v-model="invoiceTypeFilter">
              <SelectTrigger>
                <SelectValue placeholder="Todos os tipos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                <SelectItem value="FT">Fatura (FT)</SelectItem>
                <SelectItem value="FR">Fatura Recibo (FR)</SelectItem>
                <SelectItem value="NC">Nota de Crédito (NC)</SelectItem>
                <SelectItem value="TV">Talão de Venda (TV)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label for="start-date">Data Início</Label>
            <Input
              id="start-date"
              v-model="startDate"
              type="date"
            />
          </div>

          <div class="space-y-2">
            <Label for="end-date">Data Fim</Label>
            <Input
              id="end-date"
              v-model="endDate"
              type="date"
            />
          </div>
        </div>

        <div class="flex gap-2 mt-4">
          <Button @click="applyFilters" :disabled="isLoading">
            <Search class="mr-2 h-4 w-4" />
            Aplicar Filtros
          </Button>
          <Button variant="outline" @click="clearFilters" :disabled="isLoading">
            Limpar
          </Button>
        </div>
      </CardContent>
    </Card>

    <!-- Table -->
    <Card class="flex-1 flex flex-col overflow-hidden">
      <CardHeader class="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Faturas Eletrónicas</CardTitle>
          <CardDescription>
            {{ totalCount }} fatura{{ totalCount !== 1 ? 's' : '' }} encontrada{{ totalCount !== 1 ? 's' : '' }}
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent class="flex-1 overflow-auto">
        <div v-if="isLoading" class="flex items-center justify-center h-full">
          <p class="text-muted-foreground">A carregar faturas...</p>
        </div>

        <div v-else-if="invoices.length === 0" class="flex items-center justify-center h-full">
          <div class="text-center">
            <FileText class="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p class="text-muted-foreground">Nenhuma fatura encontrada</p>
          </div>
        </div>

        <InvoicesTableAdvanced
          v-else
          :invoices="invoices"
          @view-details="viewDetails"
          @download-xml="downloadXML"
        />
      </CardContent>
    </Card>

    <!-- Detail Dialog -->
    <Dialog v-model:open="showDetailDialog">
      <DialogContent class="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Detalhes da Fatura</DialogTitle>
          <DialogDescription>
            Informação completa da fatura eletrónica
          </DialogDescription>
        </DialogHeader>

        <div v-if="selectedInvoice" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <Label class="text-muted-foreground">Número</Label>
              <p class="font-semibold">{{ selectedInvoice.invoice_no }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">Data</Label>
              <p>{{ formatDate(selectedInvoice.invoice_date) }}</p>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">Tipo</Label>
              <Badge :class="getInvoiceTypeBadge(selectedInvoice.invoice_type).class">
                {{ getInvoiceTypeBadge(selectedInvoice.invoice_type).label }}
              </Badge>
            </div>
            <div class="space-y-1">
              <Label class="text-muted-foreground">Total</Label>
              <p class="font-semibold text-lg">{{ formatCurrency(selectedInvoice.amount) }}</p>
            </div>
          </div>

          <div class="border-t pt-4 space-y-2">
            <h3 class="font-semibold">Cliente</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1">
                <Label class="text-muted-foreground">Nome</Label>
                <p>{{ selectedInvoice.customer_name || 'Consumidor Final' }}</p>
              </div>
              <div class="space-y-1">
                <Label class="text-muted-foreground">NIF</Label>
                <p>{{ selectedInvoice.customer_tax_id || '999999999' }}</p>
              </div>
            </div>
          </div>

          <div class="border-t pt-4 space-y-2">
            <h3 class="font-semibold">Informação Fiscal</h3>
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">IUD:</span>
                <span class="font-mono text-xs break-all">{{ selectedInvoice.iud }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Hash:</span>
                <span class="font-mono text-xs break-all">{{ selectedInvoice.invoice_hash?.slice(0, 32) }}...</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Hash Anterior:</span>
                <span class="font-mono text-xs break-all">
                  {{ selectedInvoice.previous_invoice_hash ? selectedInvoice.previous_invoice_hash.slice(0, 32) + '...' : '(primeira fatura)' }}
                </span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Algoritmo:</span>
                <span>{{ selectedInvoice.hash_algorithm || 'SHA256' }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Certificado Software:</span>
                <span>{{ selectedInvoice.software_certificate_number || '0' }}</span>
              </div>
            </div>
          </div>

          <div class="flex gap-2 pt-4">
            <Button class="flex-1" @click="downloadXML(selectedInvoice)">
              <Download class="mr-2 h-4 w-4" />
              Descarregar XML
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>
