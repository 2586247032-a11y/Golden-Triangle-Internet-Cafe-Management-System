import api from './index'

export function getMembers(params) {
  return api.get('/members', { params })
}

export function getMemberDetail(id) {
  return api.get(`/members/${id}`)
}

export function createMember(data) {
  return api.post('/members', data)
}

export function rechargeMember(id, data) {
  return api.post(`/members/${id}/recharge`, data)
}

export function updateMemberRole(id, role) {
  return api.put(`/members/${id}/role`, { role })
}
