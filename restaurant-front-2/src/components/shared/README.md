# DataTable Component

Generic, reusable data table component with pagination, filtering, sorting, and customizable cells.

## Features

- ✅ **Pagination** - Configurable page size (5, 10, 20, 50, 100)
- ✅ **Search/Filter** - Global search across filterable columns
- ✅ **Sorting** - Click column headers to sort (asc/desc)
- ✅ **Customizable cells** - Use slots to render custom content
- ✅ **Row actions** - Add custom actions per row
- ✅ **Empty state** - Customizable empty state message
- ✅ **Fully typed** - Generic TypeScript support

## Basic Usage

```vue
<script setup lang="ts">
import DataTable, { type Column } from '@/components/shared/DataTable.vue'
import type { MyDataType } from '@/types/models'

const data = ref<MyDataType[]>([])

const columns: Column<MyDataType>[] = [
  { key: 'id', label: 'ID', sortable: true, width: 'w-[100px]' },
  { key: 'name', label: 'Nome', sortable: true },
  { key: 'status', label: 'Estado', sortable: true },
]
</script>

<template>
  <DataTable
    :data="data"
    :columns="columns"
    search-placeholder="Pesquisar..."
    :page-size="10"
  />
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `TData[]` | required | Array of data to display |
| `columns` | `Column<TData>[]` | required | Column definitions |
| `searchPlaceholder` | `string` | `'Pesquisar...'` | Search input placeholder |
| `pageSize` | `number` | `10` | Initial page size |
| `showPagination` | `boolean` | `true` | Show pagination controls |
| `showSearch` | `boolean` | `true` | Show search input |

## Column Definition

```typescript
interface Column<T> {
  key: string              // Property key in data object
  label: string            // Column header label
  sortable?: boolean       // Enable sorting (default: true)
  filterable?: boolean     // Include in search (default: true)
  width?: string          // Tailwind width class
  render?: (row: T) => any // Custom render function
}
```

## Slots

### Cell Customization

Customize individual cells using the `cell-{key}` slot:

```vue
<DataTable :data="data" :columns="columns">
  <template #cell-name="{ value, row }">
    <span class="font-bold">{{ value }}</span>
  </template>
</DataTable>
```

### Row Actions

Add action buttons to each row:

```vue
<DataTable :data="data" :columns="columns">
  <!-- Add header for actions column -->
  <template #header-actions>
    <th class="w-20">
      <span class="sr-only">Ações</span>
    </th>
  </template>

  <!-- Add actions for each row -->
  <template #row-actions="{ row }">
    <td>
      <Button @click="handleEdit(row)">Editar</Button>
      <Button @click="handleDelete(row)">Eliminar</Button>
    </td>
  </template>
</DataTable>
```

### Custom Filters

Add custom filter components:

```vue
<DataTable :data="data" :columns="columns">
  <template #filters>
    <Select v-model="statusFilter">
      <SelectTrigger>
        <SelectValue placeholder="Estado" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="active">Ativo</SelectItem>
        <SelectItem value="inactive">Inativo</SelectItem>
      </SelectContent>
    </Select>
  </template>
</DataTable>
```

### Empty State

Customize the empty state message:

```vue
<DataTable :data="data" :columns="columns">
  <template #empty>
    <div class="text-center py-8">
      <p class="text-muted-foreground">Nenhum item encontrado</p>
      <Button @click="addNew">Adicionar Novo</Button>
    </div>
  </template>
</DataTable>
```

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| `rowClick` | `row: TData` | Emitted when a row is clicked |

## Complete Example (Categories)

See `/components/categories/CategoriesTable.vue` for a real-world example with:
- Custom cell rendering (badges, icons)
- Dropdown menu actions
- TypeScript types
- All features enabled
