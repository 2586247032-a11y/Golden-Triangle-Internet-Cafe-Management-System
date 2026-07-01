import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, logout as apiLogout, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => user.value?.role || '')
  const isStaff = computed(() => role.value === 'super_admin' || role.value === 'cashier')
  const isSuper = computed(() => role.value === 'super_admin')
  const isMember = computed(() => role.value === 'member')

  async function login(loginName, password) {
    const result = await apiLogin(loginName, password)
    token.value = result.token
    user.value = {
      user_id: result.user_id,
      name: result.name,
      role: result.role,
    }
    localStorage.setItem('token', result.token)
    localStorage.setItem('user', JSON.stringify(user.value))
    return result
  }

  async function logout() {
    try {
      await apiLogout()
    } catch (e) { /* ignore */ }
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function checkAuth() {
    if (!token.value) return false
    try {
      const me = await getMe()
      user.value = me
      return true
    } catch (e) {
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      return false
    }
  }

  return { token, user, isLoggedIn, role, isStaff, isSuper, isMember, login, logout, checkAuth }
})
