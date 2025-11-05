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
import type { User, Group } from '@/types/models'

interface UserWithGroupNames extends User {
  groupNames?: string
}

interface Props {
  users: UserWithGroupNames[]
}

defineProps<Props>()

const emit = defineEmits<{
  edit: [user: User]
  delete: [user: User]
}>()

// Define columns using TanStack Table
const columns: ColumnDef<UserWithGroupNames>[] = [
  {
    accessorKey: 'id',
    header: createSortableHeader('ID', 'id'),
    cell: ({ row }) => h('span', { class: 'font-mono text-sm text-muted-foreground' }, row.getValue('id')),
    enableHiding: true,
    meta: {
      label: 'ID',
    },
  },
  {
    accessorKey: 'username',
    header: createSortableHeader('Username', 'username'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('username')),
    enableHiding: true,
    meta: {
      label: 'Username',
    },
  },
  {
    accessorKey: 'email',
    header: createSortableHeader('Email', 'email'),
    cell: ({ row }) => h('span', { class: 'text-sm' }, row.getValue('email')),
    enableHiding: true,
    meta: {
      label: 'Email',
    },
  },
  {
    accessorKey: 'groupNames',
    header: createSortableHeader('Grupos', 'groupNames'),
    cell: ({ row }) => {
      const groupNames = row.getValue('groupNames') as string
      return h(
        'span',
        {
          class: 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold bg-primary/10 text-primary',
        },
        groupNames || 'Nenhum'
      )
    },
    enableHiding: true,
    meta: {
      label: 'Grupos',
    },
  },
  {
    accessorKey: 'is_active',
    header: createSortableHeader('Ativo', 'is_active'),
    cell: ({ row }) => {
      const isActive = row.getValue('is_active')
      return h(
        'span',
        {
          class: [
            'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
            isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
          ],
        },
        isActive ? 'Ativo' : 'Inativo'
      )
    },
    enableHiding: true,
    meta: {
      label: 'Ativo',
    },
  },
  {
    accessorKey: 'is_staff',
    header: createSortableHeader('Staff', 'is_staff'),
    cell: ({ row }) => {
      const isStaff = row.getValue('is_staff')
      return h(
        'span',
        {
          class: 'text-sm',
        },
        isStaff ? 'Sim' : 'Não'
      )
    },
    enableHiding: true,
    meta: {
      label: 'Staff',
    },
  },
  createActionsColumn('actions', (user: User) => {
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
                    onClick: () => emit('edit', user),
                  },
                  {
                    default: () => [h(Pencil, { class: 'mr-2 h-4 w-4' }), 'Editar'],
                  }
                ),
                h(
                  DropdownMenuItem,
                  {
                    onClick: () => emit('delete', user),
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
    :data="users"
    :columns="columns"
    search-key="username"
    search-placeholder="Pesquisar utilizadores..."
  >
    <template #empty>
      <p class="text-muted-foreground">Nenhum utilizador encontrado</p>
    </template>
  </DataTableAdvanced>
</template>
