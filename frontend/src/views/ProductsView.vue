<template>
  <div class="products-page">
    <el-row :gutter="20">
      <!-- 商品列表 -->
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span>商品列表</span></template>
          <div class="product-grid">
            <div
              v-for="p in products"
              :key="p.product_id"
              :class="['product-item', { unavailable: !p.is_available || p.stock <= 0 }]"
              @click="addToCart(p)"
            >
              <div class="product-name">{{ p.name }}</div>
              <div class="product-meta">
                <el-tag size="small">{{ p.category }}</el-tag>
                <span class="product-price">¥{{ p.price.toFixed(2) }}/{{ p.unit }}</span>
              </div>
              <div class="product-stock">
                库存：<span :style="{ color: p.stock <= 5 ? '#f56c6c' : '#67c23a' }">{{ p.stock }}</span>
                <el-button v-if="isSuper" size="small" text type="warning" style="margin-left: 8px"
                  @click.stop="showRestockDialog(p)">补货</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 购物车 -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header><span>购物车</span></template>

          <!-- 选择会员 -->
          <el-form label-width="60px" style="margin-bottom: 16px">
            <el-form-item label="会员">
              <el-select
                v-model="selectedMemberId"
                filterable
                remote
                :remote-method="searchMembers"
                :loading="memberSearching"
                placeholder="搜索会员"
                style="width: 100%"
                clearable
              >
                <el-option
                  v-for="m in memberOptions"
                  :key="m.member_id"
                  :label="`${m.name} (${m.phone}) - 余额 ¥${m.balance}`"
                  :value="m.member_id"
                />
              </el-select>
            </el-form-item>
          </el-form>

          <!-- 购物车列表 -->
          <el-table :data="cart" stripe size="small" v-if="cart.length > 0">
            <el-table-column prop="name" label="商品" />
            <el-table-column label="单价" width="80">
              <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="数量" width="120">
              <template #default="{ row, $index }">
                <el-input-number v-model="row.quantity" :min="1" :max="row.stock" size="small" @change="recalcTotal" />
              </template>
            </el-table-column>
            <el-table-column label="小计" width="80">
              <template #default="{ row }">¥{{ (row.price * row.quantity).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button type="danger" size="small" text @click="removeFromCart($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-else description="购物车为空，点击左侧商品添加" />

          <el-divider v-if="cart.length > 0" />
          <div v-if="cart.length > 0" class="cart-footer">
            <div class="total">合计：<span>¥{{ totalAmount.toFixed(2) }}</span></div>
            <el-button type="primary" size="large" :loading="submitting" :disabled="!selectedMemberId" @click="handleSubmit">
              结算
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 补货对话框 -->
    <el-dialog v-model="restockVisible" title="补货" width="350px">
      <div v-if="restockProductData">
        <p>商品：<strong>{{ restockProductData.name }}</strong></p>
        <p>当前库存：<strong>{{ restockProductData.stock }}</strong></p>
        <el-form label-width="80px" style="margin-top: 16px">
          <el-form-item label="补货数量">
            <el-input-number v-model="restockQty" :min="1" :max="999" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="restockVisible = false">取消</el-button>
        <el-button type="primary" :loading="restockLoading" @click="handleRestock">确认补货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProducts, restockProduct } from '../api/products'
import { getMembers } from '../api/members'
import { createOrder } from '../api/rentals'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const isSuper = computed(() => authStore.role === 'super_admin')

const products = ref([])
const cart = ref([])
const selectedMemberId = ref(null)
const memberOptions = ref([])
const memberSearching = ref(false)
const submitting = ref(false)

const totalAmount = computed(() => {
  return cart.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

function addToCart(product) {
  if (!product.is_available || product.stock <= 0) {
    ElMessage.warning('该商品暂不可售')
    return
  }
  const existing = cart.value.find(c => c.product_id === product.product_id)
  if (existing) {
    if (existing.quantity < product.stock) {
      existing.quantity++
    } else {
      ElMessage.warning('库存不足')
    }
  } else {
    cart.value.push({
      product_id: product.product_id,
      name: product.name,
      price: product.price,
      stock: product.stock,
      quantity: 1,
    })
  }
}

function removeFromCart(index) {
  cart.value.splice(index, 1)
}

function recalcTotal() {}

async function searchMembers(query) {
  if (!query) { memberOptions.value = []; return }
  memberSearching.value = true
  try {
    memberOptions.value = await getMembers({ keyword: query })
  } finally {
    memberSearching.value = false
  }
}

async function handleSubmit() {
  if (!selectedMemberId.value) {
    ElMessage.warning('请先选择会员')
    return
  }
  submitting.value = true
  try {
    await createOrder({
      member_id: selectedMemberId.value,
      items: cart.value.map(c => ({ product_id: c.product_id, quantity: c.quantity })),
    })
    ElMessage.success('下单成功')
    cart.value = []
    // 刷新商品列表
    products.value = await getProducts()
  } catch (e) { /* handled */ }
  finally { submitting.value = false }
}

onMounted(async () => {
  products.value = await getProducts()
})

// 补货
const restockVisible = ref(false)
const restockLoading = ref(false)
const restockProductData = ref(null)
const restockQty = ref(10)

function showRestockDialog(product) {
  restockProductData.value = product
  restockQty.value = 10
  restockVisible.value = true
}

async function handleRestock() {
  restockLoading.value = true
  try {
    await restockProduct(restockProductData.value.product_id, restockQty.value)
    ElMessage.success(`已为「${restockProductData.value.name}」补货 ${restockQty.value} 件`)
    restockVisible.value = false
    products.value = await getProducts()
  } catch (e) { /* handled */ }
  finally { restockLoading.value = false }
}
</script>

<style scoped>
.product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.product-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.product-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.product-item.unavailable {
  opacity: 0.5;
  cursor: not-allowed;
}

.product-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.product-price {
  color: #e74c3c;
  font-weight: 500;
}

.product-stock {
  font-size: 12px;
  color: #909399;
}

.total {
  font-size: 18px;
  margin-bottom: 12px;
}

.total span {
  color: #e74c3c;
  font-weight: bold;
  font-size: 24px;
}

.cart-footer {
  text-align: right;
}
</style>
