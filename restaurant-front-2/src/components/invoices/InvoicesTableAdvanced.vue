<script setup lang="ts">
import { h, ref } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { FileText, Download, Eye, FileX } from 'lucide-vue-next'
import { createSortableHeader } from '@/lib/table-helpers'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
import type { Payment, InvoiceType } from '@/types/models/payment'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface Props {
  invoices: Payment[]
}

defineProps<Props>()

// Emit for actions
const emit = defineEmits<{
  viewDetails: [invoice: Payment]
  downloadXml: [invoice: Payment]
  issueCreditNote: [invoice: Payment]
}>()

// Helper functions
function getInvoiceTypeBadge(type?: InvoiceType) {
  if (!type) return { label: 'N/A', variant: 'secondary' as const }

  const badges: Record<InvoiceType, { label: string; variant: 'default' | 'secondary' | 'outline' | 'destructive' }> = {
    FT: { label: 'Fatura', variant: 'default' },
    FR: { label: 'Fatura Recibo', variant: 'secondary' },
    NC: { label: 'Nota de Crédito', variant: 'destructive' },
    TV: { label: 'Talão de Venda', variant: 'outline' },
  }

  return badges[type] || { label: type, variant: 'secondary' as const }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

function formatCurrency(amount: number | string): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return `${num.toFixed(2)} CVE`
}

function truncateIud(iud?: string): string {
  if (!iud) return 'N/A'
  if (iud.length <= 20) return iud
  return `${iud.substring(0, 10)}...${iud.substring(iud.length - 7)}`
}

// Define columns
const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: 'invoice_no',
    header: createSortableHeader('Número', 'invoice_no'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('invoice_no') || 'N/A'),
    enableHiding: false,
    meta: {
      label: 'Número',
    },
  },
  {
    accessorKey: 'invoice_date',
    header: createSortableHeader('Data', 'invoice_date'),
    cell: ({ row }) => h('span', { class: 'text-sm' }, formatDate(row.getValue('invoice_date'))),
    enableHiding: true,
    meta: {
      label: 'Data',
    },
  },
  {
    accessorKey: 'invoice_type',
    header: createSortableHeader('Tipo', 'invoice_type'),
    cell: ({ row }) => {
      const badge = getInvoiceTypeBadge(row.getValue('invoice_type'))
      return h(Badge, { variant: badge.variant }, () => badge.label)
    },
    enableHiding: true,
    meta: {
      label: 'Tipo',
    },
  },
  {
    accessorKey: 'customer_name',
    header: createSortableHeader('Cliente', 'customer_name'),
    cell: ({ row }) => {
      const name = row.getValue('customer_name') as string
      const taxId = row.original.customer_tax_id
      return h('div', { class: 'flex flex-col' }, [
        h('span', { class: 'text-sm font-medium' }, name || 'Consumidor Final'),
        taxId ? h('span', { class: 'text-xs text-muted-foreground' }, `NIF: ${taxId}`) : null,
      ])
    },
    enableHiding: true,
    meta: {
      label: 'Cliente',
    },
  },
  {
    accessorKey: 'amount',
    header: createSortableHeader('Valor', 'amount'),
    cell: ({ row }) => h('span', { class: 'font-semibold' }, formatCurrency(row.getValue('amount'))),
    enableHiding: true,
    meta: {
      label: 'Valor',
    },
  },
  {
    accessorKey: 'iud',
    header: 'IUD',
    cell: ({ row }) => {
      const iud = row.getValue('iud') as string
      return h('span', { class: 'text-xs font-mono text-muted-foreground' }, truncateIud(iud))
    },
    enableHiding: true,
    meta: {
      label: 'IUD',
    },
  },
  {
    id: 'actions',
    header: 'Ações',
    cell: ({ row }) => {
      const invoice = row.original
      const canIssueNC = invoice.invoice_type !== 'NC'  // Can't issue NC against another NC

      const buttons = [
        h(
          Button,
          {
            variant: 'ghost',
            size: 'sm',
            onClick: () => emit('viewDetails', invoice),
          },
          () => [h(Eye, { class: 'h-4 w-4' })]
        ),
        h(
          Button,
          {
            variant: 'ghost',
            size: 'sm',
            onClick: () => emit('downloadXml', invoice),
          },
          () => [h(Download, { class: 'h-4 w-4' })]
        ),
      ]

      // Add "Issue Credit Note" button for FT, FR, TV (not NC)
      if (canIssueNC) {
        buttons.push(
          h(
            Button,
            {
              variant: 'ghost',
              size: 'sm',
              class: 'text-red-600 hover:text-red-700 hover:bg-red-50',
              onClick: () => emit('issueCreditNote', invoice),
            },
            () => [h(FileX, { class: 'h-4 w-4' })]
          )
        )
      }

      return h('div', { class: 'flex gap-2' }, buttons)
    },
    enableHiding: false,
    meta: {
      label: 'Ações',
    },
  },
]
</script>

<template>
  <DataTableAdvanced
    :data="invoices"
    :columns="columns"
    search-key="invoice_no"
    search-placeholder="Pesquisar por número de fatura..."
    @viewDetails="emit('viewDetails', $event)"
    @downloadXml="emit('downloadXml', $event)"
    @issueCreditNote="emit('issueCreditNote', $event)"
  />
</template>
