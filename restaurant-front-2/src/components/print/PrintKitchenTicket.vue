<script setup lang="ts">
import { computed } from 'vue'
import type { Order, OrderItem } from '@/types/models'

interface Props {
  order: Order
  station?: '1' | '2' | '3' // Kitchen, Bar, Counter
}

const props = defineProps<Props>()

const stationNames = {
  '1': 'COZINHA',
  '2': 'BAR',
  '3': 'BALCÃO',
}

const stationName = computed(() => {
  return props.station ? stationNames[props.station] : 'TODOS'
})

// Filter items by station if specified
const filteredItems = computed(() => {
  if (!props.station) {
    return props.order.items
  }
  return props.order.items.filter(item => item.to_be_prepared_in === props.station)
})

const statusNames = {
  '1': 'Pendente',
  '2': 'Preparando',
  '3': 'Pronto',
  '4': 'Entregue',
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getTableDisplay(): string {
  if (props.order.orderType === 'ONLINE') {
    return 'ONLINE'
  }
  return props.order.details.table ? `Mesa ${props.order.details.table}` : 'N/A'
}
</script>

<template>
  <div :id="`kitchen-ticket-${order.orderID}${station ? `-${station}` : ''}`" class="print-ticket">
    <div class="print-header">
      <h1>{{ stationName }}</h1>
      <p>TICKET DE PREPARAÇÃO</p>
      <p>━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
    </div>

    <div class="print-section">
      <div class="print-row">
        <span class="print-label">Pedido:</span>
        <span>#{{ order.orderID }}</span>
      </div>
      <div class="print-row">
        <span class="print-label">{{ order.orderType === 'ONLINE' ? 'Tipo:' : 'Mesa:' }}</span>
        <span>{{ getTableDisplay() }}</span>
      </div>
      <div class="print-row">
        <span class="print-label">Data/Hora:</span>
        <span>{{ formatDateTime(order.created_at) }}</span>
      </div>
    </div>

    <div class="print-section">
      <div class="print-items">
        <div v-for="(item, index) in filteredItems" :key="index" class="print-item">
          <div class="print-item-name">
            {{ item.quantity }}x {{ item.name || `Item #${item.menu_item}` }}
            <span v-if="!station" class="station-badge">
              {{ stationNames[item.to_be_prepared_in as '1' | '2' | '3'] }}
            </span>
          </div>
          <div class="print-item-details">
            <span>Estado: {{ statusNames[item.status] }}</span>
            <span>{{ Number(item.price).toFixed(2) }}€</span>
          </div>
        </div>
      </div>

      <div v-if="filteredItems.length === 0" style="text-align: center; padding: 20px 0; font-style: italic;">
        Nenhum item para esta estação
      </div>
    </div>

    <div class="print-section">
      <div class="print-row">
        <span class="print-label">Total de Items:</span>
        <span>{{ filteredItems.reduce((sum, item) => sum + item.quantity, 0) }}</span>
      </div>
      <div class="print-row">
        <span class="print-label">Estado do Pedido:</span>
        <span class="status-badge">{{ order.status }}</span>
      </div>
    </div>

    <div class="print-footer">
      <p>━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
      <p>Impresso em: {{ new Date().toLocaleString('pt-PT') }}</p>
      <p>Sistema de Gestão de Restaurante</p>
    </div>
  </div>
</template>

<style scoped>
.print-ticket {
  width: 80mm;
  max-width: 300px;
  margin: 0 auto;
  padding: 8px;
}

/* Hide from screen, only show when printing */
@media screen {
  .print-ticket {
    display: none;
  }
}

@media print {
  .print-ticket {
    display: block;
  }
}
</style>
