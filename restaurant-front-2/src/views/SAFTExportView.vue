<script setup lang="ts">
import { ref, computed } from 'vue'
import { paymentsApi } from '@/services/api/payments'
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
  FileArchive,
  Download,
  AlertCircle,
  CheckCircle2,
  Calendar,
  FileText,
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
const startDate = ref('')
const endDate = ref('')
const isExporting = ref(false)

// Set default dates (current month)
const today = new Date()
const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)

startDate.value = firstDayOfMonth.toISOString().split('T')[0]
endDate.value = lastDayOfMonth.toISOString().split('T')[0]

// Validation
const isValidDateRange = computed(() => {
  if (!startDate.value || !endDate.value) return false
  return new Date(startDate.value) <= new Date(endDate.value)
})

// Export SAF-T
async function exportSAFT() {
  if (!isValidDateRange.value) {
    showToast('Período inválido. Data início deve ser anterior à data fim.', 'error')
    return
  }

  try {
    isExporting.value = true

    // Call API to export SAF-T
    const response = await paymentsApi.exportSAFT(startDate.value, endDate.value)

    // Create blob from response
    const blob = new Blob([response.data], { type: 'application/xml' })
    const url = window.URL.createObjectURL(blob)
    
    // Create download link
    const link = document.createElement('a')
    link.href = url
    const filename = `SAFT-CV_${startDate.value}_${endDate.value}.xml`
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    showToast(`SAF-T CV exportado com sucesso: ${filename}`, 'success')
  } catch (error: any) {
    showToast(
      error.response?.data?.error || 'Erro ao exportar SAF-T CV',
      'error'
    )
  } finally {
    isExporting.value = false
  }
}

// Quick date presets
function setCurrentMonth() {
  const today = new Date()
  const first = new Date(today.getFullYear(), today.getMonth(), 1)
  const last = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  startDate.value = first.toISOString().split('T')[0]
  endDate.value = last.toISOString().split('T')[0]
}

function setLastMonth() {
  const today = new Date()
  const first = new Date(today.getFullYear(), today.getMonth() - 1, 1)
  const last = new Date(today.getFullYear(), today.getMonth(), 0)
  startDate.value = first.toISOString().split('T')[0]
  endDate.value = last.toISOString().split('T')[0]
}

function setCurrentYear() {
  const today = new Date()
  const first = new Date(today.getFullYear(), 0, 1)
  const last = new Date(today.getFullYear(), 11, 31)
  startDate.value = first.toISOString().split('T')[0]
  endDate.value = last.toISOString().split('T')[0]
}

function setLastYear() {
  const today = new Date()
  const first = new Date(today.getFullYear() - 1, 0, 1)
  const last = new Date(today.getFullYear() - 1, 11, 31)
  startDate.value = first.toISOString().split('T')[0]
  endDate.value = last.toISOString().split('T')[0]
}
</script>

<template>
  <div class="flex h-full flex-col gap-6 p-6">
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
      <h1 class="text-3xl font-bold flex items-center gap-3">
        <FileArchive class="h-8 w-8" />
        Exportação SAF-T CV
      </h1>
      <p class="text-sm text-muted-foreground mt-2">
        Standard Audit File for Tax - Cabo Verde (Portaria n.º 47/2021)
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Export Form -->
      <Card class="lg:col-span-2">
        <CardHeader>
          <CardTitle>Gerar Ficheiro SAF-T CV</CardTitle>
          <CardDescription>
            Selecione o período fiscal para exportação
          </CardDescription>
        </CardHeader>
        <CardContent class="space-y-6">
          <!-- Date Range -->
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="start-date">Data Início *</Label>
              <Input
                id="start-date"
                v-model="startDate"
                type="date"
              />
            </div>
            <div class="space-y-2">
              <Label for="end-date">Data Fim *</Label>
              <Input
                id="end-date"
                v-model="endDate"
                type="date"
              />
            </div>
          </div>

          <!-- Quick Presets -->
          <div class="space-y-2">
            <Label>Períodos Rápidos</Label>
            <div class="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                @click="setCurrentMonth"
              >
                <Calendar class="mr-2 h-4 w-4" />
                Mês Atual
              </Button>
              <Button
                variant="outline"
                size="sm"
                @click="setLastMonth"
              >
                Mês Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                @click="setCurrentYear"
              >
                Ano Atual
              </Button>
              <Button
                variant="outline"
                size="sm"
                @click="setLastYear"
              >
                Ano Anterior
              </Button>
            </div>
          </div>

          <!-- Validation Warning -->
          <div
            v-if="!isValidDateRange"
            class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start gap-3"
          >
            <AlertCircle class="h-5 w-5 text-yellow-600 mt-0.5" />
            <div class="text-sm text-yellow-900">
              <strong>Atenção:</strong> A data de início deve ser anterior à data de fim.
            </div>
          </div>

          <!-- Export Button -->
          <Button
            class="w-full"
            size="lg"
            @click="exportSAFT"
            :disabled="!isValidDateRange || isExporting"
          >
            <Download class="mr-2 h-5 w-5" />
            {{ isExporting ? 'A exportar...' : 'Exportar SAF-T CV (XML)' }}
          </Button>
        </CardContent>
      </Card>

      <!-- Info Card -->
      <div class="space-y-6">
        <!-- What is SAF-T CV -->
        <Card>
          <CardHeader>
            <CardTitle class="text-lg">O que é o SAF-T CV?</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3 text-sm">
            <p class="text-muted-foreground">
              O SAF-T CV (Standard Audit File for Tax - Cabo Verde) é o formato oficial
              para exportação de dados fiscais exigido pela DNRE.
            </p>
            <div class="space-y-2">
              <div class="flex items-start gap-2">
                <CheckCircle2 class="h-4 w-4 text-green-600 mt-0.5" />
                <span>Clientes e Fornecedores</span>
              </div>
              <div class="flex items-start gap-2">
                <CheckCircle2 class="h-4 w-4 text-green-600 mt-0.5" />
                <span>Produtos e Serviços</span>
              </div>
              <div class="flex items-start gap-2">
                <CheckCircle2 class="h-4 w-4 text-green-600 mt-0.5" />
                <span>Faturas e Notas de Crédito</span>
              </div>
              <div class="flex items-start gap-2">
                <CheckCircle2 class="h-4 w-4 text-green-600 mt-0.5" />
                <span>Hash Chain de Integridade</span>
              </div>
              <div class="flex items-start gap-2">
                <CheckCircle2 class="h-4 w-4 text-green-600 mt-0.5" />
                <span>Métodos de Pagamento</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Requirements -->
        <Card>
          <CardHeader>
            <CardTitle class="text-lg">Requisitos</CardTitle>
          </CardHeader>
          <CardContent class="space-y-2 text-sm">
            <div class="flex items-start gap-2">
              <FileText class="h-4 w-4 text-blue-600 mt-0.5" />
              <div>
                <p class="font-medium">Formato</p>
                <p class="text-muted-foreground">XML conforme XSD oficial</p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <FileText class="h-4 w-4 text-blue-600 mt-0.5" />
              <div>
                <p class="font-medium">Versão</p>
                <p class="text-muted-foreground">SAF-T PT 1.04_01</p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <FileText class="h-4 w-4 text-blue-600 mt-0.5" />
              <div>
                <p class="font-medium">Submissão</p>
                <p class="text-muted-foreground">Portal da DNRE</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
