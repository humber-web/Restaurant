<script setup lang="ts">
import type { SidebarProps } from '@/components/ui/sidebar'
import { RouterLink } from 'vue-router'

import { 
  GalleryVerticalEnd,
  LayoutDashboard,
  UtensilsCrossed,
  Settings,
  Calculator,
  CreditCard,
  ClipboardList
} from "lucide-vue-next"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarRail,
} from '@/components/ui/sidebar'

const props = defineProps<SidebarProps>()

// Restaurant management navigation structure
const data = {
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: LayoutDashboard,
      items: [],
    },
    {
      title: "Mesas",
      url: "/mesas",
      icon: UtensilsCrossed,
      items: [
        {
          title: "Vista Geral",
          url: "/mesas",
        },
        {
          title: "Gestão de Pedidos",
          url: "/mesas/pedidos",
        },
      ],
    },
    {
      title: "Pedidos",
      url: "/pedidos",
      icon: ClipboardList,
      items: [],
    },
    {
      title: "Pagamentos",
      url: "/pagamentos",
      icon: CreditCard,
      items: [
        {
          title: "Processar Pagamento",
          url: "/pagamentos",
        },
        {
          title: "Histórico",
          url: "/pagamentos/historico",
        },
      ],
    },
    {
      title: "Contabilidade",
      url: "/contabilidade/caixa",
      icon: Calculator,
      items: [
        {
          title: "Caixa Registadora",
          url: "/contabilidade/caixa",
        },
        {
          title: "Relatórios",
          url: "/contabilidade/relatorios",
        },
        {
          title: "Auditoria",
          url: "/contabilidade/auditoria",
        },
      ],
    },
    {
      title: "Configurações",
      url: "/configuracoes/produtos",
      icon: Settings,
      items: [
        {
          title: "Produtos",
          url: "/configuracoes/produtos",
        },
        {
          title: "Categorias",
          url: "/configuracoes/categorias",
        },
        {
          title: "Mesas",
          url: "/configuracoes/mesas",
        },
        {
          title: "Utilizadores",
          url: "/configuracoes/utilizadores",
        },
        {
          title: "Inventário",
          url: "/configuracoes/inventario",
        },
      ],
    },
  ],
}
</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <RouterLink to="/dashboard">
              <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                <GalleryVerticalEnd class="size-4" />
              </div>
              <div class="flex flex-col gap-0.5 leading-none">
                <span class="font-semibold">Restaurante</span>
                <span class="text-xs">Sistema de Gestão</span>
              </div>
            </RouterLink>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup>
        <SidebarMenu>
          <SidebarMenuItem v-for="item in data.navMain" :key="item.title">
            <SidebarMenuButton as-child>
              <RouterLink :to="item.url" class="font-medium">
                <component :is="item.icon" class="size-4" />
                {{ item.title }}
              </RouterLink>
            </SidebarMenuButton>
            <SidebarMenuSub v-if="item.items && item.items.length">
              <SidebarMenuSubItem v-for="childItem in item.items" :key="childItem.title">
                <SidebarMenuSubButton as-child>
                  <RouterLink :to="childItem.url">{{ childItem.title }}</RouterLink>
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
            </SidebarMenuSub>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroup>
    </SidebarContent>
    <SidebarRail />
  </Sidebar>
</template>
