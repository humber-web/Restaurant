<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { tablesApi } from '@/services/api';
import type { Table } from '@/types/models';
import TablesTableAdvanced from '@/components/tables/TablesTableAdvanced.vue'
import TablesForm from '@/components/tables/TablesForm.vue'
import DeleteTablesDialog from '@/components/tables/DeleteTablesDialog.vue'
// Configuração de mesas

const tables = ref<Table[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);
const formOpen = ref(false);
const deleteDialogOpen = ref(false);
const selectedTable = ref<Table | null>(null);
const formMode = ref<'create' | 'edit'>('create');
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')



onMounted(async () => {
  fetchTables();
});

async function fetchTables() {
  isLoading.value = true;
  error.value = null;
  try {
    tables.value = await tablesApi.getTables();
  } catch (err: any) {
    error.value = err?.message || 'Erro ao carregar mesas';
  } finally {
    isLoading.value = false;
  }
}

function openCreateDialog() {
  selectedTable.value = null
  formMode.value = 'create'
  formOpen.value = true
}

function openEditDialog(table: Table) {
  selectedTable.value = table
  formMode.value = 'edit'
  formOpen.value = true
}

function openDeleteDialog(table: Table) {
  selectedTable.value = table
  deleteDialogOpen.value = true
}

async function handleCreate(data: Omit<Table, 'tableid'>) {
  const newTable = await tablesApi.createTable(data)
  tables.value = [...tables.value, newTable]
  showToast('Mesa criada com sucesso', 'success')
}

async function handleUpdate(data: Omit<Table, 'tableid'>) {
  if (!selectedTable.value) return
  const updated = await tablesApi.updateTable(selectedTable.value.tableid, data)
  tables.value = tables.value.map(table =>
    table.tableid === selectedTable.value!.tableid ? updated : table
  )
  showToast('Mesa atualizada com sucesso', 'success')
}

async function handleFormSubmit(data: Omit<Table, 'tableid'>) {
  try {
    if (formMode.value === 'create') {
      await handleCreate(data);
    } else {
      await handleUpdate(data);
    }
  } catch (error: any) {
    showToast(
      formMode.value === 'create' ? 'Erro ao criar mesa' : 'Erro ao atualizar mesa',
      'error'
    )
    throw error // Re-throw to keep form open
  }
}

async function handleDelete(id: number) {
  try {
    await tablesApi.deleteTable(id)
    tables.value = tables.value.filter(table => table.tableid !== id)
    showToast('Mesa eliminada com sucesso', 'success')
  } catch (error: any) {
    showToast('Erro ao eliminar mesa', 'error')
    throw error
  }
}


function showToast(message: string, variant: 'success' | 'error') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

</script>

<template>
  <div class="flex flex-col gap-6 p-6">
    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      class="fixed top-4 right-4 z-50 rounded-lg border px-4 py-3 shadow-lg transition-all"
      :class="toastVariant === 'success' ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'"
    >
      {{ toastMessage }}
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex min-h-[400px] items-center justify-center">
      <div class="text-center">
        <div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4" />
        <p class="text-muted-foreground">A carregar mesas...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="flex flex-col gap-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Mesas</h1>
          <p class="text-muted-foreground mt-1">Gerir as mesas do restaurante</p>
        </div>
        <Button @click="openCreateDialog" size="default">
          <Plus class="mr-2 h-4 w-4" />
          Nova Mesa
        </Button>
      </div>

      <TablesTableAdvanced
        :tables="tables"
        @edit="openEditDialog"
        @delete="openDeleteDialog"
      />
    </div>

    <!-- Table Form Dialog -->
    <TablesForm
      v-model:open="formOpen"
      :table="selectedTable || undefined"
      :mode="formMode"
      @submit="handleFormSubmit"
    />

    <!-- Delete Confirmation Dialog -->
    <DeleteTablesDialog
      v-model:open="deleteDialogOpen"
      :table="selectedTable"
      @confirm="handleDelete"
    />
  </div>
</template>
