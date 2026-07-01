import api from './index'

export function createOrder(data) {
  return api.post('/orders', data)
}

export function getOrders(params) {
  return api.get('/orders', { params })
}

export function createRental(data) {
  return api.post('/rentals', data)
}

export function returnRental(id, data) {
  return api.post(`/rentals/${id}/return`, data)
}

export function getRentals(params) {
  return api.get('/rentals', { params })
}

export function getSettings() {
  return api.get('/settings')
}

export function updateSetting(key, data) {
  return api.put(`/settings/${key}`, data)
}

export function getZoneSettings() {
  return api.get('/settings/zones')
}

export function updateZonePricing(id, data) {
  return api.put(`/settings/zones/${id}`, data)
}

export function getOperators() {
  return api.get('/operators')
}

export function createOperator(login, password, name) {
  return api.post('/operators', { login, password, name })
}

export function deleteOperator(id) {
  return api.delete(`/operators/${id}`)
}
