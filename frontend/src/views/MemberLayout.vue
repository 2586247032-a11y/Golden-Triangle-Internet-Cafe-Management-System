<template>
  <div class="member-layout">
    <el-header class="member-header">
      <div class="header-left">
        <h2>金三角网吧会员中心</h2>
      </div>
      <div class="header-right">
        <span class="user-name">{{ authStore.user?.name || '会员' }}</span>
        <el-button text size="small" type="danger" @click="handleLogout">退出</el-button>
      </div>
    </el-header>

    <el-container>
      <el-aside width="180px" class="member-aside">
        <el-menu :default-active="route.path" router background-color="#2c3e50" text-color="#ecf0f1" active-text-color="#fff">
          <el-menu-item index="/member/home">
            <el-icon><User /></el-icon> 我的账户
          </el-menu-item>
          <el-menu-item index="/member/products">
            <el-icon><Goods /></el-icon> 商品购买
          </el-menu-item>
          <el-menu-item index="/member/rentals">
            <el-icon><Headset /></el-icon> 设备租借
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="member-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.member-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.member-header {
  background: #1a1a2e;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 56px;
  flex-shrink: 0;
}

.member-header h2 {
  font-size: 18px;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  color: #ecf0f1;
}

.member-aside {
  background: #2c3e50;
  min-height: calc(100vh - 56px);
}

.member-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
