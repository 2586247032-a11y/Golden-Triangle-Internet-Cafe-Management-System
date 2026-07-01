<template>
  <div class="login-page">
    <div class="login-card">
      <h1>🎮 金三角网吧</h1>
      <h3>收银管理系统</h3>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent="handleLogin">
        <el-form-item prop="login">
          <el-input v-model="form.login" placeholder="管理员账号 / 会员手机号" :prefix-icon="Phone" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <p class="hint">管理员: admin / 123456 &nbsp;|&nbsp; 收银员: cashier1 / 123456 &nbsp;|&nbsp; 会员: 手机号 / 123456</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Phone, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  login: '',
  password: '',
})

const rules = {
  login: [
    { required: true, message: '请输入账号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login(form.login, form.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect
    if (redirect) { router.push(redirect); return }
    if (authStore.isMember) { router.push('/member/home'); return }
    router.push('/counter')
  } catch (e) {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.3);
}

.login-card h1 {
  text-align: center;
  margin-bottom: 4px;
  font-size: 24px;
}

.login-card h3 {
  text-align: center;
  color: #909399;
  font-weight: 400;
  margin-bottom: 32px;
}

.hint {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  margin-top: 16px;
}
</style>
