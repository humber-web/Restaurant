<script setup lang="ts" generic="TData extends Record<string, any>">
import { ref, computed, watch } from 'vue'
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Search } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

export interface Column<T = any> {
  key: string
  label: string
  sortable?: boolean
  filterable?: boolean
  width?: string
  render?: (row: T) => any
}

interface Props {
  data: TData[]
  columns: Column<TData>[]
  searchPlaceholder?: string
  pageSize?: number
  showPagination?: boolean
  showSearch?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  searchPlaceholder: 'Pesquisar...',
  pageSize: 10,
  showPagination: true,
  showSearch: true,
})

const emit = defineEmits<{
  rowClick: [row: TData]
}>()

// State
const searchQuery = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(props.pageSize)
const sortKey = ref<string>('')
const sortOrder = ref<'asc' | 'desc'>('asc')

// Computed
const filteredData = computed(() => {
  let filtered = [...props.data]

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((row) => {
      return props.columns.some((col) => {
        if (col.filterable !== false) {
          const value = row[col.key]
          return String(value).toLowerCase().includes(query)
        }
        return false
      })
    })
  }

  // Sort
  if (sortKey.value) {
    filtered.sort((a, b) => {
      const aVal = a[sortKey.value]
      const bVal = b[sortKey.value]
      
      let comparison = 0
      if (aVal > bVal) comparison = 1
      if (aVal < bVal) comparison = -1
      
      return sortOrder.value === 'asc' ? comparison : -comparison
    })
  }

  return filtered
})

const paginatedData = computed(() => {
  if (!props.showPagination) return filteredData.value
  
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / itemsPerPage.value)
})

const pageNumbers = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  
  if (totalPages.value <= maxVisible) {
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    if (currentPage.value <= 3) {
      pages.push(1, 2, 3, 4, -1, totalPages.value)
    } else if (currentPage.value >= totalPages.value - 2) {
      pages.push(1, -1, totalPages.value - 3, totalPages.value - 2, totalPages.value - 1, totalPages.value)
    } else {
      pages.push(1, -1, currentPage.value - 1, currentPage.value, currentPage.value + 1, -1, totalPages.value)
    }
  }
  
  return pages
})

// Methods
function handleSort(key: string, sortable?: boolean) {
  if (sortable === false) return
  
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

function getCellValue(row: TData, column: Column<TData>) {
  if (column.render) {
    return column.render(row)
  }
  return row[column.key]
}

// Watch for data changes and reset to first page
watch(() => props.data, () => {
  currentPage.value = 1
})

// Watch for search query changes and reset to first page
watch(searchQuery, () => {
  currentPage.value = 1
})
</script>

<template>
  <div class="space-y-4">
    <!-- Search and Filters -->
    <div v-if="showSearch" class="flex items-center gap-2">
      <div class="relative flex-1 max-w-sm">
        <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          v-model="searchQuery"
          :placeholder="searchPlaceholder"
          class="pl-9"
        />
      </div>
      <slot name="filters" />
    </div>

    <!-- Table -->
    <div class="rounded-lg border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              v-for="column in columns"
              :key="column.key"
              :class="[
                column.width,
                column.sortable !== false ? 'cursor-pointer select-none hover:bg-muted/50' : ''
              ]"
              @click="handleSort(column.key, column.sortable)"
            >
              <div class="flex items-center gap-2">
                {{ column.label }}
                <span v-if="column.sortable !== false && sortKey === column.key" class="text-muted-foreground">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </div>
            </TableHead>
            <slot name="header-actions" />
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-if="paginatedData.length === 0">
            <TableCell :colspan="columns.length + 1" class="h-24 text-center">
              <slot name="empty">
                <p class="text-muted-foreground">Nenhum resultado encontrado</p>
              </slot>
            </TableCell>
          </TableRow>
          <TableRow
            v-else
            v-for="(row, index) in paginatedData"
            :key="index"
            @click="emit('rowClick', row)"
          >
            <TableCell v-for="column in columns" :key="column.key">
              <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
                {{ getCellValue(row, column) }}
              </slot>
            </TableCell>
            <slot name="row-actions" :row="row" />
          </TableRow>
        </TableBody>
      </Table>
    </div>

    <!-- Pagination -->
    <div v-if="showPagination && filteredData.length > 0" class="flex items-center justify-between">
      <div class="text-sm text-muted-foreground">
        A mostrar {{ ((currentPage - 1) * itemsPerPage) + 1 }} a 
        {{ Math.min(currentPage * itemsPerPage, filteredData.length) }} de 
        {{ filteredData.length }} resultados
      </div>
      
      <div class="flex items-center gap-2">
        <!-- Items per page -->
        <div class="flex items-center gap-2">
          <span class="text-sm text-muted-foreground">Linhas por página:</span>
          <Select v-model="itemsPerPage" @update:model-value="currentPage = 1">
            <SelectTrigger class="w-20">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="5">5</SelectItem>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="20">20</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <!-- Page navigation -->
        <div class="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            class="h-8 w-8"
            :disabled="currentPage === 1"
            @click="goToPage(1)"
          >
            <ChevronsLeft class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            class="h-8 w-8"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            <ChevronLeft class="h-4 w-4" />
          </Button>
          
          <div class="flex items-center gap-1">
            <template v-for="(page, idx) in pageNumbers" :key="idx">
              <span v-if="page === -1" class="px-2">...</span>
              <Button
                v-else
                variant="outline"
                size="icon"
                class="h-8 w-8"
                :class="{ 'bg-primary text-primary-foreground': page === currentPage }"
                @click="goToPage(page)"
              >
                {{ page }}
              </Button>
            </template>
          </div>
          
          <Button
            variant="outline"
            size="icon"
            class="h-8 w-8"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            <ChevronRight class="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            class="h-8 w-8"
            :disabled="currentPage === totalPages"
            @click="goToPage(totalPages)"
          >
            <ChevronsRight class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
