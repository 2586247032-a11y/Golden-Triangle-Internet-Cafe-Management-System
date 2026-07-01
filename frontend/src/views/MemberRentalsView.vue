<template>
  <div class="member-rentals">
    <h3 style="margin-bottom: 16px">设备租借</h3>

    <!-- 可选设备卡片 -->
    <el-card shadow="never" style="margin-bottom: 20px">
      <template #header><span>可选设备</span></template>
      <div class="equipment-grid">
        <div v-for="equip in equipmentList" :key="equip.name"
             class="equipment-card" @click="selectEquipment(equip)">
          <div class="equip-icon">{{ equip.icon }}</div>
          <div class="equip-name">{{ equip.name }}</div>
          <div class="equip-price">¥{{ equip.fee }}/天</div>
          <div class="equip-desc">{{ equip.desc }}</div>
          <el-button type="primary" size="small" style="margin-top: 8px">申请租借</el-button>
        </div>
      </div>
    </el-card>

    <!-- 我的租借记录 -->
    <el-card shadow="never">
      <template #header><span>我的租借记录</span></template>
      <el-table :data="rentals" stripe v-loading="loading" empty-text="暂无租借记录">
        <el-table-column prop="equipment_name" label="设备" width="120" />
        <el-table-column label="日租费" width="80">
          <template #default="{ row }">¥{{ row.rental_fee_per_day.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="租借时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.start_time) }}</template>
        </el-table-column>
        <el-table-column label="归还时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.end_time) }}</template>
        </el-table-column>
        <el-table-column label="费用" width="80">
          <template #default="{ row }">{{ row.total_fee != null ? '¥' + row.total_fee.toFixed(2) : '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'warning' : 'success'" size="small">
              {{ row.status === 'active' ? '使用中' : '已归还' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 确认租借对话框 -->
    <el-dialog v-model="confirmVisible" title="确认租借" width="380px">
      <div v-if="selectedEquip" class="confirm-content">
        <div class="confirm-icon">{{ selectedEquip.icon }}</div>
        <h3>{{ selectedEquip.name }}</h3>
        <p>日租金：<strong style="color: #e74c3c; font-size: 18px">¥{{ selectedEquip.fee }}/天</strong></p>
        <p style="color: #909399; font-size: 13px">{{ selectedEquip.desc }}</p>
        <el-divider />
        <p style="color: #909399; font-size: 13px">提交后请到前台领取设备，归还时前台计算总费用</p>
      </div>
      <template #footer>
        <el-button @click="confirmVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">确认租借</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRentals, createRental } from '../api/rentals'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()

// 固定设备列表（价格不可改）
const equipmentList = [
  { name: '游戏耳机', fee: 10, icon: '🎧', desc: '7.1声道电竞耳机，带麦克风' },
  { name: '机械键盘', fee: 15, icon: '⌨️', desc: '青轴机械键盘，RGB背光' },
  { name: '充电宝', fee: 5, icon: '🔋', desc: '20000mAh大容量，支持快充' },
  { name: '游戏鼠标', fee: 8, icon: '🖱️', desc: '电竞鼠标，DPI可调' },
  { name: '游戏手柄', fee: 10, icon: '🎮', desc: 'Xbox布局手柄，无线连接' },
  { name: '摄像头', fee: 8, icon: '📷', desc: '1080P高清摄像头，带补光灯' },
]

const rentals = ref([])
const loading = ref(false)
const confirmVisible = ref(false)
const createLoading = ref(false)
const selectedEquip = ref(null)

function formatDateTime(dt) {
  if (!dt) return '-'
  return dt.replace('T', ' ').substring(0, 19)
}

function selectEquipment(equip) {
  selectedEquip.value = equip
  confirmVisible.value = true
}

async function loadRentals() {
  loading.value = true
  try {
    rentals.value = await getRentals({ member_id: authStore.user.user_id })
  } finally { loading.value = false }
}

async function handleCreate() {
  createLoading.value = true
  try {
    await createRental({
      member_id: authStore.user.user_id,
      equipment_name: selectedEquip.value.name,
      rental_fee_per_day: selectedEquip.value.fee,
    })
    ElMessage.success('申请成功，请到前台领取设备')
    confirmVisible.value = false
    loadRentals()
  } catch (e) { /* handled by interceptor */ }
  finally { createLoading.value = false }
}

onMounted(loadRentals)
</script>

<style scoped>
.equipment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.equipment-card {
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  padding: 16px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}

.equipment-card:hover {
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.equip-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.equip-name {
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 4px;
  color: #303133;
}

.equip-price {
  color: #e74c3c;
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 4px;
}

.equip-desc {
  font-size: 12px;
  color: #909399;
}

.confirm-content {
  text-align: center;
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 8px;
}
</style>
