<script setup lang="ts">
import { ref, watch } from 'vue'
import { X } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { purchasesApi } from '@/services/api'
import type { PurchaseOrder } from '@/types/models'

interface Props {
  open: boolean
  purchaseOrderId: number | null
}

interface Emits {
  (e: 'update:open', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const purchaseOrder = ref<PurchaseOrder | null>(null)
const isLoading = ref(false)

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

// Watch for changes to purchaseOrderId and fetch details
watch(() => [props.open, props.purchaseOrderId], async ([isOpen, orderId]) => {
  if (isOpen && orderId) {
    await fetchPurchaseOrder(orderId as number)
  }
})

async function fetchPurchaseOrder(id: number) {
  isLoading.value = true
  try {
    purchaseOrder.value = await purchasesApi.getPurchaseOrder(id)
  } catch (error) {
    console.error('Error loading purchase order:', error)
  } finally {
    isLoading.value = false
  }
}

function handleClose() {
  emit('update:open', false)
  // Clear data when closing
  setTimeout(() => {
    purchaseOrder.value = null
  }, 300)
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
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-5xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Detalhes da Ordem de Compra</DialogTitle>
        <DialogDescription>
          Informações completas sobre a ordem de compra
        </DialogDescription>
      </DialogHeader>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex min-h-[300px] items-center justify-center">
        <div class="text-center">
          <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4" />
          <p class="text-muted-foreground">A carregar detalhes...</p>
        </div>
      </div>

      <!-- Purchase Order Details -->
      <div v-else-if="purchaseOrder" class="space-y-6">
        <!-- Header Info -->
        <div class="grid gap-4 md:grid-cols-2 border-b pb-4">
          <div>
            <label class="text-sm font-medium text-muted-foreground">Número da Ordem</label>
            <p class="text-lg font-semibold">{{ purchaseOrder.po_number }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-muted-foreground">Estado</label>
            <div class="mt-1">
              <Badge :class="statusColors[purchaseOrder.status]" variant="outline">
                {{ statusLabels[purchaseOrder.status] }}
              </Badge>
            </div>
          </div>
          <div>
            <label class="text-sm font-medium text-muted-foreground">Fornecedor</label>
            <p class="text-base font-medium">{{ purchaseOrder.supplier_name || `Fornecedor #${purchaseOrder.supplier}` }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-muted-foreground">Valor Total</label>
            <p class="text-lg font-bold text-primary">{{ formatCurrency(purchaseOrder.total_amount) }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-muted-foreground">Data da Ordem</label>
            <p class="text-base">{{ formatDate(purchaseOrder.order_date) }}</p>
          </div>
          <div>
            <label class="text-sm font-medium text-muted-foreground">Entrega Prevista</label>
            <p class="text-base">
              {{ purchaseOrder.expected_delivery_date ? formatDate(purchaseOrder.expected_delivery_date) : '-' }}
            </p>
          </div>
        </div>

        <!-- Supplier Info (if available) -->
        <div v-if="purchaseOrder.supplier_info" class="border rounded-lg p-4 bg-muted/50">
          <h3 class="font-semibold mb-3">Informações do Fornecedor</h3>
          <div class="grid gap-2 md:grid-cols-2">
            <div v-if="purchaseOrder.supplier_info.contact_name">
              <label class="text-sm font-medium text-muted-foreground">Contacto</label>
              <p class="text-sm">{{ purchaseOrder.supplier_info.contact_name }}</p>
            </div>
            <div v-if="purchaseOrder.supplier_info.email">
              <label class="text-sm font-medium text-muted-foreground">Email</label>
              <p class="text-sm">{{ purchaseOrder.supplier_info.email }}</p>
            </div>
            <div v-if="purchaseOrder.supplier_info.phone">
              <label class="text-sm font-medium text-muted-foreground">Telefone</label>
              <p class="text-sm">{{ purchaseOrder.supplier_info.phone }}</p>
            </div>
            <div v-if="purchaseOrder.supplier_info.address">
              <label class="text-sm font-medium text-muted-foreground">Morada</label>
              <p class="text-sm">{{ purchaseOrder.supplier_info.address }}</p>
            </div>
          </div>
        </div>

        <!-- Items Table -->
        <div>
          <h3 class="font-semibold mb-3">Items da Ordem</h3>
          <div class="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item de Inventário</TableHead>
                  <TableHead>Produto</TableHead>
                  <TableHead class="text-right">Quantidade Encomendada</TableHead>
                  <TableHead class="text-right">Preço Unitário</TableHead>
                  <TableHead class="text-right">Total</TableHead>
                  <TableHead class="text-right">Quantidade Recebida</TableHead>
                  <TableHead class="text-right">Restante</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-if="!purchaseOrder.items || purchaseOrder.items.length === 0">
                  <TableCell colspan="7" class="text-center text-muted-foreground">
                    Nenhum item encontrado
                  </TableCell>
                </TableRow>
                <TableRow v-for="item in purchaseOrder.items" :key="item.id">
                  <TableCell class="font-medium">
                    {{ item.inventory_item_name || item.product_name || `Item #${item.inventory_item}` }}
                  </TableCell>
                  <TableCell>
                    <span class="text-sm text-muted-foreground">{{ item.product_name || '-' }}</span>
                  </TableCell>
                  <TableCell class="text-right">{{ item.quantity_ordered }}</TableCell>
                  <TableCell class="text-right">{{ formatCurrency(item.unit_price) }}</TableCell>
                  <TableCell class="text-right font-medium">
                    {{ formatCurrency(item.line_total || (parseFloat(item.quantity_ordered) * parseFloat(item.unit_price)).toFixed(2)) }}
                  </TableCell>
                  <TableCell class="text-right">{{ item.received_quantity }}</TableCell>
                  <TableCell class="text-right">
                    {{ item.remaining_quantity || (parseFloat(item.quantity_ordered) - parseFloat(item.received_quantity)).toFixed(2) }}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </div>

        <!-- Notes -->
        <div v-if="purchaseOrder.notes" class="border rounded-lg p-4 bg-muted/50">
          <label class="text-sm font-medium text-muted-foreground block mb-2">Notas</label>
          <p class="text-sm whitespace-pre-wrap">{{ purchaseOrder.notes }}</p>
        </div>

        <!-- Metadata -->
        <div class="grid gap-2 md:grid-cols-2 text-xs text-muted-foreground border-t pt-4">
          <div v-if="purchaseOrder.created_by_name">
            <label class="font-medium">Criado por</label>
            <p>{{ purchaseOrder.created_by_name }}</p>
          </div>
          <div>
            <label class="font-medium">Criado em</label>
            <p>{{ formatDate(purchaseOrder.created_at) }}</p>
          </div>
          <div>
            <label class="font-medium">Última atualização</label>
            <p>{{ formatDate(purchaseOrder.updated_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end border-t pt-4">
        <Button type="button" variant="outline" @click="handleClose">
          Fechar
        </Button>
      </div>
    </DialogContent>
  </Dialog>
</template>
