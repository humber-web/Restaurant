<script setup lang="ts">
import { computed } from 'vue'
import { MoreHorizontal, Pencil, Trash2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import DataTable, { type Column } from '@/components/shared/DataTable.vue'
import type { MenuCategory, PreparedIn } from '@/types/models'

interface Props {
  categories: MenuCategory[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  edit: [category: MenuCategory]
  delete: [category: MenuCategory]
}>()

const preparedInConfig: Record<PreparedIn, { label: string; variant: 'default' | 'secondary' | 'outline' }> = {
  '1': { label: 'Cozinha', variant: 'default' },
  '2': { label: 'Bar', variant: 'secondary' },
  '3': { label: 'Ambos', variant: 'outline' },
}

const columns = computed<Column<MenuCategory>[]>(() => [
  {
    key: 'categoryID',
    label: 'ID',
    sortable: true,
    width: 'w-[100px]',
  },
  {
    key: 'name',
    label: 'Nome',
    sortable: true,
  },
  {
    key: 'prepared_in',
    label: 'Preparado em',
    sortable: true,
  },
])

</script>

<template>
  <DataTable
    :data="categories"
    :columns="columns"
    search-placeholder="Pesquisar categorias..."
    :page-size="10"
  >
    <!-- Custom cell for categoryID -->
    <template #cell-categoryID="{ value }">
      <span class="font-mono text-sm text-muted-foreground">{{ value }}</span>
    </template>

    <!-- Custom cell for name -->
    <template #cell-name="{ value }">
      <span class="font-medium">{{ value }}</span>
    </template>

    <!-- Custom cell for prepared_in -->
    <template #cell-prepared_in="{ value }">
      <span
        class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold"
        :class="{
          'bg-primary text-primary-foreground': preparedInConfig[value as PreparedIn].variant === 'default',
          'bg-secondary text-secondary-foreground': preparedInConfig[value as PreparedIn].variant === 'secondary',
          'border border-input bg-background': preparedInConfig[value as PreparedIn].variant === 'outline'
        }"
      >
        {{ preparedInConfig[value as PreparedIn].label }}
      </span>
    </template>

    <!-- Header actions column -->
    <template #header-actions>
      <th class="w-20">
        <span class="sr-only">Ações</span>
      </th>
    </template>

    <!-- Row actions -->
    <template #row-actions="{ row }">
      <td class="text-right">
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
              variant="ghost"
              size="icon"
              class="h-8 w-8"
            >
              <MoreHorizontal class="h-4 w-4" />
              <span class="sr-only">Abrir menu</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Ações</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="emit('edit', row)">
              <Pencil class="mr-2 h-4 w-4" />
              Editar
            </DropdownMenuItem>
            <DropdownMenuItem 
              @click="emit('delete', row)"
              class="text-destructive focus:text-destructive"
            >
              <Trash2 class="mr-2 h-4 w-4" />
              Eliminar
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </td>
    </template>

    <!-- Empty state -->
    <template #empty>
      <p class="text-muted-foreground">Nenhuma categoria encontrada</p>
    </template>
  </DataTable>
</template>
