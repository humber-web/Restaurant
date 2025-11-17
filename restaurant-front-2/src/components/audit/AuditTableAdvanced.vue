<script setup lang="ts">
import { h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { createSortableHeader } from '@/lib/table-helpers'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
import type { OperationLog } from '@/types/models/audit'
import { Plus, Edit, Trash2, User } from 'lucide-vue-next'

interface Props {
  logs: OperationLog[]
}

defineProps<Props>()

// Helper functions
function getActionVariant(action: string): 'default' | 'secondary' | 'destructive' {
  switch (action) {
    case 'CREATE': return 'default'
    case 'UPDATE': return 'secondary'
    case 'DELETE': return 'destructive'
    default: return 'secondary'
  }
}

function getActionIcon(action: string) {
  switch (action) {
    case 'CREATE': return Plus
    case 'UPDATE': return Edit
    case 'DELETE': return Trash2
    default: return Edit
  }
}

function getActionLabel(action: string): string {
  switch (action) {
    case 'CREATE': return 'Criado'
    case 'UPDATE': return 'Atualizado'
    case 'DELETE': return 'Eliminado'
    default: return action
  }
}

function getModelLabel(modelName: string): string {
  const labels: Record<string, string> = {
    'user': 'Utilizador',
    'menuitem': 'Produto',
    'menucategory': 'Categoria',
    'table': 'Mesa',
    'order': 'Pedido',
    'payment': 'Pagamento',
    'inventoryitemn': 'Inventário',
    'cashregister': 'Caixa',
  }
  return labels[modelName.toLowerCase()] || modelName
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// Column definitions
const columns: ColumnDef<OperationLog>[] = [
  {
    accessorKey: 'id',
    header: createSortableHeader('ID', 'id'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, `#${row.getValue('id')}`),
    enableHiding: true,
    meta: { label: 'ID' },
  },
  {
    accessorKey: 'timestamp',
    header: createSortableHeader('Data/Hora', 'timestamp'),
    cell: ({ row }) => h('span', { class: 'text-sm whitespace-nowrap' }, formatDateTime(row.getValue('timestamp'))),
    enableHiding: true,
    meta: { label: 'Data/Hora' },
  },
  {
    accessorKey: 'username',
    header: createSortableHeader('Utilizador', 'username'),
    cell: ({ row }) => {
      return h('div', { class: 'flex items-center gap-2' }, [
        h(User, { class: 'h-4 w-4 text-muted-foreground' }),
        h('div', { class: 'flex flex-col' }, [
          h('span', { class: 'font-medium' }, row.getValue('username')),
          h('span', { class: 'text-xs text-muted-foreground' }, row.original.user_email)
        ])
      ])
    },
    enableHiding: true,
    meta: { label: 'Utilizador' },
  },
  {
    accessorKey: 'action',
    header: createSortableHeader('Ação', 'action'),
    cell: ({ row }) => {
      const action = row.getValue('action') as string
      const Icon = getActionIcon(action)
      return h('div', { class: 'flex items-center gap-2' }, [
        h(Badge, { variant: getActionVariant(action), class: 'gap-1' }, () => [
          h(Icon, { class: 'h-3 w-3' }),
          getActionLabel(action)
        ])
      ])
    },
    enableHiding: true,
    meta: { label: 'Ação' },
  },
  {
    accessorKey: 'model_name',
    header: createSortableHeader('Modelo', 'model_name'),
    cell: ({ row }) => {
      const modelName = row.getValue('model_name') as string
      return h(Badge, { variant: 'outline' }, () => getModelLabel(modelName))
    },
    enableHiding: true,
    meta: { label: 'Modelo' },
  },
  {
    accessorKey: 'object_repr',
    header: createSortableHeader('Objeto', 'object_repr'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('object_repr')),
    enableHiding: true,
    meta: { label: 'Objeto' },
  },
  {
    accessorKey: 'change_message',
    header: 'Mensagem',
    cell: ({ row }) => {
      const message = row.getValue('change_message') as string
      return h('span', {
        class: 'text-sm text-muted-foreground max-w-md truncate block',
        title: message
      }, message || '—')
    },
    enableHiding: true,
    meta: { label: 'Mensagem' },
  },
]
</script>

<template>
  <DataTableAdvanced
    :data="logs"
    :columns="columns"
    search-key="object_repr"
    search-placeholder="Pesquisar por objeto..."
  />
</template>
