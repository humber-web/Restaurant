<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ordersApi, cashRegisterApi, menuApi, type Order, type MenuItem } from '@/services/api'
import { paymentsApi, type ProcessPaymentPayload } from '@/services/api/payments'
import type { CashRegister } from '@/services/api/cashRegister'
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
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

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
const isLoading = ref(true)

// Payment state
const paymentMethod = ref<'CASH' | 'CREDIT_CARD' | 'DEBIT_CARD' | 'ONLINE'>('CASH')
const paymentAmount = ref<string>('')
const isProcessingPayment = ref(false)
const paymentSuccess = ref(false)
const changeDue = ref<number>(0)

// Cash register dialog
const showCashRegisterDialog = ref(false)
const initialAmount = ref<string>('100.00')
const isOpeningRegister = ref(false)

// Computed: Order totals
const orderTotals = computed(() => {
  if (!order.value) {
    return {
      totalAmount: 0,
      totalIva: 0,
      grandTotal: 0,
    }
  }
  return {
    totalAmount: Number(order.value.totalAmount || 0),
    totalIva: Number(order.value.totalIva || 0),
    grandTotal: Number(order.value.grandTotal || 0),
  }
})

// Computed: Validation (now allows partial payments)
const isAmountValid = computed(() => {
  const amount = parseFloat(paymentAmount.value)
  return !isNaN(amount) && amount > 0
})

// Computed: Payment status based on amount
const paymentStatus = computed(() => {
  const amount = parseFloat(paymentAmount.value) || 0
  if (amount >= orderTotals.value.grandTotal) return 'full'
  if (amount > 0) return 'partial'
  return 'invalid'
})

// Computed: Real-time change
const calculatedChange = computed(() => {
  if (paymentMethod.value !== 'CASH') return 0
  const amount = parseFloat(paymentAmount.value) || 0
  return Math.max(0, amount - orderTotals.value.grandTotal)
})

// Get item name
function getItemName(menuItemId: number): string {
  const item = menuItems.value.find(m => m.itemID === menuItemId)
  return item?.name || 'Item'
}

// Numeric keypad
function appendNumber(num: string) {
  // If starts with "0." keep the decimal structure, otherwise replace leading zero
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
  const amount = (orderTotals.value.grandTotal * percentage).toFixed(2)
  paymentAmount.value = amount
}

function setExactAmount() {
  paymentAmount.value = orderTotals.value.grandTotal.toFixed(2)
}

// Fetch data
async function fetchData() {
  isLoading.value = true
  try {
    const [orderData, register, items] = await Promise.all([
      ordersApi.getOrder(orderID.value),
      cashRegisterApi.getOpenRegister(),
      menuApi.getItems()
    ])

    order.value = orderData
    cashRegister.value = register
    menuItems.value = items

    // Pre-fill payment amount with order total
    paymentAmount.value = orderTotals.value.grandTotal.toFixed(2)

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

  const amount = parseFloat(paymentAmount.value)
  if (isNaN(amount) || amount <= 0) {
    showToast('Por favor insira um valor válido', 'error')
    return
  }

  // Warn for partial payment
  if (amount < orderTotals.value.grandTotal) {
    const remaining = orderTotals.value.grandTotal - amount
    if (!confirm(`Pagamento parcial de €${amount.toFixed(2)}. Faltam €${remaining.toFixed(2)}. Continuar?`)) {
      return
    }
  }

  isProcessingPayment.value = true

  try {
    const payload: ProcessPaymentPayload = {
      orderID: order.value.orderID,
      amount: amount,
      payment_method: paymentMethod.value
    }

    const response = await paymentsApi.processPayment(payload)

    // Show success screen
    paymentSuccess.value = true
    changeDue.value = parseFloat(response.change_due)

    // Auto-redirect after 3 seconds
    setTimeout(() => {
      router.push('/pagamentos')
    }, 3000)
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
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="icon" @click="cancelPayment" :disabled="paymentSuccess">
        <ArrowLeft class="h-5 w-5" />
      </Button>
      <div>
        <h1 class="text-3xl font-bold">Processar Pagamento</h1>
        <p class="text-sm text-muted-foreground">Pedido #{{ orderID }}</p>
      </div>
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
                <span class="font-semibold">€{{ parseFloat(paymentAmount).toFixed(2) }}</span>
              </div>
              <div v-if="paymentMethod === 'CASH' && changeDue > 0" class="flex justify-between text-lg">
                <span class="font-medium">Troco:</span>
                <span class="font-bold text-green-600">€{{ changeDue.toFixed(2) }}</span>
              </div>
            </div>

            <p class="text-sm text-muted-foreground">
              A redirecionar para pagamentos em 3 segundos...
            </p>
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
            <CardTitle>Resumo do Pedido</CardTitle>
          </CardHeader>
          <CardContent>
            <div v-if="order" class="space-y-4">
              <!-- Order Details -->
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

              <!-- Items List -->
              <div class="space-y-2">
                <h3 class="font-semibold text-sm">Itens do Pedido:</h3>
                <div class="space-y-2 max-h-48 overflow-y-auto">
                  <div
                    v-for="item in order.items"
                    :key="item.menu_item"
                    class="flex justify-between items-center text-sm py-1"
                  >
                    <div class="flex-1">
                      <span class="font-medium">{{ getItemName(item.menu_item) }}</span>
                      <span class="text-muted-foreground ml-2">x{{ item.quantity }}</span>
                    </div>
                    <span class="font-semibold">€{{ (Number(item.price) * item.quantity).toFixed(2) }}</span>
                  </div>
                </div>
              </div>

              <Separator />

              <!-- Pricing -->
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-muted-foreground">Subtotal:</span>
                  <span>€{{ orderTotals.totalAmount.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-muted-foreground">IVA (15%):</span>
                  <span>€{{ orderTotals.totalIva.toFixed(2) }}</span>
                </div>
                <Separator />
                <div class="flex justify-between text-xl font-bold">
                  <span>Total a Pagar:</span>
                  <span class="text-primary">€{{ orderTotals.grandTotal.toFixed(2) }}</span>
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
                <span class="font-semibold">€{{ Number(cashRegister.initial_amount).toFixed(2) }}</span>
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
                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-2xl text-muted-foreground">€</span>
                <Input
                  v-model="paymentAmount"
                  type="text"
                  readonly
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
                  Pagamento Parcial: Faltam €{{ (orderTotals.grandTotal - parseFloat(paymentAmount || '0')).toFixed(2) }}
                </Badge>
              </div>
            </div>

            <!-- Numeric Keypad -->
            <div class="grid grid-cols-3 gap-2">
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

            <!-- Clear Button -->
            <Button variant="outline" class="w-full" @click="clearAmount()">Limpar</Button>

            <!-- Change Display (Cash Only) -->
            <div
              v-if="paymentMethod === 'CASH' && calculatedChange > 0"
              class="bg-green-50 dark:bg-green-950 border-2 border-green-500 rounded-lg p-4"
            >
              <div class="flex justify-between items-center">
                <span class="text-lg font-semibold text-green-900 dark:text-green-200">Troco:</span>
                <span class="text-3xl font-bold text-green-700 dark:text-green-300">
                  €{{ calculatedChange.toFixed(2) }}
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
                :disabled="!isAmountValid || isProcessingPayment || !cashRegister"
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
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">€</span>
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
  </div>
</template>
