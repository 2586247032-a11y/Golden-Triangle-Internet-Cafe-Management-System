import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Layout from '../components/Layout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { title: '登录', noAuth: true },
  },
  // 管理端（收银员+超级管理员）
  {
    path: '/',
    component: Layout,
    redirect: '/counter',
    meta: { staffOnly: true },
    children: [
      { path: 'counter', name: 'Counter', component: () => import('../views/CounterView.vue'), meta: { title: '收银台' } },
      { path: 'session/new', name: 'SessionNew', component: () => import('../views/SessionNewView.vue'), meta: { title: '开卡上机' } },
      { path: 'session/:id/end', name: 'SessionEnd', component: () => import('../views/SessionEndView.vue'), meta: { title: '下机结算' } },
      { path: 'members', name: 'Members', component: () => import('../views/MembersView.vue'), meta: { title: '会员管理' } },
      { path: 'products', name: 'Products', component: () => import('../views/ProductsView.vue'), meta: { title: '商品售卖' } },
      { path: 'rentals', name: 'Rentals', component: () => import('../views/RentalsView.vue'), meta: { title: '设备租借' } },
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { title: '仪表盘', superOnly: true } },
      { path: 'settings', name: 'Settings', component: () => import('../views/SettingsView.vue'), meta: { title: '系统设置', superOnly: true } },
    ],
  },
  // 会员端
  {
    path: '/member',
    component: () => import('../views/MemberLayout.vue'),
    redirect: '/member/home',
    meta: { title: '会员中心' },
    children: [
      { path: 'home', name: 'MemberHome', component: () => import('../views/MemberHomeView.vue'), meta: { title: '我的账户' } },
      { path: 'products', name: 'MemberProducts', component: () => import('../views/MemberProductsView.vue'), meta: { title: '商品购买' } },
      { path: 'rentals', name: 'MemberRentals', component: () => import('../views/MemberRentalsView.vue'), meta: { title: '设备租借' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.noAuth) {
    next()
    return
  }

  if (!authStore.token) {
    next('/login')
    return
  }

  // 管理端路由 → 仅员工可访问
  if (to.meta.staffOnly && !authStore.isStaff) {
    next('/member/home')
    return
  }

  // 仪表盘/设置 → 仅超级管理员
  if (to.meta.superOnly && !authStore.isSuper) {
    next('/counter')
    return
  }

  next()
})

export default router
