<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ordersApi, cashRegisterApi, menuApi } from '@/services/api'
import { paymentsApi, type ProcessPaymentPayload } from '@/services/api/payments'
// import type { CashRegister } from '@/services/api/cashRegister'
import type { OrderItem, CashRegister, Order, MenuItem  } from '@/types/models'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  CreditCard,
  Wallet,
  Check,
  ArrowLeft,
  DollarSign,
  Delete,
  Printer,
  FileText,
  Download,
} from 'lucide-vue-next'
import PrintReceipt from '@/components/print/PrintReceipt.vue'
import { usePrint } from '@/composables/usePrint'

const route = useRoute()
const router = useRouter()

// Print composable
const { printElement } = usePrint()

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
const orderID = computed(() => Number(route.query.order))
const order = ref<Order | null>(null)
const menuItems = ref<MenuItem[]>([])
const cashRegister = ref<CashRegister | null>(null)
const payments = ref<any[]>([])
const isLoading = ref(true)

// Item selection state
// Map of menu_item_id -> quantity to pay
const selectedItems = ref<Map<number, number>>(new Map())

// Ensure selectedItems is always a Map (handles hot reload edge cases)
function ensureMapInitialized() {
  if (!(selectedItems.value instanceof Map)) {
    selectedItems.value = new Map()
  }
}

// Payment state
const paymentMethod = ref<'CASH' | 'CREDIT_CARD' | 'DEBIT_CARD' | 'ONLINE'>('CASH')
const paymentAmount = ref<string>('')
const useManualAmount = ref(false) // Toggle between item-based and manual amount
const isProcessingPayment = ref(false)
const paymentSuccess = ref(false)
const changeDue = ref<number>(0)
const lastPaymentId = ref<number | null>(null)

// e-Fatura state
const showEFaturaDialog = ref(false)
const isGeneratingEFatura = ref(false)
const eFaturaGenerated = ref(false)
const eFaturaResult = ref<any>(null)
const customerTaxId = ref<string>('')

// Cash register dialog
const showCashRegisterDialog = ref(false)
const initialAmount = ref<string>('100.00')
const isOpeningRegister = ref(false)

// Computed: Selected items total (with IVA)
const selectedItemsTotal = computed(() => {
  if (!order.value) return 0
  ensureMapInitialized()

  let subtotal = 0
  order.value.items.forEach((item) => {
    const quantityToPay = selectedItems.value.get(item.menu_item)
    if (quantityToPay && quantityToPay > 0) {
      // Calculate based on quantity to pay (not total quantity in order)
      subtotal += Number(item.price) * quantityToPay
    }
  })

  // Apply IVA (15%)
  const iva = subtotal * 0.15
  return subtotal + iva
})

// Computed: Filter out already paid items
const unpaidItems = computed(() => {
  if (!order.value) return []
  return order.value.items.filter((item: any) => !item.is_paid)
})

// Computed: Order totals
const orderTotals = computed(() => {
  if (!order.value) {
    return {
      totalAmount: 0,
      totalIva: 0,
      grandTotal: 0,
      totalPaid: 0,
      remainingAmount: 0,
    }
  }
  return {
    totalAmount: Number(order.value.totalAmount || 0),
    totalIva: Number(order.value.totalIva || 0),
    grandTotal: Number(order.value.grandTotal || 0),
    totalPaid: Number(order.value.total_paid || 0),
    remainingAmount: Number(order.value.remaining_amount || 0),
  }
})

// Computed: Selected items count
const selectedItemsCount = computed(() => selectedItems.value.size)

// Computed: All items selected (only count unpaid items)
const allItemsSelected = computed(() => {
  if (!order.value) return false
  return selectedItems.value.size === unpaidItems.value.length
})

// Watch selected items and update payment amount
watch(selectedItemsTotal, (newTotal) => {
  if (!useManualAmount.value) {
    paymentAmount.value = newTotal.toFixed(2)
  }
})

// Computed: Validation
const isAmountValid = computed(() => {
  const amount = parseFloat(paymentAmount.value)
  return !isNaN(amount) && amount > 0
})

// Computed: Payment status based on amount
const paymentStatus = computed(() => {
  const amount = parseFloat(paymentAmount.value) || 0
  // Use remaining amount instead of grandTotal for partial payment scenarios
  const amountNeeded = orderTotals.value.remainingAmount > 0 ? orderTotals.value.remainingAmount : orderTotals.value.grandTotal
  if (amount >= amountNeeded) return 'full'
  if (amount > 0) return 'partial'
  return 'invalid'
})

// Computed: Real-time change
const calculatedChange = computed(() => {
  if (paymentMethod.value !== 'CASH') return 0
  const amount = parseFloat(paymentAmount.value) || 0
  const totalToPay = useManualAmount.value ? orderTotals.value.grandTotal : selectedItemsTotal.value
  return Math.max(0, amount - totalToPay)
})

// Set item quantity to pay
function setItemQuantity(menuItemId: number, quantity: number) {
  if (!order.value) return
  ensureMapInitialized()

  const item = order.value.items.find(i => i.menu_item === menuItemId)
  if (!item) return

  // Get remaining quantity for this item
  const maxQuantity = (item as any).remaining_quantity || item.quantity

  if (quantity <= 0) {
    selectedItems.value.delete(menuItemId)
  } else {
    // Don't allow paying more than remaining
    const finalQuantity = Math.min(quantity, maxQuantity)
    selectedItems.value.set(menuItemId, finalQuantity)
  }

  // Force reactivity
  selectedItems.value = new Map(selectedItems.value)
}

// Toggle item selection (select all remaining quantity)
function toggleItem(menuItemId: number) {
  if (!order.value) return
  ensureMapInitialized()

  if (selectedItems.value.has(menuItemId)) {
    selectedItems.value.delete(menuItemId)
  } else {
    // Select the full remaining quantity
    const item = order.value.items.find(i => i.menu_item === menuItemId)
    if (item) {
      const remainingQty = (item as any).remaining_quantity || item.quantity
      selectedItems.value.set(menuItemId, remainingQty)
    }
  }
  // Force reactivity
  selectedItems.value = new Map(selectedItems.value)
}

// Select all items (only unpaid items, full remaining quantities)
function selectAllItems() {
  if (!order.value) return
  const newMap = new Map<number, number>()
  unpaidItems.value.forEach(item => {
    const remainingQty = (item as any).remaining_quantity || item.quantity
    newMap.set(item.menu_item, remainingQty)
  })
  selectedItems.value = newMap
}

// Deselect all items
function deselectAllItems() {
  selectedItems.value = new Map()
}

// Check if item is selected
function isItemSelected(menuItemId: number): boolean {
  ensureMapInitialized()
  return selectedItems.value.has(menuItemId) && (selectedItems.value.get(menuItemId) || 0) > 0
}

// Get selected quantity for an item
function getSelectedQuantity(menuItemId: number): number {
  ensureMapInitialized()
  return selectedItems.value.get(menuItemId) || 0
}

// Get item name
function getItemName(menuItemId: number): string {
  const item = menuItems.value.find(m => m.itemID === menuItemId)
  return item?.name || 'Item'
}

// Switch to manual amount mode
function enableManualAmount() {
  useManualAmount.value = true
}

// Switch to item-based amount mode
function enableItemBasedAmount() {
  useManualAmount.value = false
  paymentAmount.value = selectedItemsTotal.value.toFixed(2)
}

// Numeric keypad
function appendNumber(num: string) {
  if (paymentAmount.value === '' || paymentAmount.value === '0') {
    paymentAmount.value = num
  } else {
    paymentAmount.value += num
  }
}

function appendDecimal() {
  if (!paymentAmount.value.includes('.')) {
    paymentAmount.value = (paymentAmount.value || '0') + '.'
  }
}

function clearAmount() {
  paymentAmount.value = ''
}

function backspace() {
  if (paymentAmount.value.length > 0) {
    paymentAmount.value = paymentAmount.value.slice(0, -1)
  }
}

// Quick amount buttons
function setAmount(percentage: number) {
  const total = useManualAmount.value ? orderTotals.value.grandTotal : selectedItemsTotal.value
  const amount = (total * percentage).toFixed(2)
  paymentAmount.value = amount
}

function setExactAmount() {
  const total = useManualAmount.value ? orderTotals.value.grandTotal : selectedItemsTotal.value
  paymentAmount.value = total.toFixed(2)
}

// Fetch data
async function fetchData() {
  isLoading.value = true
  try {
    const [orderData, register, items, paymentsData] = await Promise.all([
      ordersApi.getOrder(orderID.value),
      cashRegisterApi.getOpenRegister(),
      menuApi.getItems(),
      paymentsApi.getPaymentsByOrder(orderID.value).catch(() => [])
    ])

    order.value = orderData
    cashRegister.value = register
    menuItems.value = items
    payments.value = paymentsData

    // Select all UNPAID items by default with full remaining quantities
    const unpaid = orderData.items.filter((item: any) => !item.is_paid)
    const newMap = new Map<number, number>()
    unpaid.forEach((item: any) => {
      const remainingQty = item.remaining_quantity || item.quantity
      newMap.set(item.menu_item, remainingQty)
    })
    selectedItems.value = newMap

    // Pre-fill payment amount with selected items total
    paymentAmount.value = selectedItemsTotal.value.toFixed(2)

    // Show dialog if no cash register
    if (!register) {
      showCashRegisterDialog.value = true
    }
  } catch (error: any) {
    showToast(error.message || 'Erro ao carregar pedido', 'error')
    router.back()
  } finally {
    isLoading.value = false
  }
}

// Open cash register
async function openCashRegister() {
  const amount = parseFloat(initialAmount.value)
  if (isNaN(amount) || amount < 0) {
    showToast('Por favor insira um valor válido', 'error')
    return
  }

  isOpeningRegister.value = true
  try {
    const register = await cashRegisterApi.start({ initial_amount: amount })
    cashRegister.value = register
    showCashRegisterDialog.value = false
    showToast('Caixa aberta com sucesso!', 'success')
  } catch (error: any) {
    showToast(error.response?.data?.error || error.message || 'Erro ao abrir caixa', 'error')
  } finally {
    isOpeningRegister.value = false
  }
}

// Cancel and go back
function cancelPayment() {
  if (paymentSuccess.value) return
  router.back()
}

// Select payment method
function selectPaymentMethod(method: typeof paymentMethod.value) {
  paymentMethod.value = method
}

// Process payment
async function processPayment() {
  if (!order.value || !cashRegister.value || isProcessingPayment.value) return

  if (selectedItemsCount.value === 0 && !useManualAmount.value) {
    showToast('Selecione pelo menos um item para pagar', 'error')
    return
  }

  const amount = parseFloat(paymentAmount.value)
  if (isNaN(amount) || amount <= 0) {
    showToast('Por favor insira um valor válido', 'error')
    return
  }

  // Warn for partial payment - use remaining amount
  const amountNeeded = orderTotals.value.remainingAmount > 0 ? orderTotals.value.remainingAmount : orderTotals.value.grandTotal
  if (amount < amountNeeded) {
    const stillOwed = amountNeeded - amount
    if (!confirm(`Pagamento parcial de CVE${amount.toFixed(2)}. Ainda faltam CVE${stillOwed.toFixed(2)} para completar o pagamento. Continuar?`)) {
      return
    }
  }

  isProcessingPayment.value = true

  try {
    ensureMapInitialized()

    // Build selected_items array with quantities
    const selected_items = !useManualAmount.value
      ? Array.from(selectedItems.value.entries()).map(([menu_item_id, quantity]) => ({
          menu_item_id,
          quantity
        }))
      : undefined

    const payload: ProcessPaymentPayload = {
      orderID: order.value.orderID,
      amount: amount,
      payment_method: paymentMethod.value,
      selected_items
    }

    // Debug logging
    console.log('Payment Payload:', payload)
    console.log('Selected Items with Quantities:', selected_items)
    console.log('Use Manual Amount:', useManualAmount.value)

    const response = await paymentsApi.processPayment(payload)

    // Store payment ID for e-Fatura generation
    lastPaymentId.value = response.payment?.paymentID || null

    // Show success screen
    paymentSuccess.value = true
    changeDue.value = parseFloat(response.change_due)

    // No auto-redirect - let user decide when to leave
    // They may want to print receipt or generate e-Fatura
  } catch (error: any) {
    const errorMessage = error.response?.data?.error || error.message || 'Erro ao processar pagamento'
    const hint = error.response?.data?.hint
    showToast(hint ? `${errorMessage}\n${hint}` : errorMessage, 'error')
  } finally {
    isProcessingPayment.value = false
  }
}

// Format date/time helper
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

// e-Fatura functions
function openEFaturaDialog() {
  customerTaxId.value = ''
  eFaturaGenerated.value = false
  eFaturaResult.value = null
  showEFaturaDialog.value = true
}

async function generateEFatura() {
  if (!lastPaymentId.value) {
    showToast('ID do pagamento não encontrado', 'error')
    return
  }

  try {
    isGeneratingEFatura.value = true

    // Pass customer tax ID if provided (otherwise backend will use "Consumidor Final")
    const result = await paymentsApi.generateEFatura(
      lastPaymentId.value,
      customerTaxId.value || undefined
    )

    eFaturaGenerated.value = true
    eFaturaResult.value = result

    showToast('e-Fatura gerada com sucesso!', 'success')
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Erro ao gerar e-Fatura'
    showToast(errorMessage, 'error')
  } finally {
    isGeneratingEFatura.value = false
  }
}

async function downloadEFaturaXML() {
  if (!lastPaymentId.value) {
    showToast('ID do pagamento não encontrado', 'error')
    return
  }

  try {
    const blob = await paymentsApi.downloadEFaturaXML(lastPaymentId.value)

    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `efatura_${lastPaymentId.value}.xml`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    showToast('XML descarregado com sucesso!', 'success')
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Erro ao descarregar XML'
    showToast(errorMessage, 'error')
  }
}

onMounted(() => {
  if (!orderID.value) {
    showToast('ID do pedido não fornecido', 'error')
    router.push('/pagamentos')
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
      class="fixed top-4 right-4 z-50 rounded-lg border px-4 py-3 shadow-lg transition-all"
      :class="toastVariant === 'success' ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'"
    >
      {{ toastMessage }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" @click="cancelPayment" :disabled="paymentSuccess">
          <ArrowLeft class="h-5 w-5" />
        </Button>
        <div>
          <h1 class="text-3xl font-bold">Processar Pagamento</h1>
          <p class="text-sm text-muted-foreground">Pedido #{{ orderID }}</p>
        </div>
      </div>
      <Button
        v-if="order && !isLoading"
        variant="outline"
        @click="printReceipt"
      >
        <Printer class="mr-2 h-4 w-4" />
        Imprimir Recibo
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
      <Skeleton class="h-full w-full" />
      <Skeleton class="h-full w-full" />
    </div>

    <!-- Success Screen -->
    <div v-else-if="paymentSuccess" class="flex-1 flex items-center justify-center">
      <Card class="w-full max-w-md">
        <CardContent class="pt-6">
          <div class="flex flex-col items-center text-center space-y-4">
            <div class="rounded-full bg-green-100 p-3">
              <Check class="h-12 w-12 text-green-600" />
            </div>
            <div>
              <h2 class="text-2xl font-bold mb-2">Pagamento Concluído!</h2>
              <p class="text-muted-foreground">O pagamento foi processado com sucesso.</p>
            </div>

            <Separator />

            <div class="w-full space-y-2">
              <div class="flex justify-between">
                <span class="text-muted-foreground">Total Pago:</span>
                <span class="font-semibold">CVE{{ parseFloat(paymentAmount).toFixed(2) }}</span>
              </div>
              <div v-if="paymentMethod === 'CASH' && changeDue > 0" class="flex justify-between text-lg">
                <span class="font-medium">Troco:</span>
                <span class="font-bold text-green-600">CVE{{ changeDue.toFixed(2) }}</span>
              </div>
            </div>

            <Button
              variant="outline"
              @click="printReceipt"
              class="w-full"
            >
              <Printer class="mr-2 h-4 w-4" />
              Imprimir Recibo
            </Button>

            <Button
              v-if="lastPaymentId && !eFaturaGenerated"
              variant="default"
              @click="openEFaturaDialog"
              class="w-full"
            >
              <FileText class="mr-2 h-4 w-4" />
              Gerar e-Fatura
            </Button>

            <div v-if="lastPaymentId && eFaturaGenerated" class="w-full p-3 bg-green-50 border border-green-200 rounded-lg">
              <div class="flex items-center gap-2 text-sm text-green-900 mb-2">
                <Check class="h-4 w-4" />
                <span class="font-semibold">e-Fatura gerada com sucesso!</span>
              </div>
              <div class="text-xs text-green-800 space-y-1">
                <div><strong>Fatura:</strong> {{ eFaturaResult?.payment?.invoice_no }}</div>
                <div><strong>IUD:</strong> {{ eFaturaResult?.efatura?.iud }}</div>
                <div v-if="eFaturaResult?.efatura?.mode === 'simulation'" class="text-orange-600">
                  ⚠️ Modo simulação (XML guardado localmente)
                </div>
              </div>
              <Button
                size="sm"
                variant="outline"
                @click="downloadEFaturaXML"
                class="w-full mt-2"
              >
                <Download class="mr-2 h-3 w-3" />
                Descarregar XML
              </Button>
            </div>

            <Separator />

            <Button
              variant="default"
              size="lg"
              @click="router.push('/pagamentos')"
              class="w-full"
            >
              Voltar para Pagamentos
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Main Payment Interface -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 overflow-hidden">
      <!-- Left Column: Order Summary -->
      <div class="space-y-4 overflow-y-auto">
        <Card>
          <CardHeader>
            <div class="flex items-center justify-between">
              <CardTitle>Itens do Pedido</CardTitle>
              <div class="flex gap-2">
                <Button size="sm" variant="outline" @click="selectAllItems()">
                  Todos
                </Button>
                <Button size="sm" variant="outline" @click="deselectAllItems()">
                  Nenhum
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div v-if="order" class="space-y-4">
              <!-- Order Info -->
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-muted-foreground">Pedido:</span>
                  <span class="font-semibold">#{{ order.orderID }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-muted-foreground">Mesa:</span>
                  <span class="font-semibold">{{ order.details.table }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-muted-foreground">Data:</span>
                  <span>{{ formatDateTime(order.created_at) }}</span>
                </div>
              </div>

              <Separator />

              <!-- Items List with Checkboxes (Only show unpaid items) -->
              <div class="space-y-2">
                <h3 class="font-semibold text-sm flex items-center gap-2">
                  Selecione os Itens:
                  <Badge variant="secondary">{{ selectedItemsCount }}/{{ unpaidItems.length }}</Badge>
                </h3>
                <div v-if="unpaidItems.length === 0" class="text-center py-8 text-muted-foreground">
                  <p>Todos os itens já foram pagos!</p>
                </div>
                <div v-else class="space-y-2 max-h-64 overflow-y-auto">
                  <div
                    v-for="item in unpaidItems"
                    :key="item.menu_item"
                    class="flex items-center gap-3 text-sm py-2 px-2 rounded border"
                    :class="{ 'bg-accent border-primary': isItemSelected(item.menu_item) }"
                  >
                    <Checkbox
                      :checked="isItemSelected(item.menu_item)"
                      @update:checked="toggleItem(item.menu_item)"
                    />
                    <div class="flex-1 flex items-center justify-between gap-3">
                      <div class="flex-1">
                        <div class="font-medium">{{ getItemName(item.menu_item) }}</div>
                        <div class="text-xs text-muted-foreground">
                          CVE{{ Number(item.price).toFixed(2) }} cada
                          <span v-if="(item as any).remaining_quantity < item.quantity" class="text-orange-600">
                            • {{ (item as any).remaining_quantity }} de {{ item.quantity }} restantes
                          </span>
                          <span v-else>
                            • {{ item.quantity }} disponível{{ item.quantity > 1 ? 'is' : '' }}
                          </span>
                        </div>
                      </div>
                      <div class="flex items-center gap-2">
                        <Label class="text-xs text-muted-foreground whitespace-nowrap">Qtd:</Label>
                        <Input
                          type="number"
                          min="0"
                          :max="(item as any).remaining_quantity || item.quantity"
                          :value="getSelectedQuantity(item.menu_item)"
                          @input="(e) => setItemQuantity(item.menu_item, parseInt((e.target as HTMLInputElement).value) || 0)"
                          class="w-16 h-8 text-center"
                          @click.stop
                        />
                        <span class="font-semibold w-20 text-right">
                          CVE{{ (Number(item.price) * getSelectedQuantity(item.menu_item)).toFixed(2) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              <!-- Pricing -->
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-muted-foreground">Total do Pedido:</span>
                  <span>CVE{{ orderTotals.grandTotal.toFixed(2) }}</span>
                </div>
                <div v-if="orderTotals.totalPaid > 0" class="flex justify-between text-sm">
                  <span class="text-muted-foreground">Já Pago:</span>
                  <span class="text-green-600 font-semibold">-CVE{{ orderTotals.totalPaid.toFixed(2) }}</span>
                </div>
                <div v-if="orderTotals.totalPaid > 0" class="flex justify-between text-sm">
                  <span class="text-muted-foreground">Restante:</span>
                  <span class="font-semibold">CVE{{ orderTotals.remainingAmount.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-muted-foreground">Itens Selecionados:</span>
                  <span class="font-semibold">CVE{{ selectedItemsTotal.toFixed(2) }}</span>
                </div>
                <Separator />
                <div class="flex justify-between text-xl font-bold">
                  <span>A Pagar Agora:</span>
                  <span class="text-primary">CVE{{ selectedItemsTotal.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Cash Register Info -->
        <Card v-if="cashRegister">
          <CardHeader>
            <CardTitle class="text-sm">Informação da Caixa</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-muted-foreground">Valor Inicial:</span>
                <span class="font-semibold">CVE{{ Number(cashRegister.initial_amount).toFixed(2) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Estado:</span>
                <span class="font-semibold text-green-600">Aberta</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Right Column: Payment Input -->
      <div class="space-y-4 overflow-y-auto">
        <Card>
          <CardHeader>
            <CardTitle>Método de Pagamento</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-2 gap-3">
              <Button
                size="lg"
                :variant="paymentMethod === 'CASH' ? 'default' : 'outline'"
                class="h-20 flex flex-col gap-2"
                @click="selectPaymentMethod('CASH')"
              >
                <Wallet class="h-6 w-6" />
                <span class="text-sm font-semibold">Dinheiro</span>
              </Button>

              <Button
                size="lg"
                :variant="paymentMethod === 'CREDIT_CARD' ? 'default' : 'outline'"
                class="h-20 flex flex-col gap-2"
                @click="selectPaymentMethod('CREDIT_CARD')"
              >
                <CreditCard class="h-6 w-6" />
                <span class="text-sm font-semibold">Cartão Crédito</span>
              </Button>

              <Button
                size="lg"
                :variant="paymentMethod === 'DEBIT_CARD' ? 'default' : 'outline'"
                class="h-20 flex flex-col gap-2"
                @click="selectPaymentMethod('DEBIT_CARD')"
              >
                <CreditCard class="h-6 w-6" />
                <span class="text-sm font-semibold">Cartão Débito</span>
              </Button>

              <Button
                size="lg"
                :variant="paymentMethod === 'ONLINE' ? 'default' : 'outline'"
                class="h-20 flex flex-col gap-2"
                @click="selectPaymentMethod('ONLINE')"
              >
                <DollarSign class="h-6 w-6" />
                <span class="text-sm font-semibold">Online</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Valor do Pagamento</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- Mode Toggle -->
            <div class="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                class="flex-1"
                :class="{ 'bg-accent': !useManualAmount }"
                @click="enableItemBasedAmount()"
              >
                Itens Selecionados
              </Button>
              <Button
                variant="outline"
                size="sm"
                class="flex-1"
                :class="{ 'bg-accent': useManualAmount }"
                @click="enableManualAmount()"
              >
                Valor Manual
              </Button>
            </div>

            <!-- Quick Amount Buttons -->
            <div class="grid grid-cols-3 gap-2">
              <Button variant="outline" @click="setAmount(0.5)">50%</Button>
              <Button variant="outline" @click="setAmount(0.75)">75%</Button>
              <Button variant="default" @click="setExactAmount()">100%</Button>
            </div>

            <!-- Amount Display -->
            <div class="space-y-2">
              <Label>Valor Recebido</Label>
              <div class="relative">
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-2xl text-muted-foreground">CVE</span>
                <Input
                  v-model="paymentAmount"
                  type="text"
                  :readonly="!useManualAmount"
                  class="pl-12 text-4xl font-bold h-20 text-center"
                  :class="{
                    'border-green-500 focus-visible:ring-green-500': paymentStatus === 'full',
                    'border-yellow-500 focus-visible:ring-yellow-500': paymentStatus === 'partial',
                    'border-red-500 focus-visible:ring-red-500': paymentStatus === 'invalid'
                  }"
                />
              </div>
              <div v-if="paymentStatus === 'partial'" class="flex items-center gap-2">
                <Badge variant="secondary" class="text-xs">
                  Pagamento Parcial: Ainda faltam CVE{{ ((orderTotals.remainingAmount > 0 ? orderTotals.remainingAmount : orderTotals.grandTotal) - parseFloat(paymentAmount || '0')).toFixed(2) }}
                </Badge>
              </div>
            </div>

            <!-- Numeric Keypad (only for manual mode) -->
            <div v-if="useManualAmount" class="grid grid-cols-3 gap-2">
              <Button variant="outline" size="lg" @click="appendNumber('7')" class="h-14 text-xl">7</Button>
              <Button variant="outline" size="lg" @click="appendNumber('8')" class="h-14 text-xl">8</Button>
              <Button variant="outline" size="lg" @click="appendNumber('9')" class="h-14 text-xl">9</Button>

              <Button variant="outline" size="lg" @click="appendNumber('4')" class="h-14 text-xl">4</Button>
              <Button variant="outline" size="lg" @click="appendNumber('5')" class="h-14 text-xl">5</Button>
              <Button variant="outline" size="lg" @click="appendNumber('6')" class="h-14 text-xl">6</Button>

              <Button variant="outline" size="lg" @click="appendNumber('1')" class="h-14 text-xl">1</Button>
              <Button variant="outline" size="lg" @click="appendNumber('2')" class="h-14 text-xl">2</Button>
              <Button variant="outline" size="lg" @click="appendNumber('3')" class="h-14 text-xl">3</Button>

              <Button variant="outline" size="lg" @click="appendDecimal()" class="h-14 text-xl">.</Button>
              <Button variant="outline" size="lg" @click="appendNumber('0')" class="h-14 text-xl">0</Button>
              <Button variant="destructive" size="lg" @click="backspace()" class="h-14">
                <Delete class="h-5 w-5" />
              </Button>
            </div>

            <!-- Clear Button (only for manual mode) -->
            <Button v-if="useManualAmount" variant="outline" class="w-full" @click="clearAmount()">Limpar</Button>

            <!-- Change Display (Cash Only) -->
            <div
              v-if="paymentMethod === 'CASH' && calculatedChange > 0"
              class="bg-green-50 dark:bg-green-950 border-2 border-green-500 rounded-lg p-4"
            >
              <div class="flex justify-between items-center">
                <span class="text-lg font-semibold text-green-900 dark:text-green-200">Troco:</span>
                <span class="text-3xl font-bold text-green-700 dark:text-green-300">
                  CVE{{ calculatedChange.toFixed(2) }}
                </span>
              </div>
            </div>

            <Separator />

            <!-- Action Buttons -->
            <div class="flex gap-3">
              <Button
                variant="outline"
                class="flex-1"
                size="lg"
                @click="cancelPayment"
                :disabled="isProcessingPayment"
              >
                Cancelar
              </Button>
              <Button
                class="flex-1"
                size="lg"
                @click="processPayment"
                :disabled="!isAmountValid || isProcessingPayment || !cashRegister || (selectedItemsCount === 0 && !useManualAmount)"
              >
                <CreditCard v-if="!isProcessingPayment" class="mr-2 h-5 w-5" />
                <span v-if="isProcessingPayment">Processando...</span>
                <span v-else>Confirmar Pagamento</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Cash Register Dialog -->
    <Dialog v-model:open="showCashRegisterDialog" :close-on-escape="false" :close-on-outside-click="false">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Caixa Fechada</DialogTitle>
          <DialogDescription>
            Não há nenhuma caixa aberta. Por favor, abra uma caixa antes de processar pagamentos.
          </DialogDescription>
        </DialogHeader>

        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label>Valor Inicial da Caixa</Label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">CVE</span>
              <Input
                v-model="initialAmount"
                type="number"
                step="0.01"
                min="0"
                placeholder="100.00"
                class="pl-8"
              />
            </div>
            <p class="text-xs text-muted-foreground">
              Insira o valor inicial em dinheiro na caixa registadora.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="cancelPayment" :disabled="isOpeningRegister">
            Cancelar
          </Button>
          <Button @click="openCashRegister" :disabled="isOpeningRegister">
            <Wallet v-if="!isOpeningRegister" class="mr-2 h-4 w-4" />
            <span v-if="isOpeningRegister">Abrindo...</span>
            <span v-else>Abrir Caixa</span>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- e-Fatura Dialog -->
    <Dialog v-model:open="showEFaturaDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Gerar e-Fatura Eletrónica</DialogTitle>
          <DialogDescription>
            A e-Fatura será enviada à DNRE (Direção Nacional de Receitas do Estado) conforme legislação de Cabo Verde.
          </DialogDescription>
        </DialogHeader>

        <div v-if="!eFaturaGenerated" class="space-y-4 py-4">
          <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-start gap-2">
              <FileText class="h-5 w-5 text-blue-600 mt-0.5" />
              <div class="text-sm text-blue-900">
                <p class="font-semibold mb-1">Informações da Fatura</p>
                <ul class="space-y-1 text-xs">
                  <li><strong>Pedido:</strong> #{{ orderID }}</li>
                  <li><strong>Total:</strong> CVE{{ parseFloat(paymentAmount).toFixed(2) }}</li>
                  <li><strong>Método:</strong> {{ paymentMethod }}</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="space-y-2">
            <Label>NIF do Cliente (opcional)</Label>
            <Input
              v-model="customerTaxId"
              type="text"
              placeholder="Ex: 123456789"
              maxlength="20"
            />
            <p class="text-xs text-muted-foreground">
              Deixe em branco para "Consumidor Final" (999999999)
            </p>
          </div>

          <div class="p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <p class="text-xs text-orange-900">
              ⚠️ <strong>Modo Simulação:</strong> A e-Fatura será guardada localmente como XML. Quando as credenciais DNRE estiverem disponíveis, será enviada automaticamente.
            </p>
          </div>
        </div>

        <div v-else class="py-4">
          <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div class="flex items-center gap-2 text-green-900 mb-3">
              <Check class="h-5 w-5" />
              <span class="font-semibold">e-Fatura gerada com sucesso!</span>
            </div>
            <div class="text-sm text-green-800 space-y-2">
              <div class="grid grid-cols-2 gap-2">
                <span class="text-muted-foreground">Fatura Nº:</span>
                <span class="font-semibold">{{ eFaturaResult?.payment?.invoice_no }}</span>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <span class="text-muted-foreground">IUD:</span>
                <span class="font-mono text-xs break-all">{{ eFaturaResult?.efatura?.iud }}</span>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <span class="text-muted-foreground">Modo:</span>
                <span class="uppercase text-xs">
                  {{ eFaturaResult?.efatura?.mode === 'simulation' ? '🟡 Simulação' : '🟢 Produção' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            v-if="!eFaturaGenerated"
            variant="outline"
            @click="showEFaturaDialog = false"
            :disabled="isGeneratingEFatura"
          >
            Cancelar
          </Button>
          <Button
            v-if="!eFaturaGenerated"
            @click="generateEFatura"
            :disabled="isGeneratingEFatura"
          >
            <FileText v-if="!isGeneratingEFatura" class="mr-2 h-4 w-4" />
            <span v-if="isGeneratingEFatura">Gerando...</span>
            <span v-else>Gerar e-Fatura</span>
          </Button>
          <Button
            v-else
            variant="outline"
            @click="downloadEFaturaXML"
          >
            <Download class="mr-2 h-4 w-4" />
            Descarregar XML
          </Button>
          <Button
            v-if="eFaturaGenerated"
            @click="showEFaturaDialog = false"
          >
            Fechar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Hidden Print Template -->
    <PrintReceipt v-if="order" :order="order" :payments="payments" />
  </div>
</template>
