<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import type { User } from '@/types/models'
import type { CreateUserPayload } from '@/services/api/users'
import UsersTableAdvanced from '@/components/users/UsersTableAdvanced.vue'
import UserForm from '@/components/users/UserForm.vue'
import DeleteUserDialog from '@/components/users/DeleteUserDialog.vue'
import { useUsersStore } from '@/stores/users'

const usersStore = useUsersStore()

onMounted(async () => {
  // Fetch both users and groups
  await Promise.all([
    usersStore.fetchUsers(),
    usersStore.fetchGroups()
  ])
})

const toastMessage = ref<string | null>(null)
const toastVariant = ref<'success' | 'error'>('success')
const formOpen = ref(false)
const deleteDialogOpen = ref(false)
const selectedUser = ref<User | null>(null)
const formMode = ref<'create' | 'edit'>('create')

// Enrich users with group names
const usersWithGroupNames = computed(() => {
  const groupMap = new Map(
    usersStore.groups.map(group => [group.id, group.name])
  )

  return usersStore.users.map(user => ({
    ...user,
    groupNames: user.groups.map(gid => groupMap.get(gid)).filter(Boolean).join(', ')
  }))
})

const isLoading = computed(() => usersStore.isLoading)

function showToast(message: string, variant: 'success' | 'error') {
  toastMessage.value = message
  toastVariant.value = variant
  setTimeout(() => {
    toastMessage.value = null
  }, 3000)
}

function openCreateDialog() {
  selectedUser.value = null
  formMode.value = 'create'
  formOpen.value = true
}

function openEditDialog(user: User) {
  selectedUser.value = user
  formMode.value = 'edit'
  formOpen.value = true
}

function openDeleteDialog(user: User) {
  selectedUser.value = user
  deleteDialogOpen.value = true
}

async function handleFormSubmit(data: CreateUserPayload | Partial<User>) {
  try {
    if (formMode.value === 'create') {
      await usersStore.createUser(data as CreateUserPayload)
      showToast('Utilizador criado com sucesso', 'success')
    } else if (selectedUser.value) {
      await usersStore.updateUser(selectedUser.value.id, data as Partial<User>)
      showToast('Utilizador atualizado com sucesso', 'success')
    }
  } catch (error: any) {
    showToast(
      formMode.value === 'create' ? 'Erro ao criar utilizador' : 'Erro ao atualizar utilizador',
      'error'
    )
    throw error // Re-throw to keep form open
  }
}

async function handleDelete(id: number) {
  try {
    await usersStore.deleteUser(id)
    showToast('Utilizador eliminado com sucesso', 'success')
  } catch (error: any) {
    showToast('Erro ao eliminar utilizador', 'error')
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
        <p class="text-muted-foreground">A carregar utilizadores...</p>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="flex flex-col gap-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight">Utilizadores</h1>
          <p class="text-muted-foreground mt-1">Gerir os utilizadores do sistema</p>
        </div>
        <Button @click="openCreateDialog" size="default">
          <Plus class="mr-2 h-4 w-4" />
          Novo Utilizador
        </Button>
      </div>

      <UsersTableAdvanced
        :users="usersWithGroupNames"
        @edit="openEditDialog"
        @delete="openDeleteDialog"
      />
    </div>

    <!-- User Form Dialog -->
    <UserForm
      v-model:open="formOpen"
      :user="selectedUser || undefined"
      :mode="formMode"
      :groups="usersStore.groups"
      @submit="handleFormSubmit"
    />

    <!-- Delete Confirmation Dialog -->
    <DeleteUserDialog
      v-model:open="deleteDialogOpen"
      :user="selectedUser"
      @confirm="handleDelete"
    />
  </div>
</template>
