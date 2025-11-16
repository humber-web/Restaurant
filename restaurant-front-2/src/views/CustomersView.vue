<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { customersApi } from '@/services/api/customers'
import type { Customer, CreateCustomerPayload, CustomerType } from '@/types/models/customer'
import CustomersTableAdvanced from '@/components/customers/CustomersTableAdvanced.vue'
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
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Users, Plus, Filter, X } from 'lucide-vue-next'

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
const customers = ref<Customer[]>([])
const isLoading = ref(false)

// Filters
const filterType = ref<CustomerType | ''>('')
const filterActive = ref<boolean | ''>('')
const searchQuery = ref('')

// Dialogs
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const showDeleteDialog = ref(false)
const selectedCustomer = ref<Customer | null>(null)

// Form data
const formData = ref<CreateCustomerPayload>({
  customer_type: 'INDIVIDUAL',
  tax_id: '',
  company_name: '',
  first_name: '',
  last_name: '',
  street_name: '',
  building_number: '',
  city: '',
  postal_code: '',
  region: '',
  country: 'CV',
  address_detail: '',
  telephone: '',
  mobile_phone: '',
  fax: '',
  email: '',
  website: '',
  notes: '',
})

// Load customers
async function loadCustomers() {
  try {
    isLoading.value = true

    const params: any = {}
    if (filterType.value) params.customer_type = filterType.value
    if (filterActive.value !== '') params.is_active = filterActive.value
    if (searchQuery.value) params.search = searchQuery.value

    customers.value = await customersApi.list(params)
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao carregar clientes', 'error')
  } finally {
    isLoading.value = false
  }
}

// Apply filters
function applyFilters() {
  loadCustomers()
}

// Clear filters
function clearFilters() {
  filterType.value = ''
  filterActive.value = ''
  searchQuery.value = ''
  loadCustomers()
}

// Reset form
function resetForm() {
  formData.value = {
    customer_type: 'INDIVIDUAL',
    tax_id: '',
    company_name: '',
    first_name: '',
    last_name: '',
    street_name: '',
    city: '',
    postal_code: '',
    region: '',
    country: 'CV',
    address_detail: '',
    telephone: '',
    mobile_phone: '',
    fax: '',
    email: '',
    website: '',
    notes: '',
  }
}

// Open create dialog
function openCreateDialog() {
  resetForm()
  showCreateDialog.value = true
}

// Create customer
async function createCustomer() {
  try {
    isLoading.value = true
    await customersApi.create(formData.value)
    showToast('Cliente criado com sucesso!', 'success')
    showCreateDialog.value = false
    loadCustomers()
    resetForm()
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao criar cliente', 'error')
  } finally {
    isLoading.value = false
  }
}

// View customer
function viewCustomer(customer: Customer) {
  selectedCustomer.value = customer
  showViewDialog.value = true
}

// Open edit dialog
function editCustomer(customer: Customer) {
  selectedCustomer.value = customer
  formData.value = {
    customer_type: customer.customer_type,
    tax_id: customer.tax_id,
    company_name: customer.company_name,
    first_name: customer.first_name,
    last_name: customer.last_name,
    street_name: customer.street_name,
    building_number: customer.building_number,
    city: customer.city,
    postal_code: customer.postal_code,
    region: customer.region,
    country: customer.country,
    address_detail: customer.address_detail,
    telephone: customer.telephone,
    mobile_phone: customer.mobile_phone,
    fax: customer.fax,
    email: customer.email,
    website: customer.website,
    notes: customer.notes,
  }
  showEditDialog.value = true
}

// Update customer
async function updateCustomer() {
  if (!selectedCustomer.value) return

  try {
    isLoading.value = true
    await customersApi.update(selectedCustomer.value.customerID, formData.value)
    showToast('Cliente atualizado com sucesso!', 'success')
    showEditDialog.value = false
    loadCustomers()
    resetForm()
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao atualizar cliente', 'error')
  } finally {
    isLoading.value = false
  }
}

// Open delete dialog
function openDeleteDialog(customer: Customer) {
  selectedCustomer.value = customer
  showDeleteDialog.value = true
}

// Delete customer (soft delete)
async function deleteCustomer() {
  if (!selectedCustomer.value) return

  try {
    isLoading.value = true
    await customersApi.delete(selectedCustomer.value.customerID)
    showToast('Cliente desativado com sucesso!', 'success')
    showDeleteDialog.value = false
    loadCustomers()
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao desativar cliente', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadCustomers()
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
      <div>
        <h1 class="text-3xl font-bold">Gestão de Clientes</h1>
        <p class="text-sm text-muted-foreground">
          Gerir clientes para conformidade SAF-T CV
        </p>
      </div>
      <Button @click="openCreateDialog">
        <Plus class="mr-2 h-4 w-4" />
        Novo Cliente
      </Button>
    </div>

    <!-- Filters -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Filter class="h-5 w-5" />
          Filtros
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="space-y-2">
            <Label for="filter-type">Tipo</Label>
            <Select v-model="filterType">
              <SelectTrigger>
                <SelectValue placeholder="Todos os tipos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem value="INDIVIDUAL">Individual</SelectItem>
                <SelectItem value="COMPANY">Empresa</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label for="filter-active">Estado</Label>
            <Select v-model="filterActive">
              <SelectTrigger>
                <SelectValue placeholder="Todos os estados" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem :value="true">Ativos</SelectItem>
                <SelectItem :value="false">Inativos</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label for="search">Pesquisar</Label>
            <Input
              id="search"
              v-model="searchQuery"
              placeholder="Nome, NIF, email..."
              @keyup.enter="applyFilters"
            />
          </div>
        </div>

        <div class="flex gap-2 mt-4">
          <Button @click="applyFilters" :disabled="isLoading">
            Aplicar Filtros
          </Button>
          <Button variant="outline" @click="clearFilters" :disabled="isLoading">
            <X class="mr-2 h-4 w-4" />
            Limpar
          </Button>
        </div>
      </CardContent>
    </Card>

    <!-- Customers Table -->
    <Card class="flex-1 flex flex-col overflow-hidden">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Users class="h-5 w-5" />
          Clientes
        </CardTitle>
        <CardDescription>
          {{ customers.length }} cliente(s) encontrado(s)
        </CardDescription>
      </CardHeader>
      <CardContent class="flex-1 overflow-auto">
        <div v-if="isLoading" class="flex items-center justify-center h-full">
          <p class="text-muted-foreground">A carregar clientes...</p>
        </div>

        <div v-else-if="customers.length === 0" class="flex items-center justify-center h-full">
          <div class="text-center">
            <Users class="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p class="text-muted-foreground">Nenhum cliente encontrado</p>
          </div>
        </div>

        <CustomersTableAdvanced
          v-else
          :customers="customers"
          @view="viewCustomer"
          @edit="editCustomer"
          @delete="openDeleteDialog"
        />
      </CardContent>
    </Card>

    <!-- Create/Edit Dialog -->
    <Dialog v-model:open="showCreateDialog">
      <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Criar Novo Cliente</DialogTitle>
          <DialogDescription>
            Preencha os dados do cliente para conformidade SAF-T CV
          </DialogDescription>
        </DialogHeader>

        <div class="space-y-4">
          <!-- Customer Type -->
          <div class="space-y-2">
            <Label>Tipo de Cliente *</Label>
            <Select v-model="formData.customer_type">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="INDIVIDUAL">Individual</SelectItem>
                <SelectItem value="COMPANY">Empresa</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- NIF -->
          <div class="space-y-2">
            <Label for="tax_id">NIF (9 dígitos) *</Label>
            <Input
              id="tax_id"
              v-model="formData.tax_id"
              placeholder="123456789"
              maxlength="9"
            />
          </div>

          <!-- Company Name (if COMPANY) -->
          <div v-if="formData.customer_type === 'COMPANY'" class="space-y-2">
            <Label for="company_name">Nome da Empresa *</Label>
            <Input
              id="company_name"
              v-model="formData.company_name"
              placeholder="Nome da Empresa"
            />
          </div>

          <!-- Individual Name (if INDIVIDUAL) -->
          <div v-if="formData.customer_type === 'INDIVIDUAL'" class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="first_name">Primeiro Nome</Label>
              <Input id="first_name" v-model="formData.first_name" />
            </div>
            <div class="space-y-2">
              <Label for="last_name">Apelido</Label>
              <Input id="last_name" v-model="formData.last_name" />
            </div>
          </div>

          <!-- Address -->
          <div class="space-y-4">
            <h3 class="font-semibold border-b pb-2">Morada</h3>
            <div class="grid grid-cols-3 gap-4">
              <div class="col-span-2 space-y-2">
                <Label for="street_name">Rua *</Label>
                <Input id="street_name" v-model="formData.street_name" />
              </div>
              <div class="space-y-2">
                <Label for="building_number">Número</Label>
                <Input id="building_number" v-model="formData.building_number" />
              </div>
            </div>

            <div class="grid grid-cols-3 gap-4">
              <div class="space-y-2">
                <Label for="city">Cidade *</Label>
                <Input id="city" v-model="formData.city" />
              </div>
              <div class="space-y-2">
                <Label for="postal_code">Código Postal *</Label>
                <Input id="postal_code" v-model="formData.postal_code" placeholder="7600-000" />
              </div>
              <div class="space-y-2">
                <Label for="region">Região</Label>
                <Input id="region" v-model="formData.region" />
              </div>
            </div>

            <div class="space-y-2">
              <Label for="address_detail">Detalhes Adicionais</Label>
              <Textarea id="address_detail" v-model="formData.address_detail" />
            </div>
          </div>

          <!-- Contacts -->
          <div class="space-y-4">
            <h3 class="font-semibold border-b pb-2">Contactos</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="telephone">Telefone</Label>
                <Input id="telephone" v-model="formData.telephone" />
              </div>
              <div class="space-y-2">
                <Label for="mobile_phone">Telemóvel</Label>
                <Input id="mobile_phone" v-model="formData.mobile_phone" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="email">Email</Label>
                <Input id="email" v-model="formData.email" type="email" />
              </div>
              <div class="space-y-2">
                <Label for="website">Website</Label>
                <Input id="website" v-model="formData.website" type="url" />
              </div>
            </div>
          </div>

          <!-- Notes -->
          <div class="space-y-2">
            <Label for="notes">Notas</Label>
            <Textarea id="notes" v-model="formData.notes" />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showCreateDialog = false">Cancelar</Button>
          <Button @click="createCustomer" :disabled="isLoading">Criar Cliente</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Edit Dialog (reuses same form) -->
    <Dialog v-model:open="showEditDialog">
      <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Editar Cliente</DialogTitle>
          <DialogDescription>
            Atualizar dados do cliente #{{ selectedCustomer?.customerID }}
          </DialogDescription>
        </DialogHeader>

        <!-- Same form fields as create -->
        <div class="space-y-4">
          <!-- (Reuse same form structure as Create Dialog) -->
          <!-- Customer Type -->
          <div class="space-y-2">
            <Label>Tipo de Cliente *</Label>
            <Select v-model="formData.customer_type">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="INDIVIDUAL">Individual</SelectItem>
                <SelectItem value="COMPANY">Empresa</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- NIF -->
          <div class="space-y-2">
            <Label for="edit_tax_id">NIF (9 dígitos) *</Label>
            <Input
              id="edit_tax_id"
              v-model="formData.tax_id"
              placeholder="123456789"
              maxlength="9"
            />
          </div>

          <!-- Rest of form fields... (same as create) -->
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showEditDialog = false">Cancelar</Button>
          <Button @click="updateCustomer" :disabled="isLoading">Atualizar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- View Dialog -->
    <Dialog v-model:open="showViewDialog">
      <DialogContent class="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Detalhes do Cliente</DialogTitle>
        </DialogHeader>

        <div v-if="selectedCustomer" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <Label class="text-muted-foreground">ID</Label>
              <p class="font-semibold">#{{ selectedCustomer.customerID }}</p>
            </div>
            <div>
              <Label class="text-muted-foreground">Tipo</Label>
              <div class="mt-1">
                <Badge :variant="selectedCustomer.customer_type === 'COMPANY' ? 'default' : 'secondary'">
                  {{ selectedCustomer.customer_type === 'COMPANY' ? 'Empresa' : 'Individual' }}
                </Badge>
              </div>
            </div>
          </div>

          <div>
            <Label class="text-muted-foreground">Nome</Label>
            <p class="text-lg font-semibold">{{ selectedCustomer.full_name }}</p>
          </div>

          <div>
            <Label class="text-muted-foreground">NIF</Label>
            <p class="font-mono">{{ selectedCustomer.tax_id }}</p>
          </div>

          <div>
            <Label class="text-muted-foreground">Morada</Label>
            <p>{{ selectedCustomer.full_address }}</p>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <Label class="text-muted-foreground">Telefone</Label>
              <p>{{ selectedCustomer.telephone || 'N/A' }}</p>
            </div>
            <div>
              <Label class="text-muted-foreground">Email</Label>
              <p>{{ selectedCustomer.email || 'N/A' }}</p>
            </div>
          </div>

          <div>
            <Label class="text-muted-foreground">Estado</Label>
            <div class="mt-1">
              <Badge :variant="selectedCustomer.is_active ? 'default' : 'destructive'">
                {{ selectedCustomer.is_active ? 'Ativo' : 'Inativo' }}
              </Badge>
            </div>
          </div>

          <div v-if="selectedCustomer.notes">
            <Label class="text-muted-foreground">Notas</Label>
            <p class="text-sm">{{ selectedCustomer.notes }}</p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showViewDialog = false">Fechar</Button>
          <Button @click="editCustomer(selectedCustomer!)">Editar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <AlertDialog v-model:open="showDeleteDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Desativar Cliente?</AlertDialogTitle>
          <AlertDialogDescription>
            Tem a certeza que deseja desativar o cliente
            <strong>{{ selectedCustomer?.full_name }}</strong>?
            <br><br>
            O cliente será marcado como inativo mas permanecerá no sistema para histórico.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancelar</AlertDialogCancel>
          <AlertDialogAction @click="deleteCustomer">Desativar</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
