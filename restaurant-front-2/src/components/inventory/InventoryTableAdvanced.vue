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
import type { InventoryItem } from '@/types/models'

interface InventoryItemWithMenuItem extends InventoryItem {
  menuItemName?: string
}

interface Props {
  items: InventoryItemWithMenuItem[]
}

defineProps<Props>()

const emit = defineEmits<{
  edit: [item: InventoryItem]
  delete: [item: InventoryItem]
}>()

// Define columns using TanStack Table
const columns: ColumnDef<InventoryItemWithMenuItem>[] = [
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
    accessorKey: 'menuItemName',
    header: createSortableHeader('Item de Menu', 'menuItemName'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('menuItemName') || 'N/A'),
    enableHiding: true,
    meta: {
      label: 'Item de Menu',
    },
  },
  {
    accessorKey: 'quantity',
    header: createSortableHeader('Quantidade', 'quantity'),
    cell: ({ row }) => {
      const quantity = row.getValue('quantity') as number
      return h(
        'span',
        {
          class: [
            'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
            quantity > 10 ? 'bg-green-100 text-green-800' : quantity > 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800',
          ],
        },
        String(quantity)
      )
    },
    enableHiding: true,
    meta: {
      label: 'Quantidade',
    },
  },
  {
    accessorKey: 'reserved_quantity',
    header: createSortableHeader('Reservado', 'reserved_quantity'),
    cell: ({ row }) => h('span', { class: 'text-sm' }, row.getValue('reserved_quantity')),
    enableHiding: true,
    meta: {
      label: 'Reservado',
    },
  },
  {
    accessorKey: 'oversell_quantity',
    header: createSortableHeader('Sobrevenda', 'oversell_quantity'),
    cell: ({ row }) => h('span', { class: 'text-sm' }, row.getValue('oversell_quantity')),
    enableHiding: true,
    meta: {
      label: 'Sobrevenda',
    },
  },
  {
    accessorKey: 'supplier',
    header: createSortableHeader('Fornecedor', 'supplier'),
    cell: ({ row }) => h('span', { class: 'text-sm' }, row.getValue('supplier') || '-'),
    enableHiding: true,
    meta: {
      label: 'Fornecedor',
    },
  },
  createActionsColumn('actions', (item: InventoryItem) => {
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
    search-key="menuItemName"
    search-placeholder="Pesquisar itens de inventário..."
  >
    <template #empty>
      <p class="text-muted-foreground">Nenhum item de inventário encontrado</p>
    </template>
  </DataTableAdvanced>
</template>
