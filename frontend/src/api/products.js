import api from './index'

export function getProducts(params) {
  return api.get('/products', { params })
}

export function restockProduct(id, quantity) {
  return api.put(`/products/${id}/restock`, { quantity })
}
