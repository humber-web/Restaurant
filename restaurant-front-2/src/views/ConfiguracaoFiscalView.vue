<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fiscalApi, type CompanySettings, type TaxRate } from '@/services/api/fiscal'
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
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
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
  Building2,
  Percent,
  Plus,
  Pencil,
  Trash2,
  Save,
  AlertCircle,
  CheckCircle,
  Calendar,
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

// Company Settings State
const companySettings = ref<CompanySettings | null>(null)
const isLoadingSettings = ref(false)
const isSavingSettings = ref(false)

// Tax Rates State
const taxRates = ref<TaxRate[]>([])
const isLoadingRates = ref(false)
const showTaxRateDialog = ref(false)
const editingTaxRate = ref<TaxRate | null>(null)
const taxRateForm = ref({
  tax_code: 'NOR' as 'NOR' | 'RED' | 'ISE' | 'OUT',
  description: '',
  percentage: 15.0,
  valid_from: '',
  valid_to: '',
  is_active: true,
})

// Load data
async function loadCompanySettings() {
  try {
    isLoadingSettings.value = true
    companySettings.value = await fiscalApi.getCompanySettings()
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao carregar configurações', 'error')
  } finally {
    isLoadingSettings.value = false
  }
}

async function loadTaxRates() {
  try {
    isLoadingRates.value = true
    taxRates.value = await fiscalApi.getTaxRates()
  } catch (error: any) {
    showToast(error.response?.data?.detail || 'Erro ao carregar taxas', 'error')
  } finally {
    isLoadingRates.value = false
  }
}

// Company Settings Actions
async function saveCompanySettings() {
  if (!companySettings.value) return

  try {
    isSavingSettings.value = true
    const response = await fiscalApi.updateCompanySettings(companySettings.value)
    companySettings.value = response.data
    showToast('Configurações salvas com sucesso!', 'success')
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || 'Erro ao salvar configurações'
    showToast(errorMsg, 'error')
  } finally {
    isSavingSettings.value = false
  }
}

// Tax Rate Actions
function openCreateTaxRateDialog() {
  editingTaxRate.value = null
  taxRateForm.value = {
    tax_code: 'NOR',
    description: '',
    percentage: 15.0,
    valid_from: new Date().toISOString().split('T')[0],
    valid_to: '',
    is_active: true,
  }
  showTaxRateDialog.value = true
}

function openEditTaxRateDialog(rate: TaxRate) {
  editingTaxRate.value = rate
  taxRateForm.value = {
    tax_code: rate.tax_code,
    description: rate.description,
    percentage: rate.percentage,
    valid_from: rate.valid_from,
    valid_to: rate.valid_to || '',
    is_active: rate.is_active,
  }
  showTaxRateDialog.value = true
}

async function saveTaxRate() {
  try {
    const data = {
      ...taxRateForm.value,
      valid_to: taxRateForm.value.valid_to || undefined,
    }

    if (editingTaxRate.value) {
      await fiscalApi.updateTaxRate(editingTaxRate.value.id, data)
      showToast('Taxa atualizada com sucesso!', 'success')
    } else {
      await fiscalApi.createTaxRate(data as any)
      showToast('Taxa criada com sucesso!', 'success')
    }

    showTaxRateDialog.value = false
    await loadTaxRates()
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || 'Erro ao salvar taxa'
    showToast(errorMsg, 'error')
  }
}

async function deleteTaxRate(rate: TaxRate) {
  if (!confirm(`Tem certeza que deseja eliminar a taxa "${rate.description}"?`)) {
    return
  }

  try {
    await fiscalApi.deleteTaxRate(rate.id)
    showToast('Taxa eliminada com sucesso!', 'success')
    await loadTaxRates()
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || 'Erro ao eliminar taxa'
    showToast(errorMsg, 'error')
  }
}

function getTaxCodeBadgeColor(code: string): string {
  switch (code) {
    case 'NOR': return 'bg-blue-100 text-blue-800'
    case 'RED': return 'bg-green-100 text-green-800'
    case 'ISE': return 'bg-gray-100 text-gray-800'
    case 'OUT': return 'bg-purple-100 text-purple-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

onMounted(() => {
  loadCompanySettings()
  loadTaxRates()
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
    <div>
      <h1 class="text-3xl font-bold">Configuração Fiscal</h1>
      <p class="text-sm text-muted-foreground">
        Configure os dados da empresa e taxas de IVA para conformidade com DNRE Cabo Verde
      </p>
    </div>

    <!-- Tabs -->
    <Tabs default-value="company" class="flex-1 flex flex-col">
      <TabsList class="grid w-full max-w-md grid-cols-2">
        <TabsTrigger value="company">
          <Building2 class="mr-2 h-4 w-4" />
          Empresa
        </TabsTrigger>
        <TabsTrigger value="taxes">
          <Percent class="mr-2 h-4 w-4" />
          Taxas IVA
        </TabsTrigger>
      </TabsList>

      <!-- Company Settings Tab -->
      <TabsContent value="company" class="flex-1 overflow-y-auto">
        <Card v-if="isLoadingSettings">
          <CardContent class="pt-6">
            <p class="text-center text-muted-foreground">A carregar configurações...</p>
          </CardContent>
        </Card>

        <div v-else-if="companySettings" class="space-y-4">
          <!-- Company Identification -->
          <Card>
            <CardHeader>
              <CardTitle>Identificação da Empresa</CardTitle>
              <CardDescription>Dados fiscais e de identificação</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                  <Label for="nif">NIF *</Label>
                  <Input
                    id="nif"
                    v-model="companySettings.tax_registration_number"
                    placeholder="123456789"
                    maxlength="9"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="company-name">Nome da Empresa *</Label>
                  <Input
                    id="company-name"
                    v-model="companySettings.company_name"
                    placeholder="Empresa Lda"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Address -->
          <Card>
            <CardHeader>
              <CardTitle>Endereço</CardTitle>
              <CardDescription>Morada fiscal da empresa</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="md:col-span-2 space-y-2">
                  <Label for="street">Rua *</Label>
                  <Input
                    id="street"
                    v-model="companySettings.street_name"
                    placeholder="Av. Cidade de Lisboa"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="building">Número</Label>
                  <Input
                    id="building"
                    v-model="companySettings.building_number"
                    placeholder="123"
                  />
                </div>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="space-y-2">
                  <Label for="city">Cidade *</Label>
                  <Input
                    id="city"
                    v-model="companySettings.city"
                    placeholder="Praia"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="postal">Código Postal *</Label>
                  <Input
                    id="postal"
                    v-model="companySettings.postal_code"
                    placeholder="7600"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="country">País</Label>
                  <Input
                    id="country"
                    v-model="companySettings.country"
                    value="CV"
                    disabled
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Contact -->
          <Card>
            <CardHeader>
              <CardTitle>Contactos</CardTitle>
              <CardDescription>Informações de contacto</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                  <Label for="phone">Telefone *</Label>
                  <Input
                    id="phone"
                    v-model="companySettings.telephone"
                    placeholder="+238 xxx xxxx"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="fax">Fax</Label>
                  <Input
                    id="fax"
                    v-model="companySettings.fax"
                    placeholder="+238 xxx xxxx"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="email">Email *</Label>
                  <Input
                    id="email"
                    v-model="companySettings.email"
                    type="email"
                    placeholder="fiscal@empresa.cv"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="website">Website</Label>
                  <Input
                    id="website"
                    v-model="companySettings.website"
                    placeholder="https://empresa.cv"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Invoice Series -->
          <Card>
            <CardHeader>
              <CardTitle>Séries de Documentos</CardTitle>
              <CardDescription>Configuração das séries para faturas e documentos</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="space-y-2">
                  <Label for="invoice-series">Série de Faturas</Label>
                  <Input
                    id="invoice-series"
                    v-model="companySettings.invoice_series"
                    placeholder="FT A"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="credit-series">Série de Notas de Crédito</Label>
                  <Input
                    id="credit-series"
                    v-model="companySettings.credit_note_series"
                    placeholder="NC A"
                  />
                </div>
                <div class="space-y-2">
                  <Label for="receipt-series">Série de Talões de Venda</Label>
                  <Input
                    id="receipt-series"
                    v-model="companySettings.receipt_series"
                    placeholder="TV A"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Software Certification -->
          <Card>
            <CardHeader>
              <CardTitle>Certificação do Software</CardTitle>
              <CardDescription>Informações sobre a certificação DNRE</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                  <Label for="cert-number">Número de Certificado</Label>
                  <Input
                    id="cert-number"
                    v-model="companySettings.software_certificate_number"
                    placeholder="0"
                  />
                  <p class="text-xs text-muted-foreground">
                    Use '0' até obter a certificação oficial da DNRE
                  </p>
                </div>
                <div class="space-y-2">
                  <Label for="version">Versão do Software</Label>
                  <Input
                    id="version"
                    v-model="companySettings.software_version"
                    placeholder="1.0.0"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Save Button -->
          <div class="flex justify-end">
            <Button
              size="lg"
              @click="saveCompanySettings"
              :disabled="isSavingSettings"
            >
              <Save v-if="!isSavingSettings" class="mr-2 h-4 w-4" />
              <span v-if="isSavingSettings">A guardar...</span>
              <span v-else>Guardar Configurações</span>
            </Button>
          </div>
        </div>
      </TabsContent>

      <!-- Tax Rates Tab -->
      <TabsContent value="taxes" class="flex-1 flex flex-col overflow-hidden">
        <div class="space-y-4 flex-1 flex flex-col overflow-hidden">
          <!-- Header with Add Button -->
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold">Taxas de IVA</h2>
              <p class="text-sm text-muted-foreground">
                Gestão histórica de taxas de IVA para conformidade fiscal
              </p>
            </div>
            <Button @click="openCreateTaxRateDialog">
              <Plus class="mr-2 h-4 w-4" />
              Nova Taxa
            </Button>
          </div>

          <!-- Tax Rates Table -->
          <Card class="flex-1 flex flex-col overflow-hidden">
            <CardContent class="pt-6 flex-1 overflow-y-auto">
              <div v-if="isLoadingRates" class="text-center py-8">
                <p class="text-muted-foreground">A carregar taxas...</p>
              </div>

              <div v-else-if="taxRates.length === 0" class="text-center py-8">
                <AlertCircle class="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p class="text-muted-foreground mb-4">Nenhuma taxa de IVA configurada</p>
                <Button @click="openCreateTaxRateDialog">
                  <Plus class="mr-2 h-4 w-4" />
                  Criar Primeira Taxa
                </Button>
              </div>

              <Table v-else>
                <TableHeader>
                  <TableRow>
                    <TableHead>Código</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Percentagem</TableHead>
                    <TableHead>Válido Desde</TableHead>
                    <TableHead>Válido Até</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead class="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-for="rate in taxRates" :key="rate.id">
                    <TableCell>
                      <Badge :class="getTaxCodeBadgeColor(rate.tax_code)">
                        {{ rate.tax_code_display }}
                      </Badge>
                    </TableCell>
                    <TableCell class="font-medium">{{ rate.description }}</TableCell>
                    <TableCell>{{ rate.percentage }}%</TableCell>
                    <TableCell>
                      <div class="flex items-center gap-1 text-sm">
                        <Calendar class="h-3 w-3" />
                        {{ new Date(rate.valid_from).toLocaleDateString('pt-PT') }}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div v-if="rate.valid_to" class="flex items-center gap-1 text-sm">
                        <Calendar class="h-3 w-3" />
                        {{ new Date(rate.valid_to).toLocaleDateString('pt-PT') }}
                      </div>
                      <span v-else class="text-muted-foreground text-sm">—</span>
                    </TableCell>
                    <TableCell>
                      <Badge v-if="rate.is_active" variant="default">
                        <CheckCircle class="mr-1 h-3 w-3" />
                        {{ rate.status }}
                      </Badge>
                      <Badge v-else variant="secondary">
                        {{ rate.status }}
                      </Badge>
                    </TableCell>
                    <TableCell class="text-right">
                      <div class="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          @click="openEditTaxRateDialog(rate)"
                        >
                          <Pencil class="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          @click="deleteTaxRate(rate)"
                        >
                          <Trash2 class="h-3 w-3 text-red-600" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </TabsContent>
    </Tabs>

    <!-- Tax Rate Dialog -->
    <Dialog v-model:open="showTaxRateDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {{ editingTaxRate ? 'Editar Taxa de IVA' : 'Nova Taxa de IVA' }}
          </DialogTitle>
          <DialogDescription>
            Configure a taxa de IVA com o período de validade
          </DialogDescription>
        </DialogHeader>

        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <Label for="tax-code">Código de IVA *</Label>
            <Select v-model="taxRateForm.tax_code">
              <SelectTrigger>
                <SelectValue placeholder="Selecione o código" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="NOR">Normal</SelectItem>
                <SelectItem value="RED">Reduzida</SelectItem>
                <SelectItem value="ISE">Isento</SelectItem>
                <SelectItem value="OUT">Outro</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2">
            <Label for="description">Descrição *</Label>
            <Input
              id="description"
              v-model="taxRateForm.description"
              placeholder="Ex: IVA Normal 15%"
            />
          </div>

          <div class="space-y-2">
            <Label for="percentage">Percentagem (%) *</Label>
            <Input
              id="percentage"
              v-model.number="taxRateForm.percentage"
              type="number"
              step="0.01"
              min="0"
              max="100"
              placeholder="15.00"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="valid-from">Válido Desde *</Label>
              <Input
                id="valid-from"
                v-model="taxRateForm.valid_from"
                type="date"
              />
            </div>
            <div class="space-y-2">
              <Label for="valid-to">Válido Até</Label>
              <Input
                id="valid-to"
                v-model="taxRateForm.valid_to"
                type="date"
              />
              <p class="text-xs text-muted-foreground">
                Deixe em branco se ainda estiver ativa
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <input
              id="is-active"
              v-model="taxRateForm.is_active"
              type="checkbox"
              class="h-4 w-4"
            />
            <Label for="is-active" class="cursor-pointer">Taxa ativa</Label>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" @click="showTaxRateDialog = false">
            Cancelar
          </Button>
          <Button @click="saveTaxRate">
            <Save class="mr-2 h-4 w-4" />
            {{ editingTaxRate ? 'Atualizar' : 'Criar' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
