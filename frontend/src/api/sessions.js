import api from './index'

export function startSession(data) {
  return api.post('/sessions/start', data)
}

export function endSession(id) {
  return api.post(`/sessions/${id}/end`)
}

export function getActiveSessions() {
  return api.get('/sessions/active')
}

export function getSessions(params) {
  return api.get('/sessions', { params })
}

export function getDashboardRevenue() {
  return api.get('/dashboard/revenue')
}
