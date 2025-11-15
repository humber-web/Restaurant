import { createRouter, createWebHistory, type RouteRecordRaw, type RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/services/api/client'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/views/LayoutView.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue'),
      },
      // Mesas (Tables) - Operations
      {
        path: 'mesas',
        name: 'mesas',
        component: () => import('@/views/MesasView.vue'),
      },
      {
        path: 'mesas/layout',
        name: 'mesas-layout',
        component: () => import('@/views/MesasLayoutView.vue'),
      },
      {
        path: 'mesas/pedidos',
        name: 'mesas-pedidos',
        component: () => import('@/views/MesasPedidosView.vue'),
      },
      // Pedidos (Orders)
      {
        path: 'pedidos',
        name: 'pedidos',
        component: () => import('@/views/PedidosView.vue'),
      },
      {
        path: 'pedidos/:id',
        name: 'pedido-detalhes',
        component: () => import('@/views/PedidoDetalhesView.vue'),
      },
      // Cozinha (Kitchen)
      {
        path: 'cozinha',
        name: 'cozinha',
        component: () => import('@/views/CozinhaView.vue'),
      },
      // Pagamentos (Payments)
      {
        path: 'pagamentos',
        name: 'pagamentos',
        component: () => import('@/views/PagamentosView.vue'),
      },
      {
        path: 'pagamentos/processar',
        name: 'pagamentos-processar',
        component: () => import('@/views/PagamentosProcessarView.vue'),
      },
      {
        path: 'pagamentos/historico',
        name: 'pagamentos-historico',
        component: () => import('@/views/PagamentosHistoricoView.vue'),
      },
      // Contabilidade (Accounting)
      {
        path: 'contabilidade/caixa',
        name: 'contabilidade-caixa',
        component: () => import('@/views/CaixaRegistadoraView.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'contabilidade/relatorios',
        name: 'contabilidade-relatorios',
        component: () => import('@/views/RelatoriosView.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'contabilidade/auditoria',
        name: 'contabilidade-auditoria',
        component: () => import('@/views/AuditoriaView.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'contabilidade/faturas',
        name: 'contabilidade-faturas',
        component: () => import('@/views/FaturasView.vue'),
        meta: { requiresManager: true },
      },
      // Configurações (Settings) - All require manager
      {
        path: 'configuracoes/produtos',
        name: 'configuracoes-produtos',
        component: () => import('@/views/ProdutosView.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'configuracoes/categorias',
        name: 'configuracoes-categorias',
        component: () => import('@/views/CategoriasView.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'configuracoes/mesas',
        name: 'configuracoes-mesas',
        component: () => import('@/views/ConfiguracaoMesasView.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'configuracoes/utilizadores',
        name: 'configuracoes-utilizadores',
        component: () => import('@/views/UtilizadoresView.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'configuracoes/inventario',
        name: 'configuracoes-inventario',
        component: () => import('@/views/InventarioView.vue'),
        meta: { requiresManager: true },
      },
      {
        path: 'configuracoes/fiscal',
        name: 'configuracoes-fiscal',
        component: () => import('@/views/ConfiguracaoFiscalView.vue'),
        meta: { requiresManager: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guards
router.beforeEach(async (to: RouteLocationNormalized, _from: RouteLocationNormalized) => {
  const authStore = useAuthStore()

  // If there's an access token in storage but the store hasn't loaded the user yet,
  // try to fetch the current user so navigation decisions are accurate on page reload.
  const hasToken = !!apiClient.getAccessToken()
  // Debug info to help diagnose routing issues
  // (remove or lower log level in production)
  // eslint-disable-next-line no-console
  console.debug('[router] navigation start', { to: to.fullPath, hasToken, isAuthenticated: authStore.isAuthenticated, typeofIsAuthenticated: typeof authStore.isAuthenticated, matched: to.matched.map((m: RouteRecordRaw) => m.path), metas: to.matched.map((m: RouteRecordRaw) => (m.meta as any)) })
  if (hasToken && !authStore.isAuthenticated) {
    try {
      await authStore.fetchCurrentUser()
    } catch (err) {
      // fetching user failed — tokens may be invalid. Ensure store is logged out.
      authStore.logout()
    }
  }

  const requiresAuth = to.matched.some((r: RouteRecordRaw) => (r.meta as any)?.requiresAuth === true)
  const requiresManager = to.matched.some((r: RouteRecordRaw) => (r.meta as any)?.requiresManager === true)

  // Redirect unauthenticated users trying to access protected routes
  if (requiresAuth && !authStore.isAuthenticated) {
    // eslint-disable-next-line no-console
    console.debug('[router] blocking navigation to protected route, redirecting to login', { to: to.fullPath })
    return { name: 'login', query: { next: to.fullPath } }
  }

  // Prevent non-managers from visiting manager-only pages
  if (requiresManager && !authStore.isManager()) {
    return { name: 'dashboard' }
  }

  // If user is already logged in, don't let them see the login page
  if (to.name === 'login' && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }

  // allow navigation
  return true
})

export default router
