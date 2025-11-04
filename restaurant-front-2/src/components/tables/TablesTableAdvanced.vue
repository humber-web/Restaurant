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
import type { Table } from '@/types/models'

interface Props {
  tables: Table[]
}

defineProps<Props>()

const emit = defineEmits<{
  edit: [table: Table]
  delete: [table: Table]
}>()


// Define columns using TanStack Table
const columns: ColumnDef<Table>[] = [
  {
    accessorKey: 'tableid',
    header: createSortableHeader('ID', 'tableid'),
    cell: ({ row }) => h('span', { class: 'font-mono text-sm text-muted-foreground' }, row.getValue('tableid')),
    enableHiding: true,
    meta: {
      label: 'ID',
    },
  },
  {
    accessorKey: 'capacity',
    header: createSortableHeader('Capacidade', 'capacity'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('capacity')),
    enableHiding: true,
    meta: {
      label: 'Capacidade',
    },
  },
  {
    accessorKey: 'status',
    header: createSortableHeader('Estado', 'status'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('status')),
    enableHiding: true,
    meta: {
      label: 'Estado',
    },
  },

  createActionsColumn('actions', (table: Table) => {
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
                    onClick: () => emit('edit', table),
                  },
                  {
                    default: () => [h(Pencil, { class: 'mr-2 h-4 w-4' }), 'Editar'],
                  }
                ),
                h(
                  DropdownMenuItem,
                  {
                    onClick: () => emit('delete', table),
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
    :data="tables"
    :columns="columns"
    search-key="tableid"
    search-placeholder="Pesquisar mesas..."
  >
    <template #empty>
      <p class="text-muted-foreground">Nenhuma mesa encontrada</p>
    </template>
  </DataTableAdvanced>
</template>
