<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { cashRegisterApi } from '@/services/api/cashRegister'
import type { CashRegister, CashRegisterSummary } from '@/types/models'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
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
  DollarSign,
  TrendingUp,
  TrendingDown,
  Wallet,
  CreditCard,
  Lock,
  Unlock,
  ArrowUpCircle,
  ArrowDownCircle,
} from 'lucide-vue-next'

// State
const cashRegister = ref<CashRegister | null>(null)
const isLoading = ref(true)
const isProcessing = ref(false)

// Open cash register dialog
const showOpenDialog = ref(false)
const initialAmount = ref<string>('100.00')

// Close cash register dialog
const showCloseDialog = ref(false)
const declaredCash = ref<string>('0.00')
const declaredCard = ref<string>('0.00')
const closeSummary = ref<CashRegisterSummary | null>(null)
const showSummaryDialog = ref(false)

// Insert/Extract money dialog
const showMoneyDialog = ref(false)
const moneyOperation = ref<'insert' | 'extract'>('insert')
const moneyAmount = ref<string>('0.00')

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

// Computed
const sessionDuration = computed(() => {
  if (!cashRegister.value) return '0h 0m'

  const start = new Date(cashRegister.value.start_time)
  const now = new Date()
  const diff = now.getTime() - start.getTime()

  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  return `${hours}h ${minutes}m`
})

const totalOperations = computed(() => {
  if (!cashRegister.value) return 0
  return (
    Number(cashRegister.value.operations_cash || 0) +
    Number(cashRegister.value.operations_card || 0) +
    Number(cashRegister.value.operations_transfer || 0) +
    Number(cashRegister.value.operations_other || 0) +
    Number(cashRegister.value.operations_check || 0)
  )
})

const expectedCashAmount = computed(() => {
  if (!cashRegister.value) return 0
  return (
    Number(cashRegister.value.initial_amount || 0) +
    Number(cashRegister.value.operations_cash || 0)
  )
})

// Fetch current cash register status
async function fetchCashRegister() {
  isLoading.value = true
  try {
    cashRegister.value = await cashRegisterApi.getOpenRegister()
  } catch (error: any) {
    showToast(error.message || 'Erro ao carregar caixa', 'error')
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

  isProcessing.value = true
  try {
    cashRegister.value = await cashRegisterApi.start({ initial_amount: amount })
    showOpenDialog.value = false
    showToast('Caixa aberta com sucesso!', 'success')
    initialAmount.value = '100.00' // Reset
  } catch (error: any) {
    showToast(error.response?.data?.error || error.message || 'Erro ao abrir caixa', 'error')
  } finally {
    isProcessing.value = false
  }
}

// Close cash register
async function closeCashRegister() {
  console.log('closeCashRegister called with:', {
    declaredCash: declaredCash.value,
    declaredCard: declaredCard.value
  })

  const cash = parseFloat(declaredCash.value)
  const card = parseFloat(declaredCard.value)

  if (isNaN(cash) || isNaN(card) || cash < 0 || card < 0) {
    console.error('Invalid values:', { cash, card })
    showToast('Por favor insira valores válidos', 'error')
    return
  }

  console.log('Closing cash register with:', { cash, card })
  isProcessing.value = true
  try {
    closeSummary.value = await cashRegisterApi.close({
      declared_cash: cash,
      declared_card: card,
    })

    cashRegister.value = null
    showCloseDialog.value = false
    showSummaryDialog.value = true // Show summary dialog
    showToast('Caixa fechada com sucesso!', 'success')

    // Reset form
    declaredCash.value = '0.00'
    declaredCard.value = '0.00'
  } catch (error: any) {
    showToast(error.response?.data?.error || error.message || 'Erro ao fechar caixa', 'error')
  } finally {
    isProcessing.value = false
  }
}

// Insert money
async function insertMoney() {
  const amount = parseFloat(moneyAmount.value)
  if (isNaN(amount) || amount <= 0) {
    showToast('Por favor insira um valor válido', 'error')
    return
  }

  isProcessing.value = true
  try {
    await cashRegisterApi.insertMoney({ amount })
    showMoneyDialog.value = false
    moneyAmount.value = '0.00'
    showToast('Dinheiro inserido com sucesso!', 'success')
    await fetchCashRegister() // Reload
  } catch (error: any) {
    showToast(error.response?.data?.error || error.message || 'Erro ao inserir dinheiro', 'error')
  } finally {
    isProcessing.value = false
  }
}

// Extract money
async function extractMoney() {
  const amount = parseFloat(moneyAmount.value)
  if (isNaN(amount) || amount <= 0) {
    showToast('Por favor insira um valor válido', 'error')
    return
  }

  isProcessing.value = true
  try {
    await cashRegisterApi.extractMoney({ amount })
    showMoneyDialog.value = false
    moneyAmount.value = '0.00'
    showToast('Dinheiro retirado com sucesso!', 'success')
    await fetchCashRegister() // Reload
  } catch (error: any) {
    showToast(error.response?.data?.error || error.message || 'Erro ao retirar dinheiro', 'error')
  } finally {
    isProcessing.value = false
  }
}

// Open money dialog
function openMoneyDialog(operation: 'insert' | 'extract') {
  moneyOperation.value = operation
  moneyAmount.value = '0.00'
  showMoneyDialog.value = true
}

// Handle money dialog submit
function handleMoneySubmit() {
  if (moneyOperation.value === 'insert') {
    insertMoney()
  } else {
    extractMoney()
  }
}

// Pre-fill close dialog with expected values
function openCloseDialog() {
  if (!cashRegister.value) {
    showToast('Nenhuma caixa aberta encontrada', 'error')
    return
  }

  declaredCash.value = expectedCashAmount.value.toFixed(2)
  declaredCard.value = Number(cashRegister.value?.operations_card || 0).toFixed(2)
  showCloseDialog.value = true

  console.log('Opening close dialog with values:', {
    declaredCash: declaredCash.value,
    declaredCard: declaredCard.value
  })
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
  fetchCashRegister()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold">Caixa Registadora</h1>
      <Badge v-if="cashRegister" variant="default" class="text-sm">
        <Unlock class="mr-1 h-4 w-4" />
        Caixa Aberta
      </Badge>
      <Badge v-else variant="secondary" class="text-sm">
        <Lock class="mr-1 h-4 w-4" />
        Caixa Fechada
      </Badge>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <p class="text-muted-foreground">A carregar...</p>
    </div>

    <!-- No Cash Register Open -->
    <div v-else-if="!cashRegister" class="flex-1 flex items-center justify-center">
      <Card class="w-full max-w-md">
        <CardHeader>
          <CardTitle>Abrir Caixa Registadora</CardTitle>
          <CardDescription>
            Comece uma nova sessão de caixa inserindo o valor inicial
          </CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="initial-amount">Valor Inicial (CVE)</Label>
            <Input
              id="initial-amount"
              v-model="initialAmount"
              type="number"
              step="0.01"
              min="0"
              placeholder="100.00"
            />
          </div>
        </CardContent>
        <CardFooter>
          <Button @click="openCashRegister" :disabled="isProcessing" class="w-full">
            <Unlock class="mr-2 h-4 w-4" />
            {{ isProcessing ? 'A abrir...' : 'Abrir Caixa' }}
          </Button>
        </CardFooter>
      </Card>
    </div>

    <!-- Cash Register Open - Dashboard -->
    <div v-else class="flex-1 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <!-- Session Info -->
      <Card>
        <CardHeader>
          <CardTitle class="text-lg">Informações da Sessão</CardTitle>
        </CardHeader>
        <CardContent class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-sm text-muted-foreground">Início:</span>
            <span class="text-sm font-medium">{{ formatDateTime(cashRegister.start_time) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-muted-foreground">Duração:</span>
            <span class="text-sm font-medium">{{ sessionDuration }}</span>
          </div>
          <Separator />
          <div class="flex justify-between items-center">
            <span class="text-sm text-muted-foreground">Valor Inicial:</span>
            <span class="text-lg font-bold">CVE{{ Number(cashRegister.initial_amount).toFixed(2) }}</span>
          </div>
        </CardContent>
      </Card>

      <!-- Operations Summary -->
      <Card>
        <CardHeader>
          <CardTitle class="text-lg">Operações</CardTitle>
        </CardHeader>
        <CardContent class="space-y-3">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <Wallet class="h-4 w-4 text-green-600" />
              <span class="text-sm text-muted-foreground">Dinheiro:</span>
            </div>
            <span class="text-sm font-medium">CVE{{ Number(cashRegister.operations_cash || 0).toFixed(2) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <CreditCard class="h-4 w-4 text-blue-600" />
              <span class="text-sm text-muted-foreground">Cartão:</span>
            </div>
            <span class="text-sm font-medium">CVE{{ Number(cashRegister.operations_card || 0).toFixed(2) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <DollarSign class="h-4 w-4 text-purple-600" />
              <span class="text-sm text-muted-foreground">Outros:</span>
            </div>
            <span class="text-sm font-medium">CVE{{ Number(cashRegister.operations_other || 0).toFixed(2) }}</span>
          </div>
          <Separator />
          <div class="flex justify-between items-center">
            <span class="text-sm font-semibold">Total Operações:</span>
            <span class="text-lg font-bold text-primary">CVE{{ totalOperations.toFixed(2) }}</span>
          </div>
        </CardContent>
      </Card>

      <!-- Expected Cash -->
      <Card>
        <CardHeader>
          <CardTitle class="text-lg">Dinheiro Esperado</CardTitle>
        </CardHeader>
        <CardContent class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-sm text-muted-foreground">Inicial:</span>
            <span class="text-sm font-medium">CVE{{ Number(cashRegister.initial_amount).toFixed(2) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-muted-foreground">+ Operações:</span>
            <span class="text-sm font-medium">CVE{{ Number(cashRegister.operations_cash || 0).toFixed(2) }}</span>
          </div>
          <Separator />
          <div class="flex justify-between items-center">
            <span class="text-sm font-semibold">Total Esperado:</span>
            <span class="text-2xl font-bold text-green-600">CVE{{ expectedCashAmount.toFixed(2) }}</span>
          </div>
        </CardContent>
      </Card>

      <!-- Actions Card -->
      <Card class="md:col-span-2 lg:col-span-3">
        <CardHeader>
          <CardTitle class="text-lg">Ações</CardTitle>
          <CardDescription>Gerir a caixa registadora</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="flex flex-wrap gap-3">
            <Button @click="openMoneyDialog('insert')" variant="outline">
              <ArrowDownCircle class="mr-2 h-4 w-4 text-green-600" />
              Inserir Dinheiro
            </Button>
            <Button @click="openMoneyDialog('extract')" variant="outline">
              <ArrowUpCircle class="mr-2 h-4 w-4 text-orange-600" />
              Retirar Dinheiro
            </Button>
            <Button @click="openCloseDialog" variant="destructive">
              <Lock class="mr-2 h-4 w-4" />
              Fechar Caixa
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Insert/Extract Money Dialog -->
    <Dialog v-model:open="showMoneyDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {{ moneyOperation === 'insert' ? 'Inserir Dinheiro' : 'Retirar Dinheiro' }}
          </DialogTitle>
          <DialogDescription>
            {{ moneyOperation === 'insert'
              ? 'Adicionar dinheiro à caixa registadora'
              : 'Retirar dinheiro da caixa registadora'
            }}
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="money-amount">Valor (CVE)</Label>
            <Input
              id="money-amount"
              v-model="moneyAmount"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showMoneyDialog = false">
            Cancelar
          </Button>
          <Button @click="handleMoneySubmit" :disabled="isProcessing">
            {{ isProcessing ? 'A processar...' : 'Confirmar' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Close Cash Register Dialog -->
    <Dialog v-model:open="showCloseDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Fechar Caixa Registadora</DialogTitle>
          <DialogDescription>
            Conte o dinheiro e cartões e insira os valores declarados
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="declared-cash">Dinheiro Contado (CVE)</Label>
            <Input
              id="declared-cash"
              v-model="declaredCash"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
            />
            <p class="text-xs text-muted-foreground">
              Esperado: CVE{{ expectedCashAmount.toFixed(2) }}
            </p>
          </div>
          <div class="space-y-2">
            <Label for="declared-card">Cartões Contados (CVE)</Label>
            <Input
              id="declared-card"
              v-model="declaredCard"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
            />
            <p class="text-xs text-muted-foreground">
              Esperado: CVE{{ Number(cashRegister?.operations_card || 0).toFixed(2) }}
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showCloseDialog = false">
            Cancelar
          </Button>
          <Button variant="destructive" @click="closeCashRegister" :disabled="isProcessing">
            {{ isProcessing ? 'A fechar...' : 'Fechar Caixa' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Close Summary Dialog -->
    <Dialog v-model:open="showSummaryDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Resumo do Fecho</DialogTitle>
          <DialogDescription>
            Caixa fechada com sucesso
          </DialogDescription>
        </DialogHeader>
        <div v-if="closeSummary" class="space-y-4 py-4">
          <div class="space-y-3">
            <h3 class="font-semibold">Dinheiro</h3>
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">Esperado:</span>
              <span>CVE{{ Number(closeSummary.expected_cash || 0).toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">Declarado:</span>
              <span>CVE{{ Number(closeSummary.declared_cash || 0).toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-sm font-semibold">
              <span>Diferença:</span>
              <span :class="Number(closeSummary.cash_difference || 0) >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ Number(closeSummary.cash_difference || 0) >= 0 ? '+' : '' }}CVE{{ Number(closeSummary.cash_difference || 0).toFixed(2) }}
              </span>
            </div>
          </div>
          <Separator />
          <div class="space-y-3">
            <h3 class="font-semibold">Cartão</h3>
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">Esperado:</span>
              <span>CVE{{ Number(closeSummary.expected_card || 0).toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">Declarado:</span>
              <span>CVE{{ Number(closeSummary.declared_card || 0).toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-sm font-semibold">
              <span>Diferença:</span>
              <span :class="Number(closeSummary.card_difference || 0) >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ Number(closeSummary.card_difference || 0) >= 0 ? '+' : '' }}CVE{{ Number(closeSummary.card_difference || 0).toFixed(2) }}
              </span>
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button @click="showSummaryDialog = false; closeSummary = null">
            Fechar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

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
