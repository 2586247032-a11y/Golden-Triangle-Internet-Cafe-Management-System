<template>
  <div class="member-products">
    <h3 style="margin-bottom: 16px">商品购买</h3>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card shadow="never">
          <div class="product-grid">
            <div v-for="p in products" :key="p.product_id" :class="['product-item', { unavailable: !p.is_available || p.stock <= 0 }]" @click="addToCart(p)">
              <div class="product-name">{{ p.name }}</div>
              <div class="product-meta">
                <el-tag size="small">{{ p.category }}</el-tag>
                <span class="product-price">¥{{ p.price.toFixed(2) }}</span>
              </div>
              <div class="product-stock">库存: {{ p.stock }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>购物车</template>
          <el-table :data="cart" stripe size="small" v-if="cart.length">
            <el-table-column prop="name" label="商品" />
            <el-table-column label="数量" width="100">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" :max="row.stock" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="小计" width="70">
              <template #default="{ row }">¥{{ (row.price * row.quantity).toFixed(2) }}</template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="点击左侧商品添加" />
          <el-divider v-if="cart.length" />
          <div v-if="cart.length" style="text-align: right">
            <div class="total">合计：<span>¥{{ total.toFixed(2) }}</span></div>
            <el-button type="primary" :loading="submitting" @click="handleSubmit">下单</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProducts } from '../api/products'
import { createOrder } from '../api/rentals'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const products = ref([])
const cart = ref([])
const submitting = ref(false)
const total = computed(() => cart.value.reduce((s, i) => s + i.price * i.quantity, 0))

function addToCart(p) {
  if (!p.is_available || p.stock <= 0) { ElMessage.warning('暂不可售'); return }
  const e = cart.value.find(c => c.product_id === p.product_id)
  if (e) { if (e.quantity < p.stock) e.quantity++; else ElMessage.warning('库存不足') }
  else cart.value.push({ product_id: p.product_id, name: p.name, price: p.price, stock: p.stock, quantity: 1 })
}

async function handleSubmit() {
  if (!cart.value.length) { ElMessage.warning('购物车为空'); return }
  submitting.value = true
  try {
    await createOrder({ member_id: authStore.user.user_id, items: cart.value.map(c => ({ product_id: c.product_id, quantity: c.quantity })) })
    ElMessage.success('下单成功')
    cart.value = []
    products.value = await getProducts()
  } catch (e) { /* */ }
  finally { submitting.value = false }
}

onMounted(async () => { products.value = await getProducts() })
</script>

<style scoped>
.product-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.product-item { padding: 10px; border: 1px solid #e4e7ed; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.product-item:hover { border-color: #409eff; background: #ecf5ff; }
.product-item.unavailable { opacity: 0.5; cursor: not-allowed; }
.product-name { font-weight: 600; margin-bottom: 4px; }
.product-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.product-price { color: #e74c3c; font-weight: 500; }
.product-stock { font-size: 12px; color: #909399; }
.total { font-size: 16px; margin-bottom: 12px; }
.total span { color: #e74c3c; font-weight: bold; font-size: 22px; }
</style>
