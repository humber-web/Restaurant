<script setup lang="ts">
import { ref, watch } from 'vue'
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
import type { User, Group } from '@/types/models'
import type { CreateUserPayload } from '@/services/api/users'

interface Props {
  open: boolean
  user?: User
  mode: 'create' | 'edit'
  groups: Group[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  submit: [data: CreateUserPayload | Partial<User>]
}>()

const username = ref('')
const email = ref('')
const password = ref('')
const selectedGroup = ref('')
const isSubmitting = ref(false)

watch(() => props.open, (isOpen) => {
  if (isOpen && props.user) {
    username.value = props.user.username
    email.value = props.user.email
    password.value = '' // Don't pre-fill password on edit
    // Get the first group name if available
    selectedGroup.value = props.groups.find(g => props.user?.groups.includes(g.id))?.name || ''
  } else if (isOpen) {
    username.value = ''
    email.value = ''
    password.value = ''
    selectedGroup.value = ''
  }
})

async function handleSubmit(e: Event) {
  e.preventDefault()

  // Validation
  if (!username.value.trim() || !email.value.trim()) return
  if (props.mode === 'create' && !password.value) return

  isSubmitting.value = true
  try {
    if (props.mode === 'create') {
      await emit('submit', {
        username: username.value.trim(),
        email: email.value.trim(),
        password: password.value,
        group: selectedGroup.value || undefined,
      } as CreateUserPayload)
    } else {
      // For edit, only send changed fields
      const updateData: Partial<User> = {
        username: username.value.trim(),
        email: email.value.trim(),
      }
      // Only include password if it was changed
      if (password.value) {
        (updateData as any).password = password.value
      }
      await emit('submit', updateData)
    }
    emit('update:open', false)
    // Reset form
    username.value = ''
    email.value = ''
    password.value = ''
    selectedGroup.value = ''
  } catch (error) {
    // Error handled by parent, keep form open
    console.error('Form submission error:', error)
  } finally {
    isSubmitting.value = false
  }
}

function handleOpenChange(open: boolean) {
  emit('update:open', open)
  if (!open) {
    username.value = ''
    email.value = ''
    password.value = ''
    selectedGroup.value = ''
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>{{ mode === 'create' ? 'Novo Utilizador' : 'Editar Utilizador' }}</DialogTitle>
        <DialogDescription>
          {{ mode === 'create' ? 'Adicione um novo utilizador ao sistema.' : 'Atualize as informações do utilizador.' }}
        </DialogDescription>
      </DialogHeader>
      <form @submit="handleSubmit">
        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <Label for="username">Username</Label>
            <Input
              id="username"
              v-model="username"
              placeholder="nome_utilizador"
              required
              :disabled="mode === 'edit'"
            />
          </div>
          <div class="grid gap-2">
            <Label for="email">Email</Label>
            <Input
              id="email"
              v-model="email"
              type="email"
              placeholder="utilizador@exemplo.com"
              required
            />
          </div>
          <div class="grid gap-2">
            <Label for="password">
              Password
              <span v-if="mode === 'edit'" class="text-xs text-muted-foreground">(deixe em branco para manter)</span>
            </Label>
            <Input
              id="password"
              v-model="password"
              type="password"
              placeholder="••••••••"
              :required="mode === 'create'"
            />
          </div>
          <div v-if="mode === 'create'" class="grid gap-2">
            <Label for="group">Grupo</Label>
            <Select v-model="selectedGroup">
              <SelectTrigger id="group">
                <SelectValue placeholder="Selecione um grupo (opcional)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="group in groups"
                  :key="group.id"
                  :value="group.name"
                >
                  {{ group.name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" @click="handleOpenChange(false)" :disabled="isSubmitting">
            Cancelar
          </Button>
          <Button type="submit" :disabled="isSubmitting || !username.trim() || !email.trim() || (mode === 'create' && !password)">
            {{ isSubmitting ? 'A guardar...' : mode === 'create' ? 'Criar' : 'Guardar' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
