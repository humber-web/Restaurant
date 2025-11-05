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
import type { InventoryItem, MenuItem } from '@/types/models'

interface Props {
  open: boolean
  item?: InventoryItem
  mode: 'create' | 'edit'
  menuItems: MenuItem[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  submit: [data: Omit<InventoryItem, 'itemID'>]
}>()

const menuItem = ref<number>(0)
const quantity = ref<number>(0)
const reservedQuantity = ref<number>(0)
const supplier = ref('')
const oversellQuantity = ref<number>(0)
const isSubmitting = ref(false)

watch(() => props.open, (isOpen) => {
  if (isOpen && props.item) {
    menuItem.value = props.item.menu_item
    quantity.value = props.item.quantity
    reservedQuantity.value = props.item.reserved_quantity
    supplier.value = props.item.supplier
    oversellQuantity.value = props.item.oversell_quantity
  } else if (isOpen) {
    menuItem.value = 0
    quantity.value = 0
    reservedQuantity.value = 0
    supplier.value = ''
    oversellQuantity.value = 0
  }
})

async function handleSubmit(e: Event) {
  e.preventDefault()
  if (!menuItem.value) return

  isSubmitting.value = true
  try {
    emit('submit', {
      menu_item: menuItem.value,
      quantity: quantity.value,
      reserved_quantity: reservedQuantity.value,
      supplier: supplier.value.trim(),
      oversell_quantity: oversellQuantity.value,
    })
    emit('update:open', false)
    // Reset form
    menuItem.value = 0
    quantity.value = 0
    reservedQuantity.value = 0
    supplier.value = ''
    oversellQuantity.value = 0
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
    menuItem.value = 0
    quantity.value = 0
    reservedQuantity.value = 0
    supplier.value = ''
    oversellQuantity.value = 0
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-[425px]">
      <DialogHeader>
        <DialogTitle>{{ mode === 'create' ? 'Novo Item de Inventário' : 'Editar Item de Inventário' }}</DialogTitle>
        <DialogDescription>
          {{ mode === 'create' ? 'Adicione um novo item ao inventário.' : 'Atualize as informações do item de inventário.' }}
        </DialogDescription>
      </DialogHeader>
      <form @submit="handleSubmit">
        <div class="grid gap-4 py-4">
          <div class="grid gap-2">
            <Label for="menu-item">Item de Menu</Label>
            <Select v-model="menuItem" :disabled="mode === 'edit'">
              <SelectTrigger id="menu-item">
                <SelectValue placeholder="Selecione um item de menu" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="item in menuItems"
                  :key="item.itemID"
                  :value="item.itemID"
                >
                  {{ item.name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="grid gap-2">
            <Label for="quantity">Quantidade</Label>
            <Input
              id="quantity"
              v-model.number="quantity"
              type="number"
              min="0"
              placeholder="0"
              required
            />
          </div>
          <div class="grid gap-2">
            <Label for="reserved-quantity">Quantidade Reservada</Label>
            <Input
              id="reserved-quantity"
              v-model.number="reservedQuantity"
              type="number"
              min="0"
              placeholder="0"
            />
          </div>
          <div class="grid gap-2">
            <Label for="oversell-quantity">Quantidade de Sobrevenda</Label>
            <Input
              id="oversell-quantity"
              v-model.number="oversellQuantity"
              type="number"
              min="0"
              placeholder="0"
            />
          </div>
          <div class="grid gap-2">
            <Label for="supplier">Fornecedor</Label>
            <Input
              id="supplier"
              v-model="supplier"
              placeholder="Nome do fornecedor"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" @click="handleOpenChange(false)" :disabled="isSubmitting">
            Cancelar
          </Button>
          <Button type="submit" :disabled="isSubmitting || !menuItem">
            {{ isSubmitting ? 'A guardar...' : mode === 'create' ? 'Criar' : 'Guardar' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
