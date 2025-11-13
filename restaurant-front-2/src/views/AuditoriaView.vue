<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { auditApi } from '@/services/api'
import type { OperationLog } from '@/types/models/audit'
import AuditTableAdvanced from '@/components/audit/AuditTableAdvanced.vue'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  RefreshCw,
  Filter,
  Activity,
  Plus,
  Edit,
  Trash2,
  Users,
  FileText,
} from 'lucide-vue-next'

// State
const logs = ref<OperationLog[]>([])
const isLoading = ref(true)

// Filters
const filterAction = ref<string>('ALL')
const filterModel = ref<string>('ALL')
const filterUser = ref<string>('')
const filterDateFrom = ref<string>('')
const filterDateTo = ref<string>('')

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

// Computed: Filtered logs
const filteredLogs = computed(() => {
  let result = logs.value

  // Filter by action
  if (filterAction.value !== 'ALL') {
    result = result.filter(log => log.action === filterAction.value)
  }

  // Filter by model
  if (filterModel.value !== 'ALL') {
    result = result.filter(log => log.model_name.toLowerCase() === filterModel.value.toLowerCase())
  }

  // Filter by user (username search)
  if (filterUser.value) {
    result = result.filter(log =>
      log.username.toLowerCase().includes(filterUser.value.toLowerCase()) ||
      log.user_email.toLowerCase().includes(filterUser.value.toLowerCase())
    )
  }

  // Filter by date range
  if (filterDateFrom.value) {
    const fromDate = new Date(filterDateFrom.value)
    fromDate.setHours(0, 0, 0, 0)
    result = result.filter(log => new Date(log.timestamp) >= fromDate)
  }

  if (filterDateTo.value) {
    const toDate = new Date(filterDateTo.value)
    toDate.setHours(23, 59, 59, 999)
    result = result.filter(log => new Date(log.timestamp) <= toDate)
  }

  return result
})

// Computed: Statistics
const statistics = computed(() => {
  const total = filteredLogs.value.length

  const byAction = {
    CREATE: filteredLogs.value.filter(log => log.action === 'CREATE').length,
    UPDATE: filteredLogs.value.filter(log => log.action === 'UPDATE').length,
    DELETE: filteredLogs.value.filter(log => log.action === 'DELETE').length,
  }

  // Count unique users
  const uniqueUsers = new Set(filteredLogs.value.map(log => log.user)).size

  // Count by model
  const modelCounts: Record<string, number> = {}
  filteredLogs.value.forEach(log => {
    const model = log.model_name.toLowerCase()
    modelCounts[model] = (modelCounts[model] || 0) + 1
  })

  // Get top 5 models
  const topModels = Object.entries(modelCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  // Recent activity (last 24 hours)
  const twentyFourHoursAgo = new Date()
  twentyFourHoursAgo.setHours(twentyFourHoursAgo.getHours() - 24)
  const recentActivity = filteredLogs.value.filter(
    log => new Date(log.timestamp) >= twentyFourHoursAgo
  ).length

  return {
    total,
    byAction,
    uniqueUsers,
    topModels,
    recentActivity,
  }
})

// Computed: Unique models for filter dropdown
const availableModels = computed(() => {
  const models = new Set(logs.value.map(log => log.model_name))
  return Array.from(models).sort()
})

// Fetch logs
async function fetchLogs() {
  try {
    isLoading.value = true
    logs.value = await auditApi.getOperationLogs()
    showToast('Registos carregados com sucesso')
  } catch (error) {
    console.error('Error fetching audit logs:', error)
    showToast('Erro ao carregar registos de auditoria', 'error')
  } finally {
    isLoading.value = false
  }
}

// Clear filters
function clearFilters() {
  filterAction.value = 'ALL'
  filterModel.value = 'ALL'
  filterUser.value = ''
  filterDateFrom.value = ''
  filterDateTo.value = ''
}

// Set default date range (last 7 days)
function setLast7Days() {
  const today = new Date()
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(today.getDate() - 7)

  filterDateFrom.value = sevenDaysAgo.toISOString().split('T')[0]
  filterDateTo.value = today.toISOString().split('T')[0]
}

// Set today
function setToday() {
  const today = new Date().toISOString().split('T')[0]
  filterDateFrom.value = today
  filterDateTo.value = today
}

onMounted(() => {
  fetchLogs()
})
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">Auditoria</h1>
        <p class="text-muted-foreground">Rastreamento de todas as operações do sistema</p>
      </div>
      <Button @click="fetchLogs" :disabled="isLoading">
        <RefreshCw :class="['mr-2 h-4 w-4', { 'animate-spin': isLoading }]" />
        Atualizar
      </Button>
    </div>

    <!-- Statistics Cards -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total de Registos</CardTitle>
          <Activity class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statistics.total }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Últimas 24h: {{ statistics.recentActivity }}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Criações</CardTitle>
          <Plus class="h-4 w-4 text-green-600" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-green-600">{{ statistics.byAction.CREATE }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Novos registos criados
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Atualizações</CardTitle>
          <Edit class="h-4 w-4 text-blue-600" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-blue-600">{{ statistics.byAction.UPDATE }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Registos modificados
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Eliminações</CardTitle>
          <Trash2 class="h-4 w-4 text-red-600" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-red-600">{{ statistics.byAction.DELETE }}</div>
          <p class="text-xs text-muted-foreground mt-1">
            Registos eliminados
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- Activity Insights -->
    <div class="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <div class="flex items-center gap-2">
            <Users class="h-5 w-5 text-muted-foreground" />
            <CardTitle class="text-lg">Atividade por Utilizador</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div class="flex items-center justify-between">
            <span class="text-sm text-muted-foreground">Utilizadores ativos</span>
            <span class="text-2xl font-bold">{{ statistics.uniqueUsers }}</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div class="flex items-center gap-2">
            <FileText class="h-5 w-5 text-muted-foreground" />
            <CardTitle class="text-lg">Modelos Mais Modificados</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div v-if="statistics.topModels.length > 0" class="space-y-2">
            <div
              v-for="[model, count] in statistics.topModels"
              :key="model"
              class="flex items-center justify-between text-sm"
            >
              <span class="font-medium capitalize">{{ model }}</span>
              <span class="text-muted-foreground">{{ count }} ops</span>
            </div>
          </div>
          <p v-else class="text-sm text-muted-foreground">Sem dados disponíveis</p>
        </CardContent>
      </Card>
    </div>

    <!-- Filters -->
    <Card>
      <CardHeader>
        <div class="flex items-center justify-between">
          <div>
            <CardTitle class="text-lg">Filtros</CardTitle>
            <CardDescription>Filtrar registos de auditoria</CardDescription>
          </div>
          <div class="flex gap-2">
            <Button variant="outline" size="sm" @click="setToday">
              Hoje
            </Button>
            <Button variant="outline" size="sm" @click="setLast7Days">
              Últimos 7 Dias
            </Button>
            <Button variant="outline" size="sm" @click="clearFilters">
              <Filter class="mr-2 h-4 w-4" />
              Limpar Filtros
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <!-- Action Filter -->
          <div class="space-y-2">
            <Label>Ação</Label>
            <Select v-model="filterAction">
              <SelectTrigger>
                <SelectValue placeholder="Todas" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todas</SelectItem>
                <SelectItem value="CREATE">Criado</SelectItem>
                <SelectItem value="UPDATE">Atualizado</SelectItem>
                <SelectItem value="DELETE">Eliminado</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Model Filter -->
          <div class="space-y-2">
            <Label>Modelo</Label>
            <Select v-model="filterModel">
              <SelectTrigger>
                <SelectValue placeholder="Todos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">Todos</SelectItem>
                <SelectItem
                  v-for="model in availableModels"
                  :key="model"
                  :value="model"
                >
                  {{ model }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- User Filter -->
          <div class="space-y-2">
            <Label>Utilizador</Label>
            <Input
              v-model="filterUser"
              type="text"
              placeholder="Nome ou email"
            />
          </div>

          <!-- Date From Filter -->
          <div class="space-y-2">
            <Label>Data Início</Label>
            <Input
              v-model="filterDateFrom"
              type="date"
              placeholder="Data início"
            />
          </div>

          <!-- Date To Filter -->
          <div class="space-y-2">
            <Label>Data Fim</Label>
            <Input
              v-model="filterDateTo"
              type="date"
              placeholder="Data fim"
            />
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Audit Table -->
    <Card class="flex-1 flex flex-col">
      <CardHeader>
        <div class="flex items-center justify-between">
          <CardTitle class="text-lg">Registos de Auditoria ({{ filteredLogs.length }})</CardTitle>
        </div>
      </CardHeader>
      <CardContent class="flex-1">
        <AuditTableAdvanced
          v-if="!isLoading"
          :logs="filteredLogs"
        />
        <div v-else class="flex items-center justify-center py-8">
          <p class="text-muted-foreground">A carregar registos...</p>
        </div>
      </CardContent>
    </Card>

    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      :class="[
        'fixed bottom-4 right-4 z-50 rounded-md px-6 py-4 text-white shadow-lg transition-all',
        toastVariant === 'success' ? 'bg-green-600' : 'bg-red-600',
      ]"
    >
      {{ toastMessage }}
    </div>
  </div>
</template>
