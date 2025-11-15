import { ref, watch } from 'vue'
import type { Table } from '@/types/models'

export interface TablePosition {
  tableId: number
  x: number
  y: number
  width?: number
  height?: number
}

const STORAGE_KEY = 'restaurant_table_positions'

// Default grid layout generator
function generateDefaultPositions(tables: Table[]): TablePosition[] {
  const positions: TablePosition[] = []
  const cols = 4 // 4 tables per row
  const spacing = 180 // pixels between tables
  const offsetX = 20
  const offsetY = 20

  tables.forEach((table, index) => {
    const row = Math.floor(index / cols)
    const col = index % cols

    positions.push({
      tableId: table.tableid,
      x: offsetX + col * spacing,
      y: offsetY + row * spacing,
      width: 120,
      height: 120,
    })
  })

  return positions
}

export function useTablePositions() {
  const positions = ref<Map<number, TablePosition>>(new Map())

  // Load positions from localStorage
  function loadPositions() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data = JSON.parse(stored) as TablePosition[]
        positions.value = new Map(data.map(pos => [pos.tableId, pos]))
      }
    } catch (error) {
      console.error('Error loading table positions:', error)
    }
  }

  // Save positions to localStorage
  function savePositions() {
    try {
      const data = Array.from(positions.value.values())
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch (error) {
      console.error('Error saving table positions:', error)
    }
  }

  // Initialize positions for tables that don't have saved positions
  function initializePositions(tables: Table[]) {
    const defaultPositions = generateDefaultPositions(tables)

    defaultPositions.forEach(pos => {
      if (!positions.value.has(pos.tableId)) {
        positions.value.set(pos.tableId, pos)
      }
    })

    // Remove positions for tables that no longer exist
    const tableIds = new Set(tables.map(t => t.tableid))
    for (const tableId of positions.value.keys()) {
      if (!tableIds.has(tableId)) {
        positions.value.delete(tableId)
      }
    }

    savePositions()
  }

  // Get position for a specific table
  function getPosition(tableId: number): TablePosition | undefined {
    return positions.value.get(tableId)
  }

  // Update position for a table
  function updatePosition(tableId: number, x: number, y: number) {
    const existing = positions.value.get(tableId)
    if (existing) {
      existing.x = x
      existing.y = y
      positions.value.set(tableId, existing)
    } else {
      positions.value.set(tableId, {
        tableId,
        x,
        y,
        width: 120,
        height: 120,
      })
    }
    savePositions()
  }

  // Reset all positions to default grid layout
  function resetPositions(tables: Table[]) {
    positions.value.clear()
    initializePositions(tables)
  }

  // Auto-save on changes
  watch(positions, savePositions, { deep: true })

  // Load on initialization
  loadPositions()

  return {
    positions,
    getPosition,
    updatePosition,
    initializePositions,
    resetPositions,
  }
}
