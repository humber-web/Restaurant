<script setup lang="ts">
import { h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
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
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
import { createSortableHeader, createActionsColumn } from '@/lib/table-helpers'
import type { MenuCategory, PreparedIn } from '@/types/models'

interface Props {
  categories: MenuCategory[]
}

defineProps<Props>()

const emit = defineEmits<{
  edit: [category: MenuCategory]
  delete: [category: MenuCategory]
}>()

const preparedInConfig: Record<PreparedIn, { label: string; variant: 'default' | 'secondary' | 'outline' }> = {
  '1': { label: 'Cozinha', variant: 'default' },
  '2': { label: 'Bar', variant: 'secondary' },
  '3': { label: 'Ambos', variant: 'outline' },
}

// Define columns using TanStack Table
const columns: ColumnDef<MenuCategory>[] = [
  {
    accessorKey: 'categoryID',
    header: createSortableHeader('ID', 'categoryID'),
    cell: ({ row }) => h('span', { class: 'font-mono text-sm text-muted-foreground' }, row.getValue('categoryID')),
    enableHiding: true,
    meta: {
      label: 'ID',
    },
  },
  {
    accessorKey: 'name',
    header: createSortableHeader('Nome', 'name'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('name')),
    enableHiding: true,
    meta: {
      label: 'Nome',
    },
  },
  {
    accessorKey: 'prepared_in',
    header: createSortableHeader('Preparado em', 'prepared_in'),
    cell: ({ row }) => {
      const value = row.getValue('prepared_in') as PreparedIn
      const config = preparedInConfig[value]
      if (!config) return null
      return h(
        'span',
        {
          class: [
            'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
            config.variant === 'default' && 'bg-primary text-primary-foreground',
            config.variant === 'secondary' && 'bg-secondary text-secondary-foreground',
            config.variant === 'outline' && 'border border-input bg-background',
          ],
        },
        config.label
      )
    },
    enableHiding: true,
    meta: {
      label: 'Preparado em',
    },
  },
  createActionsColumn('actions', (category: MenuCategory) => {
    return h(
      DropdownMenu,
      {},
      {
        default: () => [
          h(
            DropdownMenuTrigger,
            { asChild: true },
            {
              default: () =>
                h(
                  Button,
                  {
                    variant: 'ghost',
                    size: 'icon',
                    class: 'h-8 w-8',
                  },
                  {
                    default: () => [
                      h(MoreHorizontal, { class: 'h-4 w-4' }),
                      h('span', { class: 'sr-only' }, 'Abrir menu'),
                    ],
                  }
                ),
            }
          ),
          h(
            DropdownMenuContent,
            { align: 'end' },
            {
              default: () => [
                h(DropdownMenuLabel, {}, { default: () => 'Ações' }),
                h(DropdownMenuSeparator),
                h(
                  DropdownMenuItem,
                  {
                    onClick: () => emit('edit', category),
                  },
                  {
                    default: () => [h(Pencil, { class: 'mr-2 h-4 w-4' }), 'Editar'],
                  }
                ),
                h(
                  DropdownMenuItem,
                  {
                    onClick: () => emit('delete', category),
                    class: 'text-destructive focus:text-destructive',
                  },
                  {
                    default: () => [h(Trash2, { class: 'mr-2 h-4 w-4' }), 'Eliminar'],
                  }
                ),
              ],
            }
          ),
        ],
      }
    )
  }),
]
</script>

<template>
  <DataTableAdvanced
    :data="categories"
    :columns="columns"
    search-key="name"
    search-placeholder="Pesquisar categorias..."
  >
    <template #empty>
      <p class="text-muted-foreground">Nenhuma categoria encontrada</p>
    </template>
  </DataTableAdvanced>
</template>
