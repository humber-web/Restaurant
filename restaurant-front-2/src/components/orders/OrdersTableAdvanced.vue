<script setup lang="ts">
import { h } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import type { ColumnDef } from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { createSortableHeader } from '@/lib/table-helpers'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
import type { Order } from '@/types/models/order'
import { CreditCard, Eye } from 'lucide-vue-next'

interface Props {
  orders: Order[]
}

defineProps<Props>()

const router = useRouter()

// Helper functions for formatting
function getOrderStatusVariant(status: string): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case 'PENDING': return 'secondary'
    case 'PREPARING': return 'outline'
    case 'READY': return 'default'
    case 'DELIVERED': return 'default'
    case 'CANCELLED': return 'destructive'
    default: return 'secondary'
  }
}

function getOrderStatusLabel(status: string): string {
  switch (status) {
    case 'PENDING': return 'Pendente'
    case 'PREPARING': return 'Em Preparação'
    case 'READY': return 'Pronto'
    case 'DELIVERED': return 'Entregue'
    case 'CANCELLED': return 'Cancelado'
    default: return status
  }
}

function getPaymentStatusVariant(status: string): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case 'PAID': return 'default'
    case 'PARTIALLY_PAID': return 'outline'
    case 'PENDING': return 'secondary'
    case 'FAILED': return 'destructive'
    default: return 'secondary'
  }
}

function getPaymentStatusLabel(status: string): string {
  switch (status) {
    case 'PAID': return 'Pago'
    case 'PARTIALLY_PAID': return 'Parcialmente Pago'
    case 'PENDING': return 'Pendente'
    case 'FAILED': return 'Falhado'
    default: return status
  }
}

function getOrderTypeLabel(type: string): string {
  switch (type) {
    case 'RESTAURANT': return 'Restaurante'
    case 'ONLINE': return 'Online'
    default: return type
  }
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Column definitions using table-helpers
const columns: ColumnDef<Order>[] = [
  {
    accessorKey: 'orderID',
    header: createSortableHeader('ID', 'orderID'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, `#${row.getValue('orderID')}`),
    enableHiding: true,
    meta: { label: 'ID' },
  },
  {
    accessorKey: 'details.table',
    header: createSortableHeader('Mesa', 'details.table'),
    cell: ({ row }) => {
      const tableId = row.original.details?.table
      if (tableId) {
        return h(RouterLink, {
          to: `/mesas/pedidos?table=${tableId}`,
          class: 'text-primary hover:underline font-medium',
        }, () => `Mesa ${tableId}`)
      }
      return h('span', { class: 'text-muted-foreground' }, '—')
    },
    enableHiding: true,
    meta: { label: 'Mesa' },
  },
  {
    accessorKey: 'orderType',
    header: createSortableHeader('Tipo', 'orderType'),
    cell: ({ row }) => h('span', getOrderTypeLabel(row.getValue('orderType'))),
    enableHiding: true,
    meta: { label: 'Tipo' },
  },
  {
    accessorKey: 'status',
    header: createSortableHeader('Estado', 'status'),
    cell: ({ row }) => {
      const status = row.getValue('status') as string
      return h(Badge, { variant: getOrderStatusVariant(status) }, () => getOrderStatusLabel(status))
    },
    enableHiding: true,
    meta: { label: 'Estado' },
  },
  {
    accessorKey: 'paymentStatus',
    header: createSortableHeader('Pagamento', 'paymentStatus'),
    cell: ({ row }) => {
      const status = row.getValue('paymentStatus') as string
      return h(Badge, { variant: getPaymentStatusVariant(status) }, () => getPaymentStatusLabel(status))
    },
    enableHiding: true,
    meta: { label: 'Pagamento' },
  },
  {
    accessorKey: 'items',
    header: 'Items',
    cell: ({ row }) => {
      const items = row.getValue('items') as Order['items']
      const totalItems = items.reduce((sum, item) => sum + item.quantity, 0)
      return h('span', { class: 'text-sm' }, `${totalItems} item${totalItems !== 1 ? 's' : ''}`)
    },
    enableHiding: true,
    meta: { label: 'Items' },
  },
  {
    accessorKey: 'grandTotal',
    header: createSortableHeader('Total', 'grandTotal'),
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue('grandTotal'))
      return h('div', { class: 'font-semibold' }, `CVE${amount.toFixed(2)}`)
    },
    enableHiding: true,
    meta: { label: 'Total' },
  },
  {
    accessorKey: 'created_at',
    header: createSortableHeader('Data/Hora', 'created_at'),
    cell: ({ row }) => h('span', { class: 'text-sm' }, formatDateTime(row.getValue('created_at'))),
    enableHiding: true,
    meta: { label: 'Data/Hora' },
  },
  {
    id: 'actions',
    header: 'Ações',
    cell: ({ row }) => {
      const order = row.original
      return h('div', { class: 'flex gap-2' }, [
        h(Button, {
          variant: 'ghost',
          size: 'sm',
          onClick: () => {
            // Navigate to order details view
            router.push(`/pedidos/${order.orderID}`)
          },
          title: 'Ver Detalhes',
        }, () => h(Eye, { class: 'h-4 w-4' })),
        h(Button, {
          variant: 'ghost',
          size: 'sm',
          onClick: () => {
            // Navigate to payment processing
            router.push(`/pagamentos/processar?order=${order.orderID}`)
          },
          title: 'Processar Pagamento',
          disabled: order.paymentStatus === 'PAID',
        }, () => h(CreditCard, { class: 'h-4 w-4' })),
      ])
    },
    enableHiding: false,
    meta: { label: 'Ações' },
  },
]
</script>

<template>
  <DataTableAdvanced
    :data="orders"
    :columns="columns"
    :global-filter="true"
    search-placeholder="Pesquisar pedidos (ID, Mesa, Status, Total...)..."
  />
</template>
