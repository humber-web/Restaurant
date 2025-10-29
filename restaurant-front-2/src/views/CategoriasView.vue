<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import CategoriesTableAdvanced from '@/components/categories/CategoriesTableAdvanced.vue'
import CategoryForm from '@/components/categories/CategoryForm.vue'
import DeleteCategoryDialog from '@/components/categories/DeleteCategoryDialog.vue'
import { menuApi } from '@/services/api'
import type { MenuCategory } from '@/types/models'

const categories = ref<MenuCategory[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)
const formOpen = ref(false)
const deleteDialogOpen = ref(false)
const selectedCategory = ref<MenuCategory | null>(null)
const formMode = ref<'create' | 'edit'>('create')
const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')

onMounted(() => {
  fetchCategories()
})

async function fetchCategories() {
  isLoading.value = true
  error.value = null
  try {
    categories.value = await menuApi.getCategories()
  } catch (err: any) {
    error.value = err?.message || 'Erro ao carregar categorias'
    showToast('Erro ao carregar categorias', 'error')
  } finally {
    isLoading.value = false
  }
}

async function handleCreate(data: Omit<MenuCategory, 'categoryID'>) {
  const newCategory = await menuApi.createCategory(data)
  categories.value = [...categories.value, newCategory]
  showToast('Categoria criada com sucesso', 'success')
}

async function handleUpdate(data: Omit<MenuCategory, 'categoryID'>) {
  if (!selectedCategory.value) return
  const updated = await menuApi.updateCategory(selectedCategory.value.categoryID, data)
  categories.value = categories.value.map(cat => 
    cat.categoryID === selectedCategory.value!.categoryID ? updated : cat
  )
  showToast('Categoria atualizada com sucesso', 'success')
}

async function handleFormSubmit(data: Omit<MenuCategory, 'categoryID'>) {
  try {
    if (formMode.value === 'create') {
      await handleCreate(data)
    } else {
      await handleUpdate(data)
    }
  } catch (error: any) {
    showToast(
      formMode.value === 'create' ? 'Erro ao criar categoria' : 'Erro ao atualizar categoria',
      'error'
    )
    throw error // Re-throw to keep form open
  }
}

async function handleDelete(id: number) {
  try {
    await menuApi.deleteCategory(id)
    categories.value = categories.value.filter(cat => cat.categoryID !== id)
    showToast('Categoria eliminada com sucesso', 'success')
  } catch (error: any) {
    showToast('Erro ao eliminar categoria', 'error')
    throw error
  }
}

function openCreateDialog() {
  selectedCategory.value = null
  formMode.value = 'create'
  formOpen.value = true
}

function openEditDialog(category: MenuCategory) {
  selectedCategory.value = category
  formMode.value = 'edit'
  formOpen.value = true
}

function openDeleteDialog(category: MenuCategory) {
  selectedCategory.value = category
  deleteDialogOpen.value = true
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
        <p class="text-muted-foreground">A carregar categorias...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="flex flex-col gap-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Categorias</h1>
          <p class="text-muted-foreground mt-1">Gerir as categorias do menu do restaurante</p>
        </div>
        <Button @click="openCreateDialog" size="default">
          <Plus class="mr-2 h-4 w-4" />
          Nova Categoria
        </Button>
      </div>

      <CategoriesTableAdvanced
        :categories="categories"
        @edit="openEditDialog"
        @delete="openDeleteDialog"
      />
    </div>

    <!-- Category Form Dialog -->
    <CategoryForm
      v-model:open="formOpen"
      :category="selectedCategory || undefined"
      :mode="formMode"
      @submit="handleFormSubmit"
    />

    <!-- Delete Confirmation Dialog -->
    <DeleteCategoryDialog
      v-model:open="deleteDialogOpen"
      :category="selectedCategory"
      @confirm="handleDelete"
    />
  </div>
</template>
