<script setup lang="ts">
import { computed } from 'vue'
import type { Order } from '@/types/models'

interface Props {
  order: Order
}

const props = defineProps<Props>()

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
    return 'Pedido Online'
  }
  return props.order.details.table ? `Mesa ${props.order.details.table}` : 'Balcão'
}

const totalItems = computed(() => {
  return props.order.items.reduce((sum, item) => sum + item.quantity, 0)
})
</script>

<template>
  <div :id="`proforma-${order.orderID}`" class="print-proforma">
    <div class="print-header">
      <h1>RESTAURANTE</h1>
      <p>Sistema de Gestão</p>
      <p>NIF: 123456789</p>
      <p>━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
      <p style="font-weight: bold; margin-top: 8px;">FATURA PROFORMA</p>
      <p style="font-size: 10px; margin-top: 4px;">(Documento não fiscal)</p>
    </div>

    <div class="print-section">
      <div class="print-row">
        <span class="print-label">Pedido Nº:</span>
        <span>#{{ order.orderID }}</span>
      </div>
      <div class="print-row">
        <span class="print-label">{{ order.orderType === 'ONLINE' ? 'Tipo:' : 'Mesa:' }}</span>
        <span>{{ getTableDisplay() }}</span>
      </div>
      <div class="print-row">
        <span class="print-label">Data:</span>
        <span>{{ formatDateTime(order.created_at) }}</span>
      </div>
      <div class="print-row">
        <span class="print-label">Estado:</span>
        <span>{{ order.status === 'PENDING' ? 'Pendente' : order.status === 'PREPARING' ? 'Em Preparação' : order.status === 'READY' ? 'Pronto' : order.status }}</span>
      </div>
    </div>

    <div class="print-section">
      <p style="font-weight: bold; margin-bottom: 8px;">ITEMS DO PEDIDO</p>
      <div class="print-items">
        <div v-for="(item, index) in order.items" :key="index" class="print-item">
          <div class="print-item-row">
            <span>{{ item.quantity }}x {{ item.name || `Item #${item.menu_item}` }}</span>
            <span>{{ (Number(item.price) * item.quantity).toFixed(2) }}€</span>
          </div>
          <div class="print-item-subrow">
            <span>{{ Number(item.price).toFixed(2) }}€ cada</span>
          </div>
        </div>
      </div>
    </div>

    <div class="print-section">
      <div class="print-row">
        <span>Total de Items:</span>
        <span>{{ totalItems }}</span>
      </div>
      <div class="print-row">
        <span>Subtotal:</span>
        <span>{{ Number(order.totalAmount).toFixed(2) }}€</span>
      </div>
      <div class="print-row">
        <span>IVA (15%):</span>
        <span>{{ Number(order.totalIva).toFixed(2) }}€</span>
      </div>
      <div class="print-total">
        <div class="print-row">
          <span>TOTAL A PAGAR:</span>
          <span>{{ Number(order.grandTotal).toFixed(2) }}€</span>
        </div>
      </div>
    </div>

    <div class="print-section" style="border-bottom: none;">
      <p style="text-align: center; font-size: 10px; margin-bottom: 4px;">
        Este documento é uma estimativa do valor a pagar
      </p>
      <p style="text-align: center; font-size: 10px;">
        Não tem valor fiscal
      </p>
    </div>

    <div class="print-footer">
      <p>━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
      <p>Obrigado pela sua preferência!</p>
      <p style="margin-top: 4px;">Bom apetite!</p>
      <p style="margin-top: 8px; font-size: 10px;">
        Impresso em: {{ new Date().toLocaleString('pt-PT') }}
      </p>
      <p style="font-size: 10px;">
        Sistema de Gestão de Restaurante
      </p>
    </div>
  </div>
</template>

<style scoped>
.print-proforma {
  width: 80mm;
  max-width: 300px;
  margin: 0 auto;
  padding: 8px;
}

.print-item-row {
  display: flex;
  justify-content: space-between;
  margin: 4px 0;
}

.print-item-subrow {
  font-size: 10px;
  color: #666;
  margin-left: 20px;
  margin-bottom: 4px;
}

/* Hide from screen, only show when printing */
@media screen {
  .print-proforma {
    display: none;
  }
}

@media print {
  .print-proforma {
    display: block;
  }

  .print-item-subrow {
    color: #333;
  }
}
</style>
