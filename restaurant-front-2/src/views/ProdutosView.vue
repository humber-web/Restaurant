<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { Plus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import type { MenuItem } from '@/types/models'
import ProductsTableAdvanced from '@/components/produts/ProductsTableAdvanced.vue'
import ProductFormDialog from '@/components/produts/ProductFormDialog.vue'
import DeleteProductDialog from '@/components/produts/DeleteProductDialog.vue'
import { useMenuStore } from '@/stores/menu'

const menuStore = useMenuStore()

onMounted(async () => {
  // Fetch both items and categories
  await Promise.all([
    menuStore.fetchItems(),
    menuStore.fetchCategories()
  ])
})

const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')
const formOpen = ref(false)
const deleteDialogOpen = ref(false)
const selectedItem = ref<MenuItem | null>(null)
const formMode = ref<'create' | 'edit'>('create')

// Enrich items with category names
const itemsWithCategory = computed(() => {
  const categoryMap = new Map(
    menuStore.categories.map(cat => [cat.categoryID, cat.name])
  )

  return menuStore.items.map(item => ({
    ...item,
    category: categoryMap.get(item.categoryID) || 'Unknown'
  }))
})

const isLoading = computed(() => menuStore.isLoading)

function showToast(message: string, variant: 'success' | 'error') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

function openCreateDialog() {
  selectedItem.value = null
  formMode.value = 'create'
  formOpen.value = true
}

function openEditDialog(item: MenuItem) {
  selectedItem.value = item
  formMode.value = 'edit'
  formOpen.value = true
}

function openDeleteDialog(item: MenuItem) {
  selectedItem.value = item
  deleteDialogOpen.value = true
}

async function handleFormSubmit(data: Omit<MenuItem, 'itemID'>) {
  try {
    if (formMode.value === 'create') {
      await menuStore.createItem(data)
      showToast('Produto criado com sucesso', 'success')
    } else if (selectedItem.value) {
      await menuStore.updateItem(selectedItem.value.itemID, data)
      showToast('Produto atualizado com sucesso', 'success')
    }
  } catch (error: any) {
    showToast(
      formMode.value === 'create' ? 'Erro ao criar produto' : 'Erro ao atualizar produto',
      'error'
    )
    throw error // Re-throw to keep form open
  }
}

async function handleDelete(id: number) {
  try {
    await menuStore.deleteItem(id)
    showToast('Produto eliminado com sucesso', 'success')
  } catch (error: any) {
    showToast('Erro ao eliminar produto', 'error')
    throw error
  }
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
        <p class="text-muted-foreground">A carregar produtos...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="flex flex-col gap-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Produtos</h1>
          <p class="text-muted-foreground mt-1">Gerir os produtos do menu do restaurante</p>
        </div>
        <Button @click="openCreateDialog" size="default">
          <Plus class="mr-2 h-4 w-4" />
          Novo Produto
        </Button>
      </div>

      <ProductsTableAdvanced
        :items="itemsWithCategory"
        @edit="openEditDialog"
        @delete="openDeleteDialog"
      />
    </div>

    <!-- Product Form Dialog -->
    <ProductFormDialog
      v-model:open="formOpen"
      :product="selectedItem || undefined"
      :mode="formMode"
      @submit="handleFormSubmit"
    />

    <!-- Delete Confirmation Dialog -->
    <DeleteProductDialog
      v-model:open="deleteDialogOpen"
      :product="selectedItem"
      @confirm="handleDelete"
    />
  </div>
</template>
