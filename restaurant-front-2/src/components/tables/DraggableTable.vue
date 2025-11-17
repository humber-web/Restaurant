<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Table } from '@/types/models'
import type { Order } from '@/types/models/order'
import { Badge } from '@/components/ui/badge'
import { Users, Circle, AlertCircle } from 'lucide-vue-next'

interface Props {
  table: Table
  x: number
  y: number
  width?: number
  height?: number
  orders?: Order[]
  isDraggable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: 120,
  height: 120,
  isDraggable: true,
})

const emit = defineEmits<{
  dragEnd: [tableId: number, x: number, y: number]
  click: [table: Table]
}>()

const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const currentX = ref(props.x)
const currentY = ref(props.y)

// Get status color
const statusColor = computed(() => {
  switch (props.table.status) {
    case 'AV':
      return 'bg-green-500'
    case 'OC':
      return 'bg-red-500'
    case 'RE':
      return 'bg-yellow-500'
    default:
      return 'bg-gray-500'
  }
})

// Get status label
const statusLabel = computed(() => {
  switch (props.table.status) {
    case 'AV':
      return 'Disponível'
    case 'OC':
      return 'Ocupada'
    case 'RE':
      return 'Reservada'
    default:
      return 'Desconhecida'
  }
})

// Get border color
const borderColor = computed(() => {
  switch (props.table.status) {
    case 'AV':
      return 'border-green-500'
    case 'OC':
      return 'border-red-500'
    case 'RE':
      return 'border-yellow-500'
    default:
      return 'border-gray-500'
  }
})

// Count active orders for this table
const activeOrdersCount = computed(() => {
  return props.orders?.filter(o => o.details.table === props.table.tableid).length || 0
})

// Has pending items
const hasPendingItems = computed(() => {
  return props.orders?.some(o =>
    o.details.table === props.table.tableid &&
    o.items.some(item => item.status === '1')
  ) || false
})

// Drag handlers
function handleMouseDown(event: MouseEvent) {
  if (!props.isDraggable) return

  isDragging.value = true
  dragStartX.value = event.clientX - currentX.value
  dragStartY.value = event.clientY - currentY.value

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

function handleMouseMove(event: MouseEvent) {
  if (!isDragging.value) return

  currentX.value = event.clientX - dragStartX.value
  currentY.value = event.clientY - dragStartY.value
}

function handleMouseUp() {
  if (!isDragging.value) return

  isDragging.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)

  emit('dragEnd', props.table.tableid, currentX.value, currentY.value)
}

function handleClick() {
  if (!isDragging.value) {
    emit('click', props.table)
  }
}

// Update position when props change
currentX.value = props.x
currentY.value = props.y
</script>

<template>
  <div
    class="absolute rounded-lg border-4 shadow-lg transition-all hover:shadow-xl"
    :class="[
      borderColor,
      isDraggable ? 'cursor-move' : 'cursor-pointer',
      isDragging ? 'opacity-75 scale-105 z-50' : 'z-10',
    ]"
    :style="{
      left: `${currentX}px`,
      top: `${currentY}px`,
      width: `${width}px`,
      height: `${height}px`,
    }"
    @mousedown="handleMouseDown"
    @click="handleClick"
  >
    <!-- Status Indicator -->
    <div class="absolute -top-2 -right-2 flex gap-1">
      <div
        :class="statusColor"
        class="w-5 h-5 rounded-full border-2 border-white shadow"
        :title="statusLabel"
      />
      <div
        v-if="hasPendingItems"
        class="w-5 h-5 rounded-full bg-orange-500 border-2 border-white shadow flex items-center justify-center"
        title="Items pendentes"
      >
        <AlertCircle class="h-3 w-3 text-white" />
      </div>
    </div>

    <!-- Table Content -->
    <div class="flex flex-col items-center justify-center h-full p-3">
      <div class="text-2xl font-bold mb-1">
        Mesa {{ table.tableid }}
      </div>

      <div class="flex items-center gap-1 text-sm text-muted-foreground mb-2">
        <Users class="h-4 w-4" />
        <span>{{ table.capacity }} lugares</span>
      </div>

      <Badge
        :variant="table.status === 'AV' ? 'default' : table.status === 'OC' ? 'destructive' : 'secondary'"
        class="text-xs"
      >
        {{ statusLabel }}
      </Badge>

      <div v-if="activeOrdersCount > 0" class="mt-2 text-xs font-semibold text-primary">
        {{ activeOrdersCount }} {{ activeOrdersCount === 1 ? 'pedido' : 'pedidos' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Prevent text selection during drag */
.cursor-move {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}
</style>
