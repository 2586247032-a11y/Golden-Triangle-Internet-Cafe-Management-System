import api from './index'

export function getComputers(params) {
  return api.get('/computers', { params })
}

export function getComputersOverview() {
  return api.get('/computers/overview')
}

export function updateComputerStatus(id, status) {
  return api.put(`/computers/${id}/status`, { status })
}

export function getZones() {
  return api.get('/zones')
}
