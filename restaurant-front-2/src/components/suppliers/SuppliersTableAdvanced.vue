<script setup lang="ts">
import { h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Eye, Pencil, Trash2 } from 'lucide-vue-next'
import { createSortableHeader } from '@/lib/table-helpers'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
import type { Supplier } from '@/types/models/supplier'

interface Props {
  suppliers: Supplier[]
}

defineProps<Props>()

// Emit events for actions
const emit = defineEmits<{
  view: [supplier: Supplier]
  edit: [supplier: Supplier]
  delete: [supplier: Supplier]
}>()

// Helper functions
function formatNIF(nif: string): string {
  // Format NIF with spacing for readability
  if (nif.length === 9) {
    return `${nif.substring(0, 3)} ${nif.substring(3, 6)} ${nif.substring(6, 9)}`
  }
  return nif
}

// Define columns
const columns: ColumnDef<Supplier>[] = [
  {
    accessorKey: 'supplierID',
    header: createSortableHeader('ID', 'supplierID'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, `#${row.getValue('supplierID')}`),
    enableHiding: true,
    meta: {
      label: 'ID',
    },
  },
  {
    accessorKey: 'tax_id',
    header: createSortableHeader('NIF', 'tax_id'),
    cell: ({ row }) => h('span', { class: 'font-mono text-sm' }, formatNIF(row.getValue('tax_id'))),
    enableHiding: false,
    meta: {
      label: 'NIF',
    },
  },
  {
    accessorKey: 'company_name',
    header: createSortableHeader('Nome da Empresa', 'company_name'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('company_name')),
    enableHiding: false,
    meta: {
      label: 'Nome',
    },
  },
  {
    accessorKey: 'contact_person',
    header: 'Contacto',
    cell: ({ row }) => h('span', { class: 'text-sm' }, row.getValue('contact_person') || 'N/A'),
    enableHiding: true,
    meta: {
      label: 'Pessoa de Contacto',
    },
  },
  {
    accessorKey: 'city',
    header: createSortableHeader('Cidade', 'city'),
    cell: ({ row }) => h('span', { class: 'text-sm' }, row.getValue('city') || 'N/A'),
    enableHiding: true,
    meta: {
      label: 'Cidade',
    },
  },
  {
    accessorKey: 'telephone',
    header: 'Telefone',
    cell: ({ row }) => {
      const phone = row.original.telephone || row.original.mobile_phone
      return h('span', { class: 'text-sm' }, phone || 'N/A')
    },
    enableHiding: true,
    meta: {
      label: 'Telefone',
    },
  },
  {
    accessorKey: 'email',
    header: 'Email',
    cell: ({ row }) => h('span', { class: 'text-sm' }, row.getValue('email') || 'N/A'),
    enableHiding: true,
    meta: {
      label: 'Email',
    },
  },
  {
    accessorKey: 'is_active',
    header: 'Estado',
    cell: ({ row }) => {
      const isActive = row.getValue('is_active')
      return h(
        Badge,
        { variant: isActive ? 'default' : 'destructive' },
        () => isActive ? 'Ativo' : 'Inativo'
      )
    },
    enableHiding: true,
    meta: {
      label: 'Estado',
    },
  },
  {
    id: 'actions',
    header: 'Ações',
    cell: ({ row }) => {
      return h('div', { class: 'flex gap-2 justify-end' }, [
        h(
          Button,
          {
            variant: 'ghost',
            size: 'sm',
            onClick: () => emit('view', row.original),
          },
          () => [h(Eye, { class: 'h-4 w-4' })]
        ),
        h(
          Button,
          {
            variant: 'ghost',
            size: 'sm',
            onClick: () => emit('edit', row.original),
          },
          () => [h(Pencil, { class: 'h-4 w-4' })]
        ),
        h(
          Button,
          {
            variant: 'ghost',
            size: 'sm',
            onClick: () => emit('delete', row.original),
          },
          () => [h(Trash2, { class: 'h-4 w-4 text-destructive' })]
        ),
      ])
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
    :data="suppliers"
    :columns="columns"
    search-key="company_name"
    search-placeholder="Pesquisar por nome, NIF ou email..."
    :global-filter="true"
    @view="emit('view', $event)"
    @edit="emit('edit', $event)"
    @delete="emit('delete', $event)"
  />
</template>
