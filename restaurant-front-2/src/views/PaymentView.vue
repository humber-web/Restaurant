<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ordersApi } from '@/services/api'
import { paymentsApi, type ProcessPaymentPayload } from '@/services/api/payments'
import { cashRegisterApi } from '@/services/api/cashRegister'
import type { Order, CashRegister } from '@/types/models'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import {
  ArrowLeft,
  CreditCard,
  DollarSign,
  CheckCircle2,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// State
const orderID = computed(() => Number(route.query.order))
const order = ref<Order | null>(null)
const cashRegister = ref<CashRegister | null>(null)
const isLoading = ref(false)
const isProcessingPayment = ref(false)

// Cash register dialog
const showCashRegisterDialog = ref(false)
const initialAmount = ref('100.00')
const isOpeningRegister = ref(false)

// Payment state
const paymentMethod = ref<'CASH' | 'CREDIT_CARD' | 'DEBIT_CARD' | 'ONLINE'>('CASH')
const paymentAmount = ref('')
const paymentSuccess = ref(false)
const changeDue = ref(0)

// Toast
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

// Computed
const orderTotals = computed(() => {
  if (!order.value) {
    return { totalAmount: 0, totalIva: 0, grandTotal: 0 }
  }
  return {
    totalAmount: Number(order.value.totalAmount || 0),
    totalIva: Number(order.value.totalIva || 0),
    grandTotal: Number(order.value.grandTotal || 0),
  }
})

const computedChangeDue = computed(() => {
  if (!paymentAmount.value) return 0
  const amount = parseFloat(paymentAmount.value) || 0
  return Math.max(0, amount - orderTotals.value.grandTotal)
})

const canProcessPayment = computed(() => {
  const amount = parseFloat(paymentAmount.value) || 0
  return amount >= orderTotals.value.grandTotal && !isProcessingPayment.value && cashRegister.value !== null
})

// Methods
function showToast(message: string, variant: 'success' | 'error' = 'success') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

async function fetchData() {
  isLoading.value = true
  try {
    const [orderData, register] = await Promise.all([
      ordersApi.getOrder(orderID.value),
      cashRegisterApi.getOpenRegister()
    ])

    order.value = orderData
    cashRegister.value = register

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

async function processPayment() {
  if (!order.value || !cashRegister.value) return

  const amount = parseFloat(paymentAmount.value)
  if (isNaN(amount) || amount < orderTotals.value.grandTotal) {
    showToast('Valor insuficiente', 'error')
    return
  }

  isProcessingPayment.value = true

  try {
    const payload: ProcessPaymentPayload = {
      orderID: order.value.orderID,
      amount: amount,
      payment_method: paymentMethod.value
    }

    const response = await paymentsApi.processPayment(payload)

    changeDue.value = parseFloat(response.change_due)
    paymentSuccess.value = true

    // Navigate back after showing success
    setTimeout(() => {
      router.push('/mesas')
    }, 3000)
  } catch (error: any) {
    const errorMessage = error.response?.data?.error || error.message || 'Erro ao processar pagamento'
    showToast(errorMessage, 'error')
  } finally {
    isProcessingPayment.value = false
  }
}

function goBack() {
  router.back()
}

// Lifecycle
onMounted(() => {
  if (!orderID.value) {
    showToast('Pedido não especificado', 'error')
    router.push('/mesas')
    return
  }
  fetchData()
})
</script>

<template>
  <div class="flex flex-col h-full bg-background">
    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      class="fixed top-4 right-4 z-50 rounded-lg border px-4 py-3 shadow-lg transition-all"
      :class="toastVariant === 'success' ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'"
    >
      {{ toastMessage }}
    </div>

    <!-- Header -->
    <div class="border-b bg-card px-6 py-4">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" @click="goBack" :disabled="paymentSuccess">
          <ArrowLeft class="h-5 w-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold">Processar Pagamento</h1>
          <p class="text-sm text-muted-foreground">Pedido #{{ orderID }}</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex-1 flex items-center justify-center p-6">
      <div class="space-y-4 w-full max-w-4xl">
        <Skeleton class="h-96 w-full" />
      </div>
    </div>

    <!-- Success State -->
    <div v-else-if="paymentSuccess" class="flex-1 flex items-center justify-center p-6">
      <Card class="max-w-md w-full text-center">
        <CardContent class="pt-12 pb-12">
          <CheckCircle2 class="h-24 w-24 text-green-500 mx-auto mb-6" />
          <h2 class="text-3xl font-bold mb-4">Pagamento Concluído!</h2>
          <div class="space-y-4 text-lg">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Total Pago:</span>
              <span class="font-bold">€{{ parseFloat(paymentAmount).toFixed(2) }}</span>
            </div>
            <div v-if="changeDue > 0 && paymentMethod === 'CASH'" class="flex justify-between text-green-600">
              <span class="font-semibold">Troco:</span>
              <span class="font-bold text-2xl">€{{ changeDue.toFixed(2) }}</span>
            </div>
          </div>
          <Separator class="my-6" />
          <p class="text-muted-foreground">Redirecionando...</p>
        </CardContent>
      </Card>
    </div>

    <!-- Main Payment Interface -->
    <div v-else-if="order" class="flex-1 flex gap-6 p-6 overflow-hidden">
      <!-- Left Column: Order Summary -->
      <div class="w-1/2 space-y-4 overflow-y-auto">
        <Card>
          <CardHeader>
            <CardTitle>Resumo do Pedido</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <!-- Order Items -->
            <div class="space-y-3 max-h-64 overflow-y-auto">
              <div v-for="item in order.items" :key="item.menu_item" class="flex justify-between text-sm">
                <div class="flex-1">
                  <span class="font-medium">{{ item.quantity }}x</span>
                  <span class="ml-2">Item #{{ item.menu_item }}</span>
                </div>
                <span class="font-semibold">€{{ (Number(item.price) * item.quantity).toFixed(2) }}</span>
              </div>
            </div>

            <Separator />

            <!-- Totals -->
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
                <span>Total:</span>
                <span class="text-primary">€{{ orderTotals.grandTotal.toFixed(2) }}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Cash Register Info -->
        <Card v-if="cashRegister">
          <CardHeader>
            <CardTitle class="text-base">Informações da Caixa</CardTitle>
          </CardHeader>
          <CardContent class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-muted-foreground">Valor Inicial:</span>
              <span>€{{ Number(cashRegister.initial_amount).toFixed(2) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Status:</span>
              <Badge variant="default">Aberta</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Right Column: Payment Input -->
      <div class="w-1/2 flex flex-col">
        <Card class="flex-1 flex flex-col">
          <CardHeader>
            <CardTitle>Pagamento</CardTitle>
          </CardHeader>
          <CardContent class="flex-1 flex flex-col space-y-6">
            <!-- Payment Method Selection -->
            <div class="space-y-3">
              <Label class="text-base">Método de Pagamento</Label>
              <div class="grid grid-cols-2 gap-3">
                <Button
                  :variant="paymentMethod === 'CASH' ? 'default' : 'outline'"
                  class="h-20 text-lg"
                  @click="paymentMethod = 'CASH'"
                >
                  💵<br/>Dinheiro
                </Button>
                <Button
                  :variant="paymentMethod === 'CREDIT_CARD' ? 'default' : 'outline'"
                  class="h-20 text-lg"
                  @click="paymentMethod = 'CREDIT_CARD'"
                >
                  💳<br/>Crédito
                </Button>
                <Button
                  :variant="paymentMethod === 'DEBIT_CARD' ? 'default' : 'outline'"
                  class="h-20 text-lg"
                  @click="paymentMethod = 'DEBIT_CARD'"
                >
                  💳<br/>Débito
                </Button>
                <Button
                  :variant="paymentMethod === 'ONLINE' ? 'default' : 'outline'"
                  class="h-20 text-lg"
                  @click="paymentMethod = 'ONLINE'"
                >
                  🌐<br/>Online
                </Button>
              </div>
            </div>

            <!-- Amount Display -->
            <div class="space-y-3 flex-1 flex flex-col justify-center">
              <Label class="text-base">Valor Recebido</Label>
              <div class="relative">
                <span class="absolute left-6 top-1/2 -translate-y-1/2 text-3xl text-muted-foreground">€</span>
                <Input
                  v-model="paymentAmount"
                  type="number"
                  step="0.01"
                  min="0"
                  class="text-5xl font-bold h-24 pl-16 text-center"
                  :class="{ 'border-red-500 border-2': parseFloat(paymentAmount) < orderTotals.grandTotal }"
                />
              </div>
              <p v-if="parseFloat(paymentAmount) < orderTotals.grandTotal" class="text-sm text-red-500 text-center">
                ⚠️ Valor insuficiente - Faltam €{{ (orderTotals.grandTotal - parseFloat(paymentAmount)).toFixed(2) }}
              </p>
            </div>

            <!-- Change Due -->
            <div v-if="paymentMethod === 'CASH' && computedChangeDue > 0" class="bg-green-50 dark:bg-green-950 border-2 border-green-500 rounded-lg p-6">
              <div class="text-center">
                <p class="text-sm font-medium text-green-900 dark:text-green-200 mb-2">Troco</p>
                <p class="text-5xl font-bold text-green-700 dark:text-green-300">€{{ computedChangeDue.toFixed(2) }}</p>
              </div>
            </div>

            <!-- Process Button -->
            <Button
              size="lg"
              class="w-full h-16 text-xl"
              :disabled="!canProcessPayment"
              @click="processPayment"
            >
              <CreditCard v-if="!isProcessingPayment" class="mr-2 h-6 w-6" />
              <span v-if="isProcessingPayment">Processando...</span>
              <span v-else>Confirmar Pagamento €{{ orderTotals.grandTotal.toFixed(2) }}</span>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Open Cash Register Dialog -->
    <Dialog v-model:open="showCashRegisterDialog" :closeOnEscape="false" :closeOnOutsideClick="false">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Abrir Caixa</DialogTitle>
          <DialogDescription>
            É necessário abrir uma caixa antes de processar pagamentos.
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
                class="pl-8 text-lg"
              />
            </div>
            <p class="text-xs text-muted-foreground">
              Este é o valor em dinheiro com que você está iniciando o caixa.
            </p>
          </div>
        </div>

        <DialogFooter class="flex-col gap-2">
          <Button
            class="w-full"
            @click="openCashRegister"
            :disabled="isOpeningRegister"
          >
            <DollarSign v-if="!isOpeningRegister" class="mr-2 h-4 w-4" />
            <span v-if="isOpeningRegister">Abrindo...</span>
            <span v-else>Abrir Caixa</span>
          </Button>
          <Button
            variant="outline"
            class="w-full"
            @click="goBack"
            :disabled="isOpeningRegister"
          >
            Cancelar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
