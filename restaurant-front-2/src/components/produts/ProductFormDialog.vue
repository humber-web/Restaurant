<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
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
import type { MenuItem, MenuCategory } from '@/types/models'
import { menuApi } from '@/services/api'

interface Props {
  open: boolean
  product?: MenuItem
  mode: 'create' | 'edit'
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  submit: [data: Omit<MenuItem, 'itemID'>]
}>()

const name = ref('')
const description = ref('')
const ingredients = ref('')
const price = ref('')
const categoryID = ref<number | null>(null)
const availability = ref(true)
const isQuantifiable = ref(false)
const isSubmitting = ref(false)
const categories = ref<MenuCategory[]>([])
const isLoadingCategories = ref(false)

// Fetch categories on mount
onMounted(async () => {
  isLoadingCategories.value = true
  try {
    categories.value = await menuApi.getCategories()
  } catch (error) {
    console.error('Failed to load categories:', error)
  } finally {
    isLoadingCategories.value = false
  }
})

// Watch for dialog open and product changes
watch([() => props.open, () => props.product], ([isOpen, product]) => {
  if (isOpen) {
    if (product) {
      // Edit mode - populate form with existing data
      name.value = product.name
      description.value = product.description
      ingredients.value = product.ingredients || ''
      price.value = product.price.toString()
      categoryID.value = product.categoryID
      availability.value = product.availability
      isQuantifiable.value = product.is_quantifiable
    } else {
      // Create mode - reset form
      resetForm()
    }
  }
}, { immediate: true })

function resetForm() {
  name.value = ''
  description.value = ''
  ingredients.value = ''
  price.value = ''
  categoryID.value = null
  availability.value = true
  isQuantifiable.value = false
}

async function handleSubmit(e: Event) {
  e.preventDefault()
  if (!name.value.trim() || !description.value.trim() || !price.value || !categoryID.value) {
    return
  }

  isSubmitting.value = true
  try {
    emit('submit', {
      name: name.value.trim(),
      description: description.value.trim(),
      ingredients: ingredients.value.trim() || undefined,
      price: parseFloat(price.value),
      categoryID: categoryID.value,
      availability: availability.value,
      is_quantifiable: isQuantifiable.value,
    })
    emit('update:open', false)
    resetForm()
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
    resetForm()
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="handleOpenChange">
    <DialogContent class="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>{{ mode === 'create' ? 'Novo Produto' : 'Editar Produto' }}</DialogTitle>
        <DialogDescription>
          {{ mode === 'create' ? 'Adicione um novo produto ao menu.' : 'Atualize as informações do produto.' }}
        </DialogDescription>
      </DialogHeader>
      <form @submit="handleSubmit">
        <div class="grid gap-4 py-4">
          <!-- Name -->
          <div class="grid gap-2">
            <Label for="name">Nome <span class="text-destructive">*</span></Label>
            <Input
              id="name"
              v-model="name"
              placeholder="Ex: Pizza Margherita"
              required
            />
          </div>

          <!-- Description -->
          <div class="grid gap-2">
            <Label for="description">Descrição <span class="text-destructive">*</span></Label>
            <Textarea
              id="description"
              v-model="description"
              placeholder="Descreva o produto..."
              rows="3"
              required
            />
          </div>

          <!-- Ingredients -->
          <div class="grid gap-2">
            <Label for="ingredients">Ingredientes</Label>
            <Textarea
              id="ingredients"
              v-model="ingredients"
              placeholder="Liste os ingredientes (opcional)..."
              rows="2"
            />
          </div>

          <!-- Price and Category -->
          <div class="grid grid-cols-2 gap-4">
            <!-- Price -->
            <div class="grid gap-2">
              <Label for="price">Preço (CVE) <span class="text-destructive">*</span></Label>
              <Input
                id="price"
                v-model="price"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                required
              />
            </div>

            <!-- Category -->
            <div class="grid gap-2">
              <Label for="category">Categoria <span class="text-destructive">*</span></Label>
              <Select v-model:model-value="categoryID" required>
                <SelectTrigger id="category">
                  <SelectValue placeholder="Selecione uma categoria" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem
                    v-for="category in categories"
                    :key="category.categoryID"
                    :value="category.categoryID"
                  >
                    {{ category.name }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <!-- Checkboxes -->
          <div class="grid gap-3">
            <!-- Availability -->
            <div class="flex items-center space-x-2">
              <Checkbox
                id="availability"
                v-model:model-value="availability"
              />
              <Label for="availability" class="text-sm font-normal cursor-pointer">
                Disponível para venda
              </Label>
            </div>

            <!-- Is Quantifiable -->
            <div class="flex items-center space-x-2">
              <Checkbox
                id="quantifiable"
                v-model:model-value="isQuantifiable"
              />
              <Label for="quantifiable" class="text-sm font-normal cursor-pointer">
                Produto quantificável (pode ser vendido em múltiplas quantidades)
              </Label>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" @click="handleOpenChange(false)" :disabled="isSubmitting">
            Cancelar
          </Button>
          <Button
            type="submit"
            :disabled="isSubmitting || !name.trim() || !description.trim() || !price || !categoryID"
          >
            {{ isSubmitting ? 'A guardar...' : mode === 'create' ? 'Criar' : 'Guardar' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
