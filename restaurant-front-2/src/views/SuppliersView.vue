<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { suppliersApi } from '@/services/api/suppliers'
import type { Supplier, CreateSupplierPayload } from '@/types/models/supplier'
import SuppliersTableAdvanced from '@/components/suppliers/SuppliersTableAdvanced.vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'
import { Building2, Plus, Filter, X } from 'lucide-vue-next'

// Toast
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')
function showToast(message: string, variant: 'success' | 'error' = 'success') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => { toastMessage.value = null }, 3000)
}

// State
const suppliers = ref<Supplier[]>([])
const isLoading = ref(false)
const filterActive = ref<boolean | ''>('')
const searchQuery = ref('')

// Dialogs
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)
const showDeleteDialog = ref(false)
const selectedSupplier = ref<Supplier | null>(null)

// Form
const formData = ref<CreateSupplierPayload>({
  tax_id: '',
  company_name: '',
  contact_person: '',
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
  bank_name: '',
  bank_account: '',
  iban: '',
  payment_terms: '',
  notes: '',
})

async function loadSuppliers() {
  try {
    isLoading.value = true
    const params: any = {}
    if (filterActive.value !== '') params.is_active = filterActive.value
    if (searchQuery.value) params.search = searchQuery.value
    suppliers.value = await suppliersApi.list(params)
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao carregar fornecedores', 'error')
  } finally {
    isLoading.value = false
  }
}

function clearFilters() {
  filterActive.value = ''
  searchQuery.value = ''
  loadSuppliers()
}

function resetForm() {
  formData.value = {
    tax_id: '', company_name: '', contact_person: '', street_name: '', city: '', postal_code: '',
    region: '', country: 'CV', address_detail: '', telephone: '', mobile_phone: '', fax: '', email: '',
    website: '', bank_name: '', bank_account: '', iban: '', payment_terms: '', notes: ''
  }
}

function openCreateDialog() {
  resetForm()
  showCreateDialog.value = true
}

async function createSupplier() {
  try {
    isLoading.value = true
    await suppliersApi.create(formData.value)
    showToast('Fornecedor criado com sucesso!', 'success')
    showCreateDialog.value = false
    loadSuppliers()
    resetForm()
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao criar fornecedor', 'error')
  } finally {
    isLoading.value = false
  }
}

function viewSupplier(supplier: Supplier) {
  selectedSupplier.value = supplier
  showViewDialog.value = true
}

function editSupplier(supplier: Supplier) {
  selectedSupplier.value = supplier
  formData.value = {
    tax_id: supplier.tax_id, company_name: supplier.company_name,
    contact_person: supplier.contact_person, street_name: supplier.street_name,
    building_number: supplier.building_number, city: supplier.city,
    postal_code: supplier.postal_code, region: supplier.region,
    country: supplier.country, address_detail: supplier.address_detail,
    telephone: supplier.telephone, mobile_phone: supplier.mobile_phone,
    fax: supplier.fax, email: supplier.email, website: supplier.website,
    bank_name: supplier.bank_name, bank_account: supplier.bank_account,
    iban: supplier.iban, payment_terms: supplier.payment_terms, notes: supplier.notes
  }
  showEditDialog.value = true
}

async function updateSupplier() {
  if (!selectedSupplier.value) return
  try {
    isLoading.value = true
    await suppliersApi.update(selectedSupplier.value.supplierID, formData.value)
    showToast('Fornecedor atualizado com sucesso!', 'success')
    showEditDialog.value = false
    loadSuppliers()
    resetForm()
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao atualizar fornecedor', 'error')
  } finally {
    isLoading.value = false
  }
}

function openDeleteDialog(supplier: Supplier) {
  selectedSupplier.value = supplier
  showDeleteDialog.value = true
}

async function deleteSupplier() {
  if (!selectedSupplier.value) return
  try {
    isLoading.value = true
    await suppliersApi.delete(selectedSupplier.value.supplierID)
    showToast('Fornecedor desativado com sucesso!', 'success')
    showDeleteDialog.value = false
    loadSuppliers()
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao desativar fornecedor', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => loadSuppliers())
</script>

<template>
  <div class="flex h-full flex-col gap-4 p-6">
    <!-- Toast -->
    <div v-if="toastMessage" class="fixed top-4 right-4 z-50 rounded-lg border px-4 py-3 shadow-lg transition-all"
      :class="toastVariant === 'success' ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'">
      {{ toastMessage }}
    </div>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">Gestão de Fornecedores</h1>
        <p class="text-sm text-muted-foreground">Gerir fornecedores para conformidade SAF-T CV</p>
      </div>
      <Button @click="openCreateDialog">
        <Plus class="mr-2 h-4 w-4" />Novo Fornecedor
      </Button>
    </div>

    <!-- Filters -->
    <Card>
      <CardHeader>
        <CardTitle class="flex items-center gap-2"><Filter class="h-5 w-5" />Filtros</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label>Estado</Label>
            <Select v-model="filterActive">
              <SelectTrigger><SelectValue placeholder="Todos os estados" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos</SelectItem>
                <SelectItem :value="true">Ativos</SelectItem>
                <SelectItem :value="false">Inativos</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="space-y-2">
            <Label>Pesquisar</Label>
            <Input v-model="searchQuery" placeholder="Nome, NIF, email..." @keyup.enter="loadSuppliers" />
          </div>
        </div>
        <div class="flex gap-2 mt-4">
          <Button @click="loadSuppliers" :disabled="isLoading">Aplicar Filtros</Button>
          <Button variant="outline" @click="clearFilters" :disabled="isLoading"><X class="mr-2 h-4 w-4" />Limpar</Button>
        </div>
      </CardContent>
    </Card>

    <!-- Table -->
    <Card class="flex-1 flex flex-col overflow-hidden">
      <CardHeader>
        <CardTitle class="flex items-center gap-2"><Building2 class="h-5 w-5" />Fornecedores</CardTitle>
        <CardDescription>{{ suppliers.length }} fornecedor(es) encontrado(s)</CardDescription>
      </CardHeader>
      <CardContent class="flex-1 overflow-auto">
        <div v-if="isLoading" class="flex items-center justify-center h-full">
          <p class="text-muted-foreground">A carregar fornecedores...</p>
        </div>
        <div v-else-if="suppliers.length === 0" class="flex items-center justify-center h-full">
          <div class="text-center">
            <Building2 class="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p class="text-muted-foreground">Nenhum fornecedor encontrado</p>
          </div>
        </div>
        <SuppliersTableAdvanced v-else :suppliers="suppliers" @view="viewSupplier" @edit="editSupplier" @delete="openDeleteDialog" />
      </CardContent>
    </Card>

    <!-- Create/Edit Dialog -->
    <Dialog v-model:open="showCreateDialog">
      <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Criar Novo Fornecedor</DialogTitle>
          <DialogDescription>Preencha os dados do fornecedor para conformidade SAF-T CV</DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label>NIF (9 dígitos) *</Label>
              <Input v-model="formData.tax_id" placeholder="123456789" maxlength="9" />
            </div>
            <div class="space-y-2">
              <Label>Nome da Empresa *</Label>
              <Input v-model="formData.company_name" placeholder="Nome da Empresa" />
            </div>
          </div>
          <div class="space-y-2">
            <Label>Pessoa de Contacto</Label>
            <Input v-model="formData.contact_person" />
          </div>
          <div class="space-y-4">
            <h3 class="font-semibold border-b pb-2">Morada</h3>
            <div class="grid grid-cols-3 gap-4">
              <div class="col-span-2 space-y-2">
                <Label>Rua *</Label>
                <Input v-model="formData.street_name" />
              </div>
              <div class="space-y-2">
                <Label>Número</Label>
                <Input v-model="formData.building_number" />
              </div>
            </div>
            <div class="grid grid-cols-3 gap-4">
              <div class="space-y-2">
                <Label>Cidade *</Label>
                <Input v-model="formData.city" />
              </div>
              <div class="space-y-2">
                <Label>Código Postal *</Label>
                <Input v-model="formData.postal_code" placeholder="7600-000" />
              </div>
              <div class="space-y-2">
                <Label>Região</Label>
                <Input v-model="formData.region" />
              </div>
            </div>
          </div>
          <div class="space-y-4">
            <h3 class="font-semibold border-b pb-2">Contactos</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label>Telefone</Label>
                <Input v-model="formData.telephone" />
              </div>
              <div class="space-y-2">
                <Label>Email</Label>
                <Input v-model="formData.email" type="email" />
              </div>
            </div>
          </div>
          <div class="space-y-4">
            <h3 class="font-semibold border-b pb-2">Informação Bancária</h3>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label>Banco</Label>
                <Input v-model="formData.bank_name" />
              </div>
              <div class="space-y-2">
                <Label>IBAN</Label>
                <Input v-model="formData.iban" />
              </div>
            </div>
            <div class="space-y-2">
              <Label>Condições de Pagamento</Label>
              <Input v-model="formData.payment_terms" placeholder="ex: 30 dias" />
            </div>
          </div>
          <div class="space-y-2">
            <Label>Notas</Label>
            <Textarea v-model="formData.notes" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showCreateDialog = false">Cancelar</Button>
          <Button @click="createSupplier" :disabled="isLoading">Criar Fornecedor</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Edit Dialog -->
    <Dialog v-model:open="showEditDialog">
      <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Editar Fornecedor</DialogTitle>
          <DialogDescription>Atualizar dados do fornecedor #{{ selectedSupplier?.supplierID }}</DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label>NIF *</Label>
              <Input v-model="formData.tax_id" maxlength="9" />
            </div>
            <div class="space-y-2">
              <Label>Nome da Empresa *</Label>
              <Input v-model="formData.company_name" />
            </div>
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div class="space-y-2">
              <Label>Cidade *</Label>
              <Input v-model="formData.city" />
            </div>
            <div class="space-y-2">
              <Label>Código Postal *</Label>
              <Input v-model="formData.postal_code" />
            </div>
            <div class="space-y-2">
              <Label>Telefone</Label>
              <Input v-model="formData.telephone" />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showEditDialog = false">Cancelar</Button>
          <Button @click="updateSupplier" :disabled="isLoading">Atualizar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- View Dialog -->
    <Dialog v-model:open="showViewDialog">
      <DialogContent class="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Detalhes do Fornecedor</DialogTitle>
        </DialogHeader>
        <div v-if="selectedSupplier" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <Label class="text-muted-foreground">ID</Label>
              <p class="font-semibold">#{{ selectedSupplier.supplierID }}</p>
            </div>
            <div>
              <Label class="text-muted-foreground">Estado</Label>
              <div class="mt-1">
                <Badge :variant="selectedSupplier.is_active ? 'default' : 'destructive'">
                  {{ selectedSupplier.is_active ? 'Ativo' : 'Inativo' }}
                </Badge>
              </div>
            </div>
          </div>
          <div>
            <Label class="text-muted-foreground">Empresa</Label>
            <p class="text-lg font-semibold">{{ selectedSupplier.company_name }}</p>
          </div>
          <div>
            <Label class="text-muted-foreground">NIF</Label>
            <p class="font-mono">{{ selectedSupplier.tax_id }}</p>
          </div>
          <div>
            <Label class="text-muted-foreground">Morada</Label>
            <p>{{ selectedSupplier.full_address }}</p>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <Label class="text-muted-foreground">Telefone</Label>
              <p>{{ selectedSupplier.telephone || 'N/A' }}</p>
            </div>
            <div>
              <Label class="text-muted-foreground">Email</Label>
              <p>{{ selectedSupplier.email || 'N/A' }}</p>
            </div>
          </div>
          <div v-if="selectedSupplier.payment_terms">
            <Label class="text-muted-foreground">Condições de Pagamento</Label>
            <p>{{ selectedSupplier.payment_terms }}</p>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" @click="showViewDialog = false">Fechar</Button>
          <Button @click="editSupplier(selectedSupplier!)">Editar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- Delete Dialog -->
    <AlertDialog v-model:open="showDeleteDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Desativar Fornecedor?</AlertDialogTitle>
          <AlertDialogDescription>
            Tem a certeza que deseja desativar o fornecedor <strong>{{ selectedSupplier?.company_name }}</strong>?<br><br>
            O fornecedor será marcado como inativo mas permanecerá no sistema para histórico.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancelar</AlertDialogCancel>
          <AlertDialogAction @click="deleteSupplier">Desativar</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
