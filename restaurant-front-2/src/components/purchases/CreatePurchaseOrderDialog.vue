<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Trash2, X } from 'lucide-vue-next'
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { suppliersApi } from '@/services/api/suppliers'
import { inventoryApi, menuApi } from '@/services/api'
import type { InventoryItem, MenuItem } from '@/types/models'
import type { Supplier } from '@/types/models/supplier'
import type { CreatePurchaseOrderRequest } from '@/types/models'
import { get } from 'node_modules/axios/index.d.cts'

interface Props {
  open: boolean
}

interface Emits {
  (e: 'update:open', value: boolean): void
  (e: 'submit', data: CreatePurchaseOrderRequest): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Data
const suppliers = ref<Supplier[]>([])
const inventoryItems = ref<InventoryItem[]>([])
const menuItems = ref<MenuItem[]>([])
const isLoadingSuppliers = ref(false)
const isLoadingInventory = ref(false)
const isSubmitting = ref(false)

// Form fields
const selectedSupplier = ref<number | null>(null)
const orderDate = ref<string>(new Date().toISOString().split('T')[0])
const expectedDeliveryDate = ref<string>('')
const notes = ref<string>('')

// Line items
interface LineItem {
  id: string
  inventory_item: number | null
  quantity_ordered: number
  unit_price: number
}

const lineItems = ref<LineItem[]>([])

// Computed
const totalAmount = computed(() => {
  return lineItems.value.reduce((sum, item) => {
    if (item.inventory_item && item.quantity_ordered && item.unit_price) {
      return sum + (item.quantity_ordered * item.unit_price)
    }
    return sum
  }, 0)
})

const isFormValid = computed(() => {
  return (
    selectedSupplier.value &&
    orderDate.value &&
    lineItems.value.length > 0 &&
    lineItems.value.every(item =>
      item.inventory_item && item.quantity_ordered > 0 && item.unit_price > 0
    )
  )
})

// Methods
async function loadData() {
  isLoadingSuppliers.value = true
  isLoadingInventory.value = true

  try {
    const [suppliersData, inventoryData, menuItemsData] = await Promise.all([
      suppliersApi.listActive(),
      inventoryApi.getItems(),
      menuApi.getItems()
    ])
    suppliers.value = suppliersData
    inventoryItems.value = inventoryData
    menuItems.value = menuItemsData
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    isLoadingSuppliers.value = false
    isLoadingInventory.value = false
  }
}

function addLineItem() {
  lineItems.value.push({
    id: Math.random().toString(36).substr(2, 9),
    inventory_item: null,
    quantity_ordered: 1,
    unit_price: 0
  })
}

function removeLineItem(id: string) {
  lineItems.value = lineItems.value.filter(item => item.id !== id)
}

function getInventoryItemName(itemId: number): string {
  const item = inventoryItems.value.find(i => i.itemID === itemId)
  return item?.itemName || `Item #${itemId}`
}

function getProductName(itemId: number): string {
  const invItem = inventoryItems.value.find(i => i.itemID === itemId)
  if (!invItem || !invItem.menu_item) {
    return '-'
  }
  const menuItem = menuItems.value.find(m => m.itemID === invItem.menu_item)
  return menuItem?.name || '-'
}

function handleClose() {
  emit('update:open', false)
}

async function handleSubmit() {
  if (!isFormValid.value) return

  isSubmitting.value = true

  try {
    const payload: CreatePurchaseOrderRequest = {
      supplier: selectedSupplier.value!,
      order_date: orderDate.value,
      expected_delivery_date: expectedDeliveryDate.value || null,
      notes: notes.value || undefined,
      items: lineItems.value.map(item => ({
        inventory_item: item.inventory_item!,
        quantity_ordered: item.quantity_ordered,
        unit_price: item.unit_price
      }))
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
  selectedSupplier.value = null
  orderDate.value = new Date().toISOString().split('T')[0]
  expectedDeliveryDate.value = ''
  notes.value = ''
  lineItems.value = []
}

// Lifecycle
onMounted(() => {
  loadData()
  // Add one empty line item by default
  addLineItem()
})
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="min-w-3xl max-w-7xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Nova Ordem de Compra</DialogTitle>
        <DialogDescription>
          Criar uma nova ordem de compra para fornecedor
        </DialogDescription>
      </DialogHeader>

      <div class="space-y-6">
        <!-- Supplier Selection -->
        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <Label for="supplier">Fornecedor *</Label>
            <Select v-model="selectedSupplier" :disabled="isLoadingSuppliers">
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

          <div class="space-y-2">
            <Label for="order-date">Data da Ordem *</Label>
            <Input
              id="order-date"
              v-model="orderDate"
              type="date"
              required
            />
          </div>
        </div>

        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <Label for="delivery-date">Data de Entrega Prevista</Label>
            <Input
              id="delivery-date"
              v-model="expectedDeliveryDate"
              type="date"
            />
          </div>
        </div>

        <!-- Line Items -->
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <Label>Items *</Label>
            <Button
              type="button"
              variant="outline"
              size="sm"
              @click="addLineItem"
            >
              <Plus class="mr-2 h-4 w-4" />
              Adicionar Item
            </Button>
          </div>

          <div class="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead class="w-[30%]">Item de Inventário</TableHead>
                  <TableHead class="w-[20%]">Produto</TableHead>
                  <TableHead class="w-[15%]">Quantidade</TableHead>
                  <TableHead class="w-[20%]">Preço Unitário (CVE)</TableHead>
                  <TableHead class="w-[10%] text-right">Total</TableHead>
                  <TableHead class="w-[5%]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-if="lineItems.length === 0">
                  <TableCell colspan="6" class="text-center text-muted-foreground">
                    Clique em "Adicionar Item" para começar
                  </TableCell>
                </TableRow>
                <TableRow v-for="item in lineItems" :key="item.id">
                  <TableCell>
                    <Select
                      v-model="item.inventory_item"
                      :disabled="isLoadingInventory"
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecionar item">
                          <span v-if="item.inventory_item">
                            {{ getInventoryItemName(item.inventory_item) }}
                          </span>
                        </SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem
                          v-for="invItem in inventoryItems"
                          :key="invItem.itemID"
                          :value="invItem.itemID"
                        >
                          {{ getInventoryItemName(invItem.itemID) }}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell>
                    <span class="text-sm text-muted-foreground">
                      {{ item.inventory_item ? getProductName(item.inventory_item) : '-' }}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Input
                      v-model.number="item.quantity_ordered"
                      type="number"
                      min="0.01"
                      step="0.01"
                      placeholder="0.00"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      v-model.number="item.unit_price"
                      type="number"
                      min="0.01"
                      step="0.01"
                      placeholder="0.00"
                    />
                  </TableCell>
                  <TableCell class="text-right font-medium">
                    {{ (item.quantity_ordered * item.unit_price).toFixed(2) }}
                  </TableCell>
                  <TableCell>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      @click="removeLineItem(item.id)"
                    >
                      <Trash2 class="h-4 w-4 text-red-500" />
                    </Button>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>

          <!-- Total -->
          <div class="flex justify-end">
            <div class="bg-muted p-4 rounded-lg">
              <div class="text-sm font-medium mb-1">Valor Total:</div>
              <div class="text-2xl font-bold">
                {{ totalAmount.toFixed(2) }} CVE
              </div>
            </div>
          </div>
        </div>

        <!-- Notes -->
        <div class="space-y-2">
          <Label for="notes">Notas</Label>
          <Textarea
            id="notes"
            v-model="notes"
            placeholder="Observações sobre a ordem de compra..."
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
          {{ isSubmitting ? 'A criar...' : 'Criar Ordem de Compra' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
