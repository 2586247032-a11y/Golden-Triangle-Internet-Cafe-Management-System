import api from './index'

export function login(login, password) {
  return api.post('/login', { login, password })
}

export function logout() {
  return api.post('/logout')
}

export function getMe() {
  return api.get('/me')
}
