<template>
  <el-container class="layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <span v-if="!isCollapse">🎮 金三角网吧</span>
        <span v-else>🎮</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        background-color="#001529"
        text-color="#ffffffb3"
        active-text-color="#fff"
      >
        <el-menu-item index="/counter" @click="navigate('/counter')">
          <el-icon><Monitor /></el-icon>
          <span>收银台</span>
        </el-menu-item>
        <el-menu-item index="/session/new" @click="navigate('/session/new')">
          <el-icon><Plus /></el-icon>
          <span>开卡上机</span>
        </el-menu-item>
        <el-menu-item index="/members" @click="navigate('/members')">
          <el-icon><User /></el-icon>
          <span>会员管理</span>
        </el-menu-item>
        <el-menu-item index="/products" @click="navigate('/products')">
          <el-icon><Goods /></el-icon>
          <span>商品售卖</span>
        </el-menu-item>
        <el-menu-item index="/rentals" @click="navigate('/rentals')">
          <el-icon><Headset /></el-icon>
          <span>设备租借</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.isSuper" index="/dashboard" @click="navigate('/dashboard')">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.isSuper" index="/settings" @click="navigate('/settings')">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主体 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button text @click="isCollapse = !isCollapse" style="font-size: 18px">
            {{ isCollapse ? '☰' : '✕' }}
          </el-button>
          <span class="title">{{ route.meta.title || '' }}</span>
        </div>
        <div class="header-right">
          <el-tag :type="authStore.isSuper ? 'danger' : 'warning'" size="small">
            {{ authStore.isSuper ? '超级管理员' : '收银员' }}
          </el-tag>
          <span class="user-name">{{ authStore.user?.name }}</span>
          <el-button type="danger" text size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isCollapse = ref(false)

function navigate(path) {
  if (route.path !== path) {
    router.push(path)
  }
}

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/session')) return '/session/new'
  return path
})

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}

.aside {
  background: #001529;
  overflow: hidden;
}

.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #ffffff1a;
}

.el-menu {
  border-right: none;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 56px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title {
  font-size: 16px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  color: #333;
}

.main {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
