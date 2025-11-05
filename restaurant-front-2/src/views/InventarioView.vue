<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import type { InventoryItem } from '@/types/models'
import InventoryTableAdvanced from '@/components/inventory/InventoryTableAdvanced.vue'
import InventoryForm from '@/components/inventory/InventoryForm.vue'
import DeleteInventoryDialog from '@/components/inventory/DeleteInventoryDialog.vue'
import { useInventoryStore } from '@/stores/inventory'
import { useMenuStore } from '@/stores/menu'

const inventoryStore = useInventoryStore()
const menuStore = useMenuStore()

onMounted(async () => {
  // Fetch both inventory items and menu items
  await Promise.all([
    inventoryStore.fetchItems(),
    menuStore.fetchItems()
  ])
})

const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')
const formOpen = ref(false)
const deleteDialogOpen = ref(false)
const selectedItem = ref<InventoryItem | null>(null)
const formMode = ref<'create' | 'edit'>('create')

// Enrich inventory items with menu item names
const itemsWithMenuItemName = computed(() => {
  const menuItemMap = new Map(
    menuStore.items.map(item => [item.itemID, item.name])
  )

  return inventoryStore.items.map(item => ({
    ...item,
    menuItemName: menuItemMap.get(item.menu_item) || 'Unknown'
  }))
})

const isLoading = computed(() => inventoryStore.isLoading || menuStore.isLoading)

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

function openEditDialog(item: InventoryItem) {
  selectedItem.value = item
  formMode.value = 'edit'
  formOpen.value = true
}

function openDeleteDialog(item: InventoryItem) {
  selectedItem.value = item
  deleteDialogOpen.value = true
}

async function handleFormSubmit(data: Omit<InventoryItem, 'itemID'>) {
  try {
    if (formMode.value === 'create') {
      await inventoryStore.createItem(data)
      showToast('Item de inventário criado com sucesso', 'success')
    } else if (selectedItem.value) {
      await inventoryStore.updateItem(selectedItem.value.itemID, data)
      showToast('Item de inventário atualizado com sucesso', 'success')
    }
  } catch (error: any) {
    showToast(
      formMode.value === 'create' ? 'Erro ao criar item de inventário' : 'Erro ao atualizar item de inventário',
      'error'
    )
    throw error // Re-throw to keep form open
  }
}

async function handleDelete(id: number) {
  try {
    await inventoryStore.deleteItem(id)
    showToast('Item de inventário eliminado com sucesso', 'success')
  } catch (error: any) {
    showToast('Erro ao eliminar item de inventário', 'error')
    throw error
  }
}

// Helper to get menu item name for delete dialog
const selectedItemMenuName = computed(() => {
  if (!selectedItem.value) return undefined
  const menuItem = menuStore.items.find(item => item.itemID === selectedItem.value!.menu_item)
  return menuItem?.name
})
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
        <p class="text-muted-foreground">A carregar inventário...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="flex flex-col gap-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Inventário</h1>
          <p class="text-muted-foreground mt-1">Gerir o inventário e stock do restaurante</p>
        </div>
        <Button @click="openCreateDialog" size="default">
          <Plus class="mr-2 h-4 w-4" />
          Novo Item
        </Button>
      </div>

      <InventoryTableAdvanced
        :items="itemsWithMenuItemName"
        @edit="openEditDialog"
        @delete="openDeleteDialog"
      />
    </div>

    <!-- Inventory Form Dialog -->
    <InventoryForm
      v-model:open="formOpen"
      :item="selectedItem || undefined"
      :mode="formMode"
      :menu-items="menuStore.items"
      @submit="handleFormSubmit"
    />

    <!-- Delete Confirmation Dialog -->
    <DeleteInventoryDialog
      v-model:open="deleteDialogOpen"
      :item="selectedItem"
      :menu-item-name="selectedItemMenuName"
      @confirm="handleDelete"
    />
  </div>
</template>
