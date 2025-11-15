<script setup lang="ts">
import { h, computed } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { createSortableHeader } from '@/lib/table-helpers'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'

export interface CategorySalesData {
  categoryID: number
  name: string
  productCount: number
  totalQuantitySold: number
  revenue: number
  orderCount: number
  averageOrderValue: number
}

interface Props {
  categories: CategorySalesData[]
}

const props = defineProps<Props>()

// Calculate max revenue for progress bars
const maxRevenue = computed(() => {
  return Math.max(...props.categories.map(c => c.revenue), 1)
})

// Helper functions
function formatCurrency(value: number): string {
  return `CVE${value.toFixed(2)}`
}

function calculatePercentage(value: number, max: number): number {
  return (value / max) * 100
}

// Column definitions
const columns: ColumnDef<CategorySalesData>[] = [
  {
    accessorKey: 'categoryID',
    header: createSortableHeader('ID', 'categoryID'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, `#${row.getValue('categoryID')}`),
    enableHiding: true,
    meta: { label: 'ID' },
  },
  {
    accessorKey: 'name',
    header: createSortableHeader('Categoria', 'name'),
    cell: ({ row }) => h(Badge, { variant: 'default', class: 'text-base px-3 py-1' }, () => row.getValue('name')),
    enableHiding: true,
    meta: { label: 'Categoria' },
  },
  {
    accessorKey: 'productCount',
    header: createSortableHeader('Nº Produtos', 'productCount'),
    cell: ({ row }) => h('div', { class: 'text-center' }, row.getValue('productCount')),
    enableHiding: true,
    meta: { label: 'Nº Produtos' },
  },
  {
    accessorKey: 'totalQuantitySold',
    header: createSortableHeader('Total Vendido', 'totalQuantitySold'),
    cell: ({ row }) => h('div', { class: 'font-semibold text-center' }, row.getValue('totalQuantitySold')),
    enableHiding: true,
    meta: { label: 'Total Vendido' },
  },
  {
    accessorKey: 'orderCount',
    header: createSortableHeader('Nº Pedidos', 'orderCount'),
    cell: ({ row }) => h('div', { class: 'text-center' }, row.getValue('orderCount')),
    enableHiding: true,
    meta: { label: 'Nº Pedidos' },
  },
  {
    accessorKey: 'revenue',
    header: createSortableHeader('Receita', 'revenue'),
    cell: ({ row }) => {
      const revenue = row.getValue('revenue') as number
      const percentage = calculatePercentage(revenue, maxRevenue.value)

      return h('div', { class: 'space-y-1' }, [
        h('div', { class: 'font-semibold text-green-600' }, formatCurrency(revenue)),
        h(Progress, { modelValue: percentage, class: 'h-2' })
      ])
    },
    enableHiding: true,
    meta: { label: 'Receita' },
  },
  {
    accessorKey: 'averageOrderValue',
    header: createSortableHeader('Valor Médio/Pedido', 'averageOrderValue'),
    cell: ({ row }) => {
      const avg = row.getValue('averageOrderValue') as number
      return h('div', { class: 'text-muted-foreground' }, formatCurrency(avg))
    },
    enableHiding: true,
    meta: { label: 'Valor Médio/Pedido' },
  },
]
</script>

<template>
  <DataTableAdvanced
    :data="categories"
    :columns="columns"
    search-key="name"
    search-placeholder="Pesquisar por categoria..."
  />
</template>
