<script setup lang="ts">
import { h } from 'vue'
import { RouterLink } from 'vue-router'
import type { ColumnDef } from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { CreditCard, Wallet, Globe } from 'lucide-vue-next'
import { createSortableHeader } from '@/lib/table-helpers'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
import type { Payment } from '@/types/models'

interface Props {
  payments: Payment[]
}

defineProps<Props>()

// Helper functions
function getPaymentMethodIcon(method: string) {
  switch (method) {
    case 'CASH':
      return Wallet
    case 'CREDIT_CARD':
    case 'DEBIT_CARD':
      return CreditCard
    case 'ONLINE':
      return Globe
    default:
      return CreditCard
  }
}

function getPaymentMethodLabel(method: string) {
  switch (method) {
    case 'CASH':
      return 'Dinheiro'
    case 'CREDIT_CARD':
      return 'Cartão de Crédito'
    case 'DEBIT_CARD':
      return 'Cartão de Débito'
    case 'ONLINE':
      return 'Online'
    default:
      return method
  }
}

function getStatusVariant(status: string): 'default' | 'secondary' | 'destructive' {
  switch (status) {
    case 'COMPLETED':
      return 'default'
    case 'PENDING':
      return 'secondary'
    case 'FAILED':
      return 'destructive'
    default:
      return 'secondary'
  }
}

function getStatusLabel(status: string) {
  switch (status) {
    case 'COMPLETED':
      return 'Concluído'
    case 'PENDING':
      return 'Pendente'
    case 'FAILED':
      return 'Falhado'
    default:
      return status
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

// Define columns
const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: 'paymentID',
    header: createSortableHeader('ID', 'paymentID'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, `#${row.getValue('paymentID')}`),
    enableHiding: true,
    meta: {
      label: 'ID',
    },
  },
  {
    accessorKey: 'order',
    header: createSortableHeader('Pedido', 'order'),
    cell: ({ row }) => {
      const orderId = row.getValue('order') as number
      return h(
        RouterLink,
        {
          to: `/pedidos?order=${orderId}`,
          class: 'text-primary hover:underline font-medium',
        },
        () => `Pedido #${orderId}`
      )
    },
    enableHiding: true,
    meta: {
      label: 'Pedido',
    },
  },
  {
    accessorKey: 'created_at',
    header: createSortableHeader('Data/Hora', 'created_at'),
    cell: ({ row }) => h('span', { class: 'text-sm' }, formatDateTime(row.getValue('created_at'))),
    enableHiding: true,
    meta: {
      label: 'Data/Hora',
    },
  },
  {
    accessorKey: 'payment_method',
    header: createSortableHeader('Método', 'payment_method'),
    cell: ({ row }) => {
      const method = row.getValue('payment_method') as string
      const Icon = getPaymentMethodIcon(method)
      return h('div', { class: 'flex items-center gap-2' }, [
        h(Icon, { class: 'h-4 w-4' }),
        h('span', { class: 'text-sm' }, getPaymentMethodLabel(method)),
      ])
    },
    enableHiding: true,
    meta: {
      label: 'Método',
    },
  },
  {
    accessorKey: 'amount',
    header: createSortableHeader('Valor', 'amount'),
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue('amount'))
      return h('span', { class: 'font-semibold' }, `CVE${amount.toFixed(2)}`)
    },
    enableHiding: true,
    meta: {
      label: 'Valor',
    },
  },
  {
    accessorKey: 'payment_status',
    header: createSortableHeader('Estado', 'payment_status'),
    cell: ({ row }) => {
      const status = row.getValue('payment_status') as string
      return h(
        Badge,
        { variant: getStatusVariant(status) },
        () => getStatusLabel(status)
      )
    },
    enableHiding: true,
    meta: {
      label: 'Estado',
    },
  },
]
</script>

<template>
  <DataTableAdvanced
    :data="payments"
    :columns="columns"
    search-key="paymentID"
    search-placeholder="Pesquisar por ID de Pagamento..."
  />
</template>

