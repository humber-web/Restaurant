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
import type { MenuItem } from '@/types/models'

interface Props {
  items: MenuItem[]
}

defineProps<Props>()

const emit = defineEmits<{
  edit: [item: MenuItem]
  delete: [item: MenuItem]
}>()



// Define columns using TanStack Table
const columns: ColumnDef<MenuItem>[] = [
  {
    accessorKey: 'itemID',
    header: createSortableHeader('ID', 'itemID'),
    cell: ({ row }) => h('span', { class: 'font-mono text-sm text-muted-foreground' }, row.getValue('itemID')),
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
    accessorKey: 'description',
    header: createSortableHeader('Descrição', 'description'),
    cell: ({ row }) => h('span', {}, row.getValue('description')),
    enableHiding: true,
    meta: {
      label: 'Descrição',
    },
  },
  {
    accessorKey: 'ingredients',
    header: createSortableHeader('Ingredientes', 'ingredients'),
    cell: ({ row }) => h('span', {}, row.getValue('ingredients')),
    enableHiding: true,
    meta: {
      label: 'Ingredientes',
    },
  },

  {
    accessorKey: 'price',
    header: createSortableHeader('Preço', 'price'),
    cell: ({ row }) =>
      h(
        'span',
        { class: 'font-mono' },
        `${Number(row.getValue('price')).toFixed(2)} CVE`
      ),
    enableHiding: true,
    meta: {
      label: 'Preço',
    },
  },
  {
    accessorKey: 'category',
    header: createSortableHeader('Categoria', 'category'),
    cell: ({ row }) => h('span', {}, row.getValue('category')),
    enableHiding: true,
    meta: {
      label: 'Categoria',
    },
  },
  {
    accessorKey: 'availability',
    header: createSortableHeader('Disponibilidade', 'availability'),
    cell: ({ row }) =>
      h('span', {}, row.getValue('availability') ? 'Disponível' : 'Indisponível'),
    enableHiding: true,
    meta: {
      label: 'Disponibilidade',
    },
  },

  {
    accessorKey: 'is_quantifiable',
    header: createSortableHeader('Quantificável', 'is_quantifiable'),
    cell: ({ row }) =>
      h('span', {}, row.getValue('is_quantifiable') ? 'Sim' : 'Não'),
    enableHiding: true,
    meta: {
      label: 'Quantificável',
    },
  },

  createActionsColumn('actions', (item: MenuItem) => {
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
                    onClick: () => emit('edit', item),
                  },
                  {
                    default: () => [h(Pencil, { class: 'mr-2 h-4 w-4' }), 'Editar'],
                  }
                ),
                h(
                  DropdownMenuItem,
                  {
                    onClick: () => emit('delete', item),
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
    :data="items"
    :columns="columns"
    search-key="name"
    search-placeholder="Pesquisar produtos..."
  >
    <template #empty>
      <p class="text-muted-foreground">Nenhum produto encontrado</p>
    </template>
  </DataTableAdvanced>
</template>
