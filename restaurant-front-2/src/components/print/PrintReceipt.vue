<script setup lang="ts">
import { computed } from 'vue'
import type { Order, Payment } from '@/types/models'

interface Props {
  order: Order
  payments?: Payment[]
}

const props = defineProps<Props>()

const paymentMethodNames = {
  CASH: 'Dinheiro',
  CREDIT_CARD: 'Cartão de Crédito',
  DEBIT_CARD: 'Cartão de Débito',
  ONLINE: 'Pagamento Online',
}

const totalPaid = computed(() => {
  if (!props.payments || props.payments.length === 0) {
    return 0
  }
  return props.payments
    .filter(p => p.payment_status === 'COMPLETED')
    .reduce((sum, p) => sum + Number(p.amount), 0)
})

const remainingAmount = computed(() => {
  return Number(props.order.grandTotal) - totalPaid.value
})

const isPaid = computed(() => {
  return props.order.paymentStatus === 'PAID' || remainingAmount.value <= 0
})

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
</script>

<template>
  <div :id="`receipt-${order.orderID}`" class="print-receipt">
    <div class="print-header">
      <h1>RESTAURANTE</h1>
      <p>Sistema de Gestão</p>
      <p>NIF: 123456789</p>
      <p>━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
      <p style="font-weight: bold; margin-top: 8px;">FATURA SIMPLIFICADA</p>
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
    </div>

    <div class="print-section">
      <p style="font-weight: bold; margin-bottom: 8px;">ITEMS</p>
      <div class="print-items">
        <div v-for="(item, index) in order.items" :key="index" class="print-item">
          <div class="print-item-row">
            <span>{{ item.quantity }}x {{ item.name || `Item #${item.menu_item}` }}</span>
            <span>{{ (Number(item.price) * item.quantity).toFixed(2) }}CVE</span>
          </div>
          <div class="print-item-subrow">
            <span>{{ Number(item.price).toFixed(2) }}CVE cada</span>
          </div>
        </div>
      </div>
    </div>

    <div class="print-section">
      <div class="print-row">
        <span>Subtotal:</span>
        <span>{{ Number(order.totalAmount).toFixed(2) }}CVE</span>
      </div>
      <div class="print-row">
        <span>IVA (15%):</span>
        <span>{{ Number(order.totalIva).toFixed(2) }}CVE</span>
      </div>
      <div class="print-total">
        <div class="print-row">
          <span>TOTAL:</span>
          <span>{{ Number(order.grandTotal).toFixed(2) }}CVE</span>
        </div>
      </div>
    </div>

    <div v-if="payments && payments.length > 0" class="print-section">
      <p style="font-weight: bold; margin-bottom: 8px;">PAGAMENTOS</p>
      <div v-for="payment in payments" :key="payment.paymentID" class="print-row">
        <span>{{ paymentMethodNames[payment.payment_method] }}</span>
        <span>{{ Number(payment.amount).toFixed(2) }}CVE</span>
      </div>
      <div class="print-total" style="margin-top: 8px;">
        <div class="print-row">
          <span>Total Pago:</span>
          <span>{{ totalPaid.toFixed(2) }}CVE</span>
        </div>
        <div v-if="!isPaid" class="print-row" style="font-size: 11px;">
          <span>Restante:</span>
          <span>{{ remainingAmount.toFixed(2) }}CVE</span>
        </div>
      </div>
    </div>

    <div v-if="isPaid" class="print-section" style="text-align: center; font-weight: bold;">
      <p>✓ PAGO</p>
    </div>

    <div class="print-footer">
      <p>━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
      <p>Obrigado pela sua preferência!</p>
      <p style="margin-top: 4px;">Volte sempre!</p>
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
.print-receipt {
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
  .print-receipt {
    display: none;
  }
}

@media print {
  .print-receipt {
    display: block;
  }

  .print-item-subrow {
    color: #333;
  }
}
</style>
