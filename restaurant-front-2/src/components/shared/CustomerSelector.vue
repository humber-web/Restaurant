<template>
  <div class="space-y-4">
    <!-- Selected Customer Display -->
    <div v-if="modelValue" class="p-3 bg-muted/30 rounded-lg border-2 border-primary/20">
      <div class="flex items-center justify-between">
        <div>
          <p class="font-semibold text-sm">{{ selectedCustomerName }}</p>
          <p class="text-xs text-muted-foreground">NIF: {{ selectedCustomerNIF }}</p>
        </div>
        <Button variant="ghost" size="sm" @click="clearCustomer">
          <X class="w-4 h-4" />
        </Button>
      </div>
    </div>

    <!-- No Customer Selected -->
    <div v-else class="space-y-3">
      <!-- Quick NIF Search -->
      <div class="space-y-2">
        <Label for="nif-search">Buscar Cliente por NIF</Label>
        <div class="flex gap-2">
          <Input
            id="nif-search"
            v-model="nifSearch"
            placeholder="123456789"
            maxlength="9"
            @input="validateNIF"
            @keypress.enter="searchByNIF"
          />
          <Button @click="searchByNIF" :disabled="!isValidNIF || loading">
            <Search class="w-4 h-4 mr-2" />
            Buscar
          </Button>
        </div>
        <p v-if="nifSearch && !isValidNIF" class="text-xs text-destructive">
          NIF deve ter 9 dígitos
        </p>
      </div>

      <!-- OR Divider -->
      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <span class="w-full border-t" />
        </div>
        <div class="relative flex justify-center text-xs uppercase">
          <span class="bg-background px-2 text-muted-foreground">ou</span>
        </div>
      </div>

      <!-- Customer List Button -->
      <Button variant="outline" class="w-full" @click="showCustomerListDialog = true">
        <Users class="w-4 h-4 mr-2" />
        Selecionar da Lista
      </Button>

      <!-- Create New Customer Button -->
      <Button variant="outline" class="w-full" @click="showCreateDialog = true">
        <UserPlus class="w-4 h-4 mr-2" />
        Criar Novo Cliente
      </Button>

      <!-- Anonymous Sale Info -->
      <p class="text-xs text-muted-foreground text-center">
        Deixe vazio para "Consumidor Final" (venda anônima)
      </p>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="p-3 bg-destructive/10 border border-destructive rounded-lg">
      <p class="text-sm text-destructive">{{ errorMessage }}</p>
    </div>

    <!-- Customer List Dialog -->
    <Dialog v-model:open="showCustomerListDialog">
      <DialogContent class="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Selecionar Cliente</DialogTitle>
        </DialogHeader>

        <div class="space-y-4">
          <!-- Search Filter -->
          <Input
            v-model="customerSearchQuery"
            placeholder="Buscar por nome ou NIF..."
            class="w-full"
          />

          <!-- Customer List -->
          <div v-if="loading" class="text-center py-8">
            <p class="text-muted-foreground">Carregando clientes...</p>
          </div>
          <div v-else-if="filteredCustomers.length === 0" class="text-center py-8">
            <p class="text-muted-foreground">Nenhum cliente encontrado</p>
          </div>
          <div v-else class="space-y-2 max-h-96 overflow-y-auto">
            <button
              v-for="customer in filteredCustomers"
              :key="customer.customerID"
              @click="selectCustomer(customer)"
              class="w-full p-3 text-left border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <p class="font-semibold text-sm">{{ customer.full_name }}</p>
              <p class="text-xs text-muted-foreground">NIF: {{ customer.tax_id }}</p>
              <p v-if="customer.email" class="text-xs text-muted-foreground">{{ customer.email }}</p>
            </button>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showCustomerListDialog = false">
            Cancelar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Quick Create Customer Dialog -->
    <Dialog v-model:open="showCreateDialog">
      <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Criar Novo Cliente</DialogTitle>
        </DialogHeader>

        <div class="space-y-4">
          <!-- Customer Type -->
          <div class="space-y-2">
            <Label>Tipo de Cliente</Label>
            <div class="flex gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="newCustomer.customer_type"
                  type="radio"
                  value="INDIVIDUAL"
                  class="w-4 h-4"
                />
                <span class="text-sm">Individual</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="newCustomer.customer_type"
                  type="radio"
                  value="COMPANY"
                  class="w-4 h-4"
                />
                <span class="text-sm">Empresa</span>
              </label>
            </div>
          </div>

          <!-- NIF (Required) -->
          <div class="space-y-2">
            <Label for="new-nif">NIF *</Label>
            <Input
              id="new-nif"
              v-model="newCustomer.tax_id"
              placeholder="123456789"
              maxlength="9"
              required
            />
          </div>

          <!-- Individual Fields -->
          <div v-if="newCustomer.customer_type === 'INDIVIDUAL'" class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="first-name">Primeiro Nome *</Label>
              <Input id="first-name" v-model="newCustomer.first_name" required />
            </div>
            <div class="space-y-2">
              <Label for="last-name">Apelido *</Label>
              <Input id="last-name" v-model="newCustomer.last_name" required />
            </div>
          </div>

          <!-- Company Field -->
          <div v-if="newCustomer.customer_type === 'COMPANY'" class="space-y-2">
            <Label for="company-name">Nome da Empresa *</Label>
            <Input id="company-name" v-model="newCustomer.company_name" required />
          </div>

          <!-- Address Fields -->
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="street">Rua *</Label>
              <Input id="street" v-model="newCustomer.street_name" required />
            </div>
            <div class="space-y-2">
              <Label for="building">Número</Label>
              <Input id="building" v-model="newCustomer.building_number" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="city">Cidade *</Label>
              <Input id="city" v-model="newCustomer.city" required />
            </div>
            <div class="space-y-2">
              <Label for="postal">Código Postal *</Label>
              <Input id="postal" v-model="newCustomer.postal_code" placeholder="7600-000" required />
            </div>
          </div>

          <!-- Contact Fields (Optional) -->
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="phone">Telefone</Label>
              <Input id="phone" v-model="newCustomer.telephone" />
            </div>
            <div class="space-y-2">
              <Label for="email">Email</Label>
              <Input id="email" v-model="newCustomer.email" type="email" />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showCreateDialog = false">
            Cancelar
          </Button>
          <Button @click="createCustomer" :disabled="!canCreateCustomer || creatingCustomer">
            {{ creatingCustomer ? 'Criando...' : 'Criar e Selecionar' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search, X, Users, UserPlus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { customersApi } from '@/services/api/customers'
import type { Customer, CreateCustomerPayload } from '@/types/models/customer'

// Props & Emits
interface Props {
  modelValue?: number | null
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  label: 'Cliente',
})

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
  'customerSelected': [customer: Customer | null]
}>()

// State
const nifSearch = ref('')
const isValidNIF = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const showCustomerListDialog = ref(false)
const showCreateDialog = ref(false)
const customerSearchQuery = ref('')
const allCustomers = ref<Customer[]>([])
const selectedCustomer = ref<Customer | null>(null)
const creatingCustomer = ref(false)

// New Customer Form
const newCustomer = ref<CreateCustomerPayload>({
  customer_type: 'INDIVIDUAL',
  tax_id: '',
  first_name: '',
  last_name: '',
  company_name: '',
  street_name: '',
  building_number: '',
  city: '',
  postal_code: '',
  country: 'CV',
  telephone: '',
  email: '',
})

// Computed
const selectedCustomerName = computed(() => {
  return selectedCustomer.value?.full_name || 'Cliente'
})

const selectedCustomerNIF = computed(() => {
  return selectedCustomer.value?.tax_id || ''
})

const filteredCustomers = computed(() => {
  if (!customerSearchQuery.value) return allCustomers.value

  const query = customerSearchQuery.value.toLowerCase()
  return allCustomers.value.filter(
    (c) =>
      c.full_name.toLowerCase().includes(query) ||
      c.tax_id.includes(query) ||
      (c.email && c.email.toLowerCase().includes(query))
  )
})

const canCreateCustomer = computed(() => {
  const hasNIF = newCustomer.value.tax_id.length === 9
  const hasName =
    newCustomer.value.customer_type === 'COMPANY'
      ? !!newCustomer.value.company_name
      : !!(newCustomer.value.first_name && newCustomer.value.last_name)
  const hasAddress =
    !!newCustomer.value.street_name &&
    !!newCustomer.value.city &&
    !!newCustomer.value.postal_code

  return hasNIF && hasName && hasAddress
})

// Methods
const validateNIF = () => {
  const nif = nifSearch.value.replace(/\D/g, '')
  nifSearch.value = nif
  isValidNIF.value = nif.length === 9
  errorMessage.value = ''
}

const searchByNIF = async () => {
  if (!isValidNIF.value) return

  loading.value = true
  errorMessage.value = ''

  try {
    const customer = await customersApi.searchByNIF(nifSearch.value)
    selectCustomer(customer)
    nifSearch.value = ''
  } catch (error: any) {
    if (error.response?.status === 404) {
      errorMessage.value = 'Cliente não encontrado. Crie um novo cliente.'
    } else {
      errorMessage.value = 'Erro ao buscar cliente. Tente novamente.'
    }
  } finally {
    loading.value = false
  }
}

const selectCustomer = (customer: Customer) => {
  selectedCustomer.value = customer
  emit('update:modelValue', customer.customerID)
  emit('customerSelected', customer)
  showCustomerListDialog.value = false
  errorMessage.value = ''
}

const clearCustomer = () => {
  selectedCustomer.value = null
  emit('update:modelValue', null)
  emit('customerSelected', null)
  nifSearch.value = ''
  errorMessage.value = ''
}

const loadCustomers = async () => {
  loading.value = true
  try {
    allCustomers.value = await customersApi.listActive()
  } catch (error) {
    errorMessage.value = 'Erro ao carregar lista de clientes.'
  } finally {
    loading.value = false
  }
}

const createCustomer = async () => {
  if (!canCreateCustomer.value) return

  creatingCustomer.value = true
  errorMessage.value = ''

  try {
    const created = await customersApi.create(newCustomer.value)
    selectCustomer(created)
    showCreateDialog.value = false
    // Reset form
    newCustomer.value = {
      customer_type: 'INDIVIDUAL',
      tax_id: '',
      first_name: '',
      last_name: '',
      company_name: '',
      street_name: '',
      building_number: '',
      city: '',
      postal_code: '',
      country: 'CV',
      telephone: '',
      email: '',
    }
  } catch (error: any) {
    errorMessage.value = error.response?.data?.error || 'Erro ao criar cliente.'
  } finally {
    creatingCustomer.value = false
  }
}

// Watch for dialog open to load customers
watch(showCustomerListDialog, (isOpen) => {
  if (isOpen && allCustomers.value.length === 0) {
    loadCustomers()
  }
})

// Load customer if modelValue is provided
watch(
  () => props.modelValue,
  async (customerId) => {
    if (customerId && !selectedCustomer.value) {
      try {
        selectedCustomer.value = await customersApi.get(customerId)
      } catch (error) {
        console.error('Failed to load customer:', error)
      }
    }
  },
  { immediate: true }
)
</script>
