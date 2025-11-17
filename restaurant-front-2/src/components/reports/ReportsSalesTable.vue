<script setup lang="ts">
import { h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { createSortableHeader } from '@/lib/table-helpers'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
import { TrendingUp, TrendingDown } from 'lucide-vue-next'

export interface ProductSalesData {
  itemID: number
  name: string
  category: string
  quantitySold: number
  revenue: number
  averagePrice: number
  orderCount: number
}

interface Props {
  products: ProductSalesData[]
}

defineProps<Props>()

// Helper functions
function formatCurrency(value: number): string {
  return `CVE${value.toFixed(2)}`
}

// Column definitions
const columns: ColumnDef<ProductSalesData>[] = [
  {
    accessorKey: 'itemID',
    header: createSortableHeader('ID', 'itemID'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, `#${row.getValue('itemID')}`),
    enableHiding: true,
    meta: { label: 'ID' },
  },
  {
    accessorKey: 'name',
    header: createSortableHeader('Produto', 'name'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('name')),
    enableHiding: true,
    meta: { label: 'Produto' },
  },
  {
    accessorKey: 'category',
    header: createSortableHeader('Categoria', 'category'),
    cell: ({ row }) => h(Badge, { variant: 'outline' }, () => row.getValue('category')),
    enableHiding: true,
    meta: { label: 'Categoria' },
  },
  {
    accessorKey: 'quantitySold',
    header: createSortableHeader('Qtd. Vendida', 'quantitySold'),
    cell: ({ row }) => h('div', { class: 'font-semibold text-center' }, row.getValue('quantitySold')),
    enableHiding: true,
    meta: { label: 'Qtd. Vendida' },
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
      return h('div', { class: 'font-semibold text-green-600' }, formatCurrency(revenue))
    },
    enableHiding: true,
    meta: { label: 'Receita' },
  },
  {
    accessorKey: 'averagePrice',
    header: createSortableHeader('Preço Médio', 'averagePrice'),
    cell: ({ row }) => {
      const price = row.getValue('averagePrice') as number
      return h('div', { class: 'text-muted-foreground' }, formatCurrency(price))
    },
    enableHiding: true,
    meta: { label: 'Preço Médio' },
  },
  {
    id: 'performance',
    header: 'Performance',
    cell: ({ row }) => {
      const quantitySold = row.getValue('quantitySold') as number
      const isHighPerformer = quantitySold >= 10 // Arbitrary threshold

      return h('div', { class: 'flex items-center gap-1' }, [
        isHighPerformer
          ? h(TrendingUp, { class: 'h-4 w-4 text-green-600' })
          : h(TrendingDown, { class: 'h-4 w-4 text-orange-500' }),
        h('span', {
          class: isHighPerformer ? 'text-green-600 text-xs font-medium' : 'text-orange-500 text-xs font-medium'
        }, isHighPerformer ? 'Top' : 'Baixo')
      ])
    },
    enableHiding: true,
    meta: { label: 'Performance' },
  },
]
</script>

<template>
  <DataTableAdvanced
    :data="products"
    :columns="columns"
    search-key="name"
    search-placeholder="Pesquisar por nome do produto..."
  />
</template>
