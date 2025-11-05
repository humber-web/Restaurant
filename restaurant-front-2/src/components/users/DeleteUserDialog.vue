<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import type { User } from '@/types/models'

interface Props {
  open: boolean
  user: User | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  confirm: [id: number]
}>()

const isDeleting = ref(false)

async function handleConfirm() {
  if (!props.user) return

  isDeleting.value = true
  try {
    await emit('confirm', props.user.id)
    emit('update:open', false)
  } catch (error) {
    // Error handled by parent
  } finally {
    isDeleting.value = false
  }
}

function handleOpenChange(open: boolean) {
  emit('update:open', open)
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>Eliminar Utilizador?</DialogTitle>
        <DialogDescription>
          Tem a certeza que deseja eliminar o utilizador <strong>{{ user?.username }}</strong>?
          Esta ação não pode ser revertida.
        </DialogDescription>
      </DialogHeader>
      <DialogFooter>
        <Button variant="outline" @click="handleOpenChange(false)" :disabled="isDeleting">
          Cancelar
        </Button>
        <Button variant="destructive" @click="handleConfirm" :disabled="isDeleting">
          {{ isDeleting ? 'A eliminar...' : 'Eliminar' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
