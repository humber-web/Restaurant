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
import type { MenuCategory, PreparedIn } from '@/types/models'

interface Props {
  open: boolean
  category?: MenuCategory
  mode: 'create' | 'edit'
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  submit: [data: Omit<MenuCategory, 'categoryID'>]
}>()

const name = ref('')
const preparedIn = ref<PreparedIn>('1')
const isSubmitting = ref(false)

const preparedInOptions = [
  { value: '1', label: 'Cozinha' },
  { value: '2', label: 'Bar' },
  { value: '3', label: 'Ambos' },
]

watch(() => props.open, (isOpen) => {
  if (isOpen && props.category) {
    name.value = props.category.name
    preparedIn.value = props.category.prepared_in
  } else if (isOpen) {
    name.value = ''
    preparedIn.value = '1'
  }
})

async function handleSubmit(e: Event) {
  e.preventDefault()
  if (!name.value.trim()) return

  isSubmitting.value = true
  try {
    await emit('submit', {
      name: name.value.trim(),
      prepared_in: preparedIn.value,
    })
    emit('update:open', false)
    // Reset form
    name.value = ''
    preparedIn.value = '1'
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
    name.value = ''
    preparedIn.value = '1'
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>{{ mode === 'create' ? 'Nova Categoria' : 'Editar Categoria' }}</DialogTitle>
        <DialogDescription>
          {{ mode === 'create' ? 'Adicione uma nova categoria ao menu.' : 'Atualize as informações da categoria.' }}
        </DialogDescription>
      </DialogHeader>
      <form @submit="handleSubmit">
        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <Label for="name">Nome</Label>
            <Input
              id="name"
              v-model="name"
              placeholder="Ex: Entradas, Pratos Principais..."
              required
            />
          </div>
          <div class="grid gap-2">
            <Label for="prepared-in">Preparado em</Label>
            <Select v-model="preparedIn">
              <SelectTrigger id="prepared-in">
                <SelectValue placeholder="Selecione onde é preparado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="option in preparedInOptions"
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
          <Button type="submit" :disabled="isSubmitting || !name.trim()">
            {{ isSubmitting ? 'A guardar...' : mode === 'create' ? 'Criar' : 'Guardar' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
