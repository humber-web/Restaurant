# DataTableAdvanced Component

**Official shadcn/ui DataTable pattern** using TanStack Table for Vue.

## Features

- ✅ **Powered by TanStack Table** - Industry-standard table library
- ✅ **Full sorting** - Multi-column sorting support
- ✅ **Column filtering** - Search by specific column
- ✅ **Pagination** - Built-in pagination controls
- ✅ **Column visibility** - Toggle which columns to show
- ✅ **Row selection** - Select multiple rows
- ✅ **Flexible rendering** - Full control over cell rendering with `h()` function
- ✅ **TypeScript** - Fully typed with generics

## Installation

Already installed! Uses:
- `@tanstack/vue-table` - Table logic
- shadcn/ui components - Styling

## Basic Usage

```vue
<script setup lang="ts">
import { h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import DataTableAdvanced from '@/components/shared/DataTableAdvanced.vue'
import { createSortableHeader } from '@/lib/table-helpers'
import type { MyData } from '@/types/models'

const data = ref<MyData[]>([])

const columns: ColumnDef<MyData>[] = [
  {
    accessorKey: 'id',
    header: createSortableHeader('ID', 'id'),
    cell: ({ row }) => h('span', { class: 'font-mono' }, row.getValue('id')),
  },
  {
    accessorKey: 'name',
    header: createSortableHeader('Nome', 'name'),
    cell: ({ row }) => h('span', { class: 'font-medium' }, row.getValue('name')),
  },
]
</script>

<template>
  <DataTableAdvanced
    :data="data"
    :columns="columns"
    search-key="name"
    search-placeholder="Pesquisar..."
  />
</template>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `TData[]` | required | Array of data to display |
| `columns` | `ColumnDef<TData>[]` | required | TanStack Table column definitions |
| `searchKey` | `string` | `undefined` | Column key to filter by search input |
| `searchPlaceholder` | `string` | `'Pesquisar...'` | Search input placeholder |
| `showColumnToggle` | `boolean` | `true` | Show column visibility toggle |

## Column Definition

Using TanStack Table's `ColumnDef`:

```typescript
import type { ColumnDef } from '@tanstack/vue-table'

const columns: ColumnDef<YourType>[] = [
  {
    accessorKey: 'fieldName',           // Property key
    header: createSortableHeader('Label', 'fieldName'), // Sortable header
    cell: ({ row }) => {                // Custom cell renderer
      const value = row.getValue('fieldName')
      return h('div', {}, value)
    },
  },
]
```

## Helper Functions

Located in `/lib/table-helpers.ts`:

### createSortableHeader

Creates a sortable column header with sort indicators:

```typescript
import { createSortableHeader } from '@/lib/table-helpers'

{
  accessorKey: 'name',
  header: createSortableHeader('Nome', 'name'),
}
```

### createTextColumn

Quick text column with optional sorting:

```typescript
import { createTextColumn } from '@/lib/table-helpers'

createTextColumn('name', 'Nome', {
  sortable: true,
  className: 'font-medium'
})
```

### createCustomColumn

Column with custom cell renderer:

```typescript
import { createCustomColumn } from '@/lib/table-helpers'

createCustomColumn('status', 'Estado', (value, row) => {
  return h('span', { class: 'badge' }, value)
}, { sortable: true })
```

### createActionsColumn

Actions column with dropdown menu:

```typescript
import { createActionsColumn } from '@/lib/table-helpers'

createActionsColumn('actions', (row) => {
  return h(DropdownMenu, {}, {
    // Your dropdown menu content
  })
})
```

## Complete Example

See `/components/categories/CategoriesTableAdvanced.vue` for a real implementation with:
- Sortable columns (ID, Nome, Preparado em)
- Custom cell rendering (badges, formatted text)
- Dropdown actions menu (Edit, Delete)
- Search by name
- Column visibility toggle
- Pagination

## Usage in View

```vue
<script setup lang="ts">
import CategoriesTableAdvanced from '@/components/categories/CategoriesTableAdvanced.vue'

const categories = ref<MenuCategory[]>([])
</script>

<template>
  <CategoriesTableAdvanced
    :categories="categories"
    @edit="handleEdit"
    @delete="handleDelete"
  />
</template>
```

## Differences from DataTable.vue

| Feature | DataTable.vue | DataTableAdvanced.vue |
|---------|---------------|----------------------|
| Library | Custom Vue logic | TanStack Table |
| Column Definition | Simple object | TanStack ColumnDef |
| Cell Rendering | Vue slots | `h()` render function |
| Performance | Good for small datasets | Optimized for large datasets |
| Features | Basic sorting, filtering | Full TanStack Table features |
| Learning Curve | Easier | Steeper (TanStack Table API) |

## When to Use

- **Use DataTable.vue**: Simple tables, quick prototypes, Vue-style slots
- **Use DataTableAdvanced.vue**: Complex tables, large datasets, need advanced features

Both are production-ready! Choose based on your needs. 🚀
