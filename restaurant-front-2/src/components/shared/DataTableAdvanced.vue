<script setup lang="ts" generic="TData">
import {
  FlexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useVueTable,
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
} from '@tanstack/vue-table'
import { ref, computed, h, watch } from 'vue'
import { ArrowUpDown, ChevronDown } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

interface Props {
  data: TData[]
  columns: ColumnDef<TData, any>[]
  searchKey?: string
  searchPlaceholder?: string
  showColumnToggle?: boolean
  globalFilter?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  searchPlaceholder: 'Pesquisar...',
  showColumnToggle: true,
  globalFilter: false,
})

const sorting = ref<SortingState>([])
const columnFilters = ref<ColumnFiltersState>([])
const columnVisibility = ref<VisibilityState>({})
const rowSelection = ref({})
const globalFilterValue = ref('')

const table = useVueTable({
  get data() {
    return props.data
  },
  get columns() {
    return props.columns
  },
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  onSortingChange: (updaterOrValue) => {
    sorting.value = typeof updaterOrValue === 'function' ? updaterOrValue(sorting.value) : updaterOrValue
  },
  onColumnFiltersChange: (updaterOrValue) => {
    columnFilters.value = typeof updaterOrValue === 'function' ? updaterOrValue(columnFilters.value) : updaterOrValue
  },
  onColumnVisibilityChange: (updaterOrValue) => {
    columnVisibility.value = typeof updaterOrValue === 'function' ? updaterOrValue(columnVisibility.value) : updaterOrValue
  },
  onRowSelectionChange: (updaterOrValue) => {
    rowSelection.value = typeof updaterOrValue === 'function' ? updaterOrValue(rowSelection.value) : updaterOrValue
  },
  onGlobalFilterChange: (updaterOrValue) => {
    globalFilterValue.value = typeof updaterOrValue === 'function' ? updaterOrValue(globalFilterValue.value) : updaterOrValue
  },
  globalFilterFn: (row, columnId, filterValue) => {
    const search = filterValue.toLowerCase()

    // Get all cell values as strings
    const rowValues = row.getAllCells().map(cell => {
      const value = cell.getValue()
      if (value == null) return ''
      if (typeof value === 'object') {
        return JSON.stringify(value).toLowerCase()
      }
      return String(value).toLowerCase()
    })

    // Check if any cell contains the search term
    return rowValues.some(value => value.includes(search))
  },
  state: {
    get sorting() {
      return sorting.value
    },
    get columnFilters() {
      return columnFilters.value
    },
    get columnVisibility() {
      return columnVisibility.value
    },
    get rowSelection() {
      return rowSelection.value
    },
    get globalFilter() {
      return globalFilterValue.value
    },
  },
})

const filterValue = computed({
  get: () => {
    if (props.globalFilter) {
      return globalFilterValue.value
    }
    return props.searchKey ? (table.getColumn(props.searchKey)?.getFilterValue() as string) ?? '' : ''
  },
  set: (value) => {
    if (props.globalFilter) {
      table.setGlobalFilter(value)
    } else if (props.searchKey) {
      table.getColumn(props.searchKey)?.setFilterValue(value)
    }
  },
})

// Get column display name from the column definition
function getColumnLabel(column: any): string {
  // Try to get the label from the column definition
  const columnDef = column.columnDef
  
  // If header is a string, use it
  if (typeof columnDef.header === 'string') {
    return columnDef.header
  }
  
  // If there's a meta.label, use it
  if (columnDef.meta?.label) {
    return columnDef.meta.label
  }
  
  // Otherwise use the column id
  return column.id
}

</script>

<template>
  <div class="space-y-4">
    <!-- Toolbar -->
    <div class="flex items-center justify-between gap-2">
      <Input
        v-if="searchKey || globalFilter"
        v-model="filterValue"
        :placeholder="searchPlaceholder"
        class="max-w-sm"
      />
      <slot name="toolbar" />
      
      <DropdownMenu v-if="showColumnToggle">
        <DropdownMenuTrigger as-child>
          <Button variant="outline" class="ml-auto">
            Colunas <ChevronDown class="ml-2 h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuCheckboxItem
            v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
            :key="column.id"
            :checked="column.getIsVisible()"
            @click="column.toggleVisibility(!column.getIsVisible())"
          >
            {{ getColumnLabel(column) }}
          </DropdownMenuCheckboxItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>

    <!-- Table -->
    <div class="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <TableHead v-for="header in headerGroup.headers" :key="header.id">
              <FlexRender
                v-if="!header.isPlaceholder"
                :render="header.column.columnDef.header"
                :props="header.getContext()"
              />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <template v-if="table.getRowModel().rows?.length">
            <TableRow
              v-for="row in table.getRowModel().rows"
              :key="row.id"
              :data-state="row.getIsSelected() ? 'selected' : undefined"
            >
              <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
                <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
              </TableCell>
            </TableRow>
          </template>
          <TableRow v-else>
            <TableCell :colspan="columns.length" class="h-24 text-center">
              <slot name="empty">
                <p class="text-muted-foreground">Nenhum resultado encontrado.</p>
              </slot>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between px-2">
      <div class="flex-1 text-sm text-muted-foreground">
        A mostrar {{ table.getRowModel().rows.length }} de
        {{ table.getFilteredRowModel().rows.length }} resultado(s).
      </div>
      <div class="flex items-center space-x-6 lg:space-x-8">
        <div class="flex items-center space-x-2">
          <p class="text-sm font-medium">Linhas por página</p>
          <select
            :value="table.getState().pagination.pageSize"
            @change="(e) => table.setPageSize(Number((e.target as HTMLSelectElement).value))"
            class="flex h-10 w-[70px] items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          >
            <option v-for="pageSize in [10, 20, 30, 40, 50]" :key="pageSize" :value="pageSize">
              {{ pageSize }}
            </option>
          </select>
        </div>
        <div class="flex w-[100px] items-center justify-center text-sm font-medium">
          Página {{ table.getState().pagination.pageIndex + 1 }} de
          {{ table.getPageCount() }}
        </div>
        <div class="flex items-center space-x-2">
          <Button
            variant="outline"
            class="hidden h-8 w-8 p-0 lg:flex"
            :disabled="!table.getCanPreviousPage()"
            @click="table.setPageIndex(0)"
          >
            <span class="sr-only">Ir para primeira página</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="h-4 w-4"
            >
              <polyline points="11 17 6 12 11 7" />
              <polyline points="18 17 13 12 18 7" />
            </svg>
          </Button>
          <Button
            variant="outline"
            class="h-8 w-8 p-0"
            :disabled="!table.getCanPreviousPage()"
            @click="table.previousPage()"
          >
            <span class="sr-only">Ir para página anterior</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="h-4 w-4"
            >
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </Button>
          <Button
            variant="outline"
            class="h-8 w-8 p-0"
            :disabled="!table.getCanNextPage()"
            @click="table.nextPage()"
          >
            <span class="sr-only">Ir para próxima página</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="h-4 w-4"
            >
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </Button>
          <Button
            variant="outline"
            class="hidden h-8 w-8 p-0 lg:flex"
            :disabled="!table.getCanNextPage()"
            @click="table.setPageIndex(table.getPageCount() - 1)"
          >
            <span class="sr-only">Ir para última página</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="h-4 w-4"
            >
              <polyline points="13 17 18 12 13 7" />
              <polyline points="6 17 11 12 6 7" />
            </svg>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
