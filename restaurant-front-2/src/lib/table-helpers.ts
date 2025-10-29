import { h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { Button } from '@/components/ui/button'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-vue-next'

/**
 * Helper to create a sortable column header
 */
export function createSortableHeader<TData>(label: string, accessorKey: string) {
  return ({ column }: any) => {
    return h(
      Button,
      {
        variant: 'ghost',
        onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
      },
      () => [
        label,
        column.getIsSorted() === 'asc'
          ? h(ArrowUp, { class: 'ml-2 h-4 w-4' })
          : column.getIsSorted() === 'desc'
          ? h(ArrowDown, { class: 'ml-2 h-4 w-4' })
          : h(ArrowUpDown, { class: 'ml-2 h-4 w-4' }),
      ]
    )
  }
}

/**
 * Helper to create a simple text column
 */
export function createTextColumn<TData>(
  accessorKey: string,
  header: string,
  options?: {
    sortable?: boolean
    className?: string
  }
): ColumnDef<TData> {
  return {
    accessorKey,
    header: options?.sortable !== false ? createSortableHeader(header, accessorKey) : header,
    cell: ({ row }: any) => {
      const value = row.getValue(accessorKey)
      return h('div', { class: options?.className }, String(value))
    },
  }
}

/**
 * Helper to create a custom cell column
 */
export function createCustomColumn<TData>(
  accessorKey: string,
  header: string,
  cellRenderer: (value: any, row: TData) => any,
  options?: {
    sortable?: boolean
  }
): ColumnDef<TData> {
  return {
    accessorKey,
    header: options?.sortable !== false ? createSortableHeader(header, accessorKey) : header,
    cell: ({ row }: any) => cellRenderer(row.getValue(accessorKey), row.original),
  }
}

/**
 * Helper to create an actions column
 */
export function createActionsColumn<TData>(
  id: string,
  cellRenderer: (row: TData) => any
): ColumnDef<TData> {
  return {
    id,
    enableHiding: false,
    cell: ({ row }: any) => cellRenderer(row.original),
  }
}
