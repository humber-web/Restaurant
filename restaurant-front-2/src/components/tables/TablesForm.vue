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
import type { Table } from '@/types/models'

interface Props {
  open: boolean
  table?: Table
  mode: 'create' | 'edit'
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  submit: [data: Omit<Table, 'tableid'>]
}>()

const capacity = ref('')
const status = ref<Table['status']>('AV')
const isSubmitting = ref(false)

const statusOptions = [
  { value: 'AV', label: 'Ativo' },
  { value: 'OC', label: 'Ocupado' },
  { value: 'RE', label: 'Reservado' },
]

watch(() => props.open, (isOpen) => {
  if (isOpen && props.table) {
    capacity.value = props.table.capacity.toString()
    status.value = props.table.status
  } else if (isOpen) {
    capacity.value = ''
    status.value = 'AV'
  }
})

async function handleSubmit(e: Event) {
  e.preventDefault()
  if (!capacity.value.trim()) return

  isSubmitting.value = true
  try {
    emit('submit', {
      capacity: parseInt(capacity.value.trim(), 10),
      status: status.value,
    })
    emit('update:open', false)
    // Reset form
    capacity.value = ''
    status.value = 'AV'
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
    capacity.value = ''
    status.value = 'AV'
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>{{ mode === 'create' ? 'Nova Mesa' : 'Editar Mesa' }}</DialogTitle>
        <DialogDescription>
          {{ mode === 'create' ? 'Adicione uma nova mesa.' : 'Atualize as informações da mesa.' }}
        </DialogDescription>
      </DialogHeader>
      <form @submit="handleSubmit">
        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <Label for="capacity">Capacidade</Label>
            <Input
              id="capacity"
              v-model="capacity"
              placeholder="Ex: 2, 4, 6..."
              required
            />
          </div>
          <div class="grid gap-2">
            <Label for="prepared-in">Estado</Label>
            <Select v-model="status">
              <SelectTrigger id="prepared-in">
                <SelectValue placeholder="Selecione o estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="option in statusOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" @click="handleOpenChange(false)" :disabled="isSubmitting">
            Cancelar
          </Button>
          <Button type="submit" :disabled="isSubmitting || !capacity.trim()">
            {{ isSubmitting ? 'A guardar...' : mode === 'create' ? 'Criar' : 'Guardar' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
