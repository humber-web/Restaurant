<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import type { Table } from '@/types/models';
import TablesTableAdvanced from '@/components/tables/TablesTableAdvanced.vue'
import TablesForm from '@/components/tables/TablesForm.vue'
import DeleteTablesDialog from '@/components/tables/DeleteTablesDialog.vue'
import { useTablesStore } from '@/stores/tables'

const tablesStore = useTablesStore()

const formOpen = ref(false);
const deleteDialogOpen = ref(false);
const selectedTable = ref<Table | null>(null);
const formMode = ref<'create' | 'edit'>('create');
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

// Use store state
const tables = computed(() => tablesStore.tables)
const isLoading = computed(() => tablesStore.isLoading)

onMounted(async () => {
  try {
    await tablesStore.fetchTables() // Smart fetch - only loads if empty
  } catch (err: any) {
    showToast('Erro ao carregar mesas', 'error')
  }
});

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

async function handleFormSubmit(data: Omit<Table, 'tableid'>) {
  try {
    if (formMode.value === 'create') {
      await tablesStore.createTable(data)
      showToast('Mesa criada com sucesso', 'success')
    } else if (selectedTable.value) {
      await tablesStore.updateTable(selectedTable.value.tableid, data)
      showToast('Mesa atualizada com sucesso', 'success')
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
    await tablesStore.deleteTable(id)
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
