<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
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
import { suppliersApi } from '@/services/api/suppliers'
import { purchasesApi } from '@/services/api'
import type { Supplier } from '@/types/models/supplier'
import type { PurchaseOrder, CreateSupplierInvoiceRequest } from '@/types/models'

interface Props {
  open: boolean
}

interface Emits {
  (e: 'update:open', value: boolean): void
  (e: 'submit', data: CreateSupplierInvoiceRequest): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Data
const suppliers = ref<Supplier[]>([])
const purchaseOrders = ref<PurchaseOrder[]>([])
const isLoadingSuppliers = ref(false)
const isLoadingPOs = ref(false)
const isSubmitting = ref(false)

// Form fields
const invoiceNumber = ref<string>('')
const selectedSupplier = ref<number | null>(null)
const selectedPurchaseOrder = ref<number | null>(null)
const invoiceDate = ref<string>(new Date().toISOString().split('T')[0])
const dueDate = ref<string>('')
const amount = ref<number>(0)
const taxAmount = ref<number>(0)
const status = ref<'RECEIVED' | 'APPROVED' | 'SCHEDULED_PAYMENT'>('RECEIVED')
const notes = ref<string>('')

// Computed
const totalAmount = computed(() => {
  return amount.value + taxAmount.value
})

const filteredPurchaseOrders = computed(() => {
  if (!selectedSupplier.value) return []
  // Only show purchase orders that are active and can be invoiced
  // Exclude DRAFT (not finalized), INVOICED/PAID (already invoiced), and CANCELLED
  return purchaseOrders.value.filter(po =>
    po.supplier === selectedSupplier.value &&
    ['SUBMITTED', 'PARTIALLY_RECEIVED', 'RECEIVED'].includes(po.status)
  )
})

const isFormValid = computed(() => {
  return (
    invoiceNumber.value.trim() !== '' &&
    selectedSupplier.value &&
    invoiceDate.value &&
    amount.value > 0
  )
})

const statusLabels: Record<string, string> = {
  SUBMITTED: 'Enviado',
  PARTIALLY_RECEIVED: 'Parcialmente Recebido',
  RECEIVED: 'Recebido',
}

// Methods
async function loadData() {
  isLoadingSuppliers.value = true
  isLoadingPOs.value = true

  try {
    const [suppliersData, posData] = await Promise.all([
      suppliersApi.listActive(),
      purchasesApi.getPurchaseOrders()
    ])
    suppliers.value = suppliersData
    purchaseOrders.value = posData
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    isLoadingSuppliers.value = false
    isLoadingPOs.value = false
  }
}

function handleSupplierChange() {
  // Reset PO selection when supplier changes
  selectedPurchaseOrder.value = null
}

function handleAmountChange() {
  // Optionally calculate tax (e.g., 15% IVA in Cape Verde)
  // taxAmount.value = amount.value * 0.15
}

function handleClose() {
  emit('update:open', false)
}

async function handleSubmit() {
  if (!isFormValid.value) return

  isSubmitting.value = true

  try {
    const payload: CreateSupplierInvoiceRequest = {
      invoice_number: invoiceNumber.value.trim(),
      supplier: selectedSupplier.value!,
      purchase_order: selectedPurchaseOrder.value || undefined,
      invoice_date: invoiceDate.value,
      due_date: dueDate.value || undefined,
      amount: amount.value,
      tax_amount: taxAmount.value,
      total_amount: totalAmount.value,
      status: status.value,
      notes: notes.value || undefined
    }

    emit('submit', payload)
    resetForm()
    handleClose()
  } catch (error) {
    console.error('Error submitting form:', error)
  } finally {
    isSubmitting.value = false
  }
}

function resetForm() {
  invoiceNumber.value = ''
  selectedSupplier.value = null
  selectedPurchaseOrder.value = null
  invoiceDate.value = new Date().toISOString().split('T')[0]
  dueDate.value = ''
  amount.value = 0
  taxAmount.value = 0
  status.value = 'RECEIVED'
  notes.value = ''
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Nova Fatura de Fornecedor</DialogTitle>
        <DialogDescription>
          Registar uma nova fatura recebida de fornecedor
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-4">
        <!-- Invoice Number and Supplier -->
        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <Label for="invoice-number">Número da Fatura *</Label>
            <Input
              id="invoice-number"
              v-model="invoiceNumber"
              placeholder="Ex: FT2025/001"
              required
            />
          </div>

          <div class="space-y-2">
            <Label for="supplier">Fornecedor *</Label>
            <Select
              v-model="selectedSupplier"
              :disabled="isLoadingSuppliers"
              @update:model-value="handleSupplierChange"
            >
              <SelectTrigger id="supplier">
                <SelectValue placeholder="Selecionar fornecedor" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="supplier in suppliers"
                  :key="supplier.supplierID"
                  :value="supplier.supplierID"
                >
                  {{ supplier.company_name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- Purchase Order (Optional) -->
        <div class="space-y-2">
          <Label for="purchase-order">Ordem de Compra (opcional)</Label>
          <Select
            v-model="selectedPurchaseOrder"
            :disabled="!selectedSupplier || isLoadingPOs"
          >
            <SelectTrigger id="purchase-order">
              <SelectValue placeholder="Associar a uma ordem de compra" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem :value="null">Nenhuma</SelectItem>
              <SelectItem
                v-for="po in filteredPurchaseOrders"
                :key="po.purchaseOrderID"
                :value="po.purchaseOrderID"
              >
                {{ po.po_number }} - {{ po.total_amount }} CVE ({{ statusLabels[po.status] }})
              </SelectItem>
            </SelectContent>
          </Select>
          <p class="text-xs text-muted-foreground">
            Apenas ordens enviadas, parcialmente recebidas ou recebidas aparecem aqui
          </p>
        </div>

        <!-- Dates -->
        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <Label for="invoice-date">Data da Fatura *</Label>
            <Input
              id="invoice-date"
              v-model="invoiceDate"
              type="date"
              required
            />
          </div>

          <div class="space-y-2">
            <Label for="due-date">Data de Vencimento</Label>
            <Input
              id="due-date"
              v-model="dueDate"
              type="date"
            />
          </div>
        </div>

        <!-- Amounts -->
        <div class="grid gap-4 md:grid-cols-3">
          <div class="space-y-2">
            <Label for="amount">Valor Base (CVE) *</Label>
            <Input
              id="amount"
              v-model.number="amount"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
              @input="handleAmountChange"
              required
            />
          </div>

          <div class="space-y-2">
            <Label for="tax-amount">Imposto (CVE)</Label>
            <Input
              id="tax-amount"
              v-model.number="taxAmount"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
            />
          </div>

          <div class="space-y-2">
            <Label>Valor Total (CVE)</Label>
            <div class="flex h-10 items-center rounded-md border bg-muted px-3">
              <span class="font-bold">{{ totalAmount.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <!-- Status -->
        <div class="space-y-2">
          <Label for="status">Estado</Label>
          <Select v-model="status">
            <SelectTrigger id="status">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="RECEIVED">Recebida</SelectItem>
              <SelectItem value="APPROVED">Aprovada</SelectItem>
              <SelectItem value="SCHEDULED_PAYMENT">Pagamento Agendado</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <!-- Notes -->
        <div class="space-y-2">
          <Label for="notes">Notas</Label>
          <Textarea
            id="notes"
            v-model="notes"
            placeholder="Observações sobre a fatura..."
            rows="3"
          />
        </div>
      </div>

      <DialogFooter>
        <Button
          type="button"
          variant="outline"
          @click="handleClose"
          :disabled="isSubmitting"
        >
          Cancelar
        </Button>
        <Button
          type="button"
          @click="handleSubmit"
          :disabled="!isFormValid || isSubmitting"
        >
          {{ isSubmitting ? 'A criar...' : 'Criar Fatura' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
