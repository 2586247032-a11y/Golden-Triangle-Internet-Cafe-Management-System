<template>
  <div class="member-home">
    <el-row :gutter="16">
      <!-- 余额卡片 -->
      <el-col :span="8">
        <el-card shadow="never" class="info-card">
          <div class="card-title">账户余额</div>
          <div class="card-value">¥{{ member?.balance?.toFixed(2) || '0.00' }}</div>
          <el-button type="primary" size="small" @click="rechargeVisible = true" style="margin-top: 12px">充值</el-button>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="info-card">
          <div class="card-title">累计充值</div>
          <div class="card-value">¥{{ member?.total_recharged?.toFixed(2) || '0.00' }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="info-card">
          <div class="card-title">积分</div>
          <div class="card-value">{{ member?.points || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近上机记录 -->
    <el-card shadow="never" style="margin-top: 20px">
      <template #header>最近上机记录</template>
      <el-table :data="sessions" stripe size="small" v-loading="loading">
        <el-table-column label="时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.start_time) }}</template>
        </el-table-column>
        <el-table-column label="时长" width="90">
          <template #default="{ row }">
            {{ row.end_time ? calcDuration(row.start_time, row.end_time) + ' 分钟' : '进行中' }}
          </template>
        </el-table-column>
        <el-table-column label="费用" width="80">
          <template #default="{ row }">¥{{ row.actual_amount?.toFixed(2) || '-' }}</template>
        </el-table-column>
        <el-table-column label="计费" width="80">
          <template #default="{ row }">{{ row.billing_mode === 'overnight' ? '包夜' : '按时' }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 充值对话框 -->
    <el-dialog v-model="rechargeVisible" title="充值" width="400px">
      <el-radio-group v-model="rechargeAmount" style="display: flex; flex-direction: column; gap: 8px">
        <el-radio v-for="t in tiers" :key="t.amount" :value="t.amount" border size="large">
          {{ t.amount }} 元 送 {{ t.bonus }} 元 → 到账 {{ t.amount + t.bonus }} 元
        </el-radio>
      </el-radio-group>
      <div style="margin-top: 16px; text-align: center" v-if="rechargeAmount > 0">
        到账：<strong style="color: #67c23a; font-size: 18px">{{ rechargeAmount + getBonus(rechargeAmount) }} 元</strong>
      </div>
      <template #footer>
        <el-button @click="rechargeVisible = false">取消</el-button>
        <el-button type="primary" :loading="rechargeLoading" @click="handleRecharge">确认充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getMemberDetail, rechargeMember } from '../api/members'
import { getSessions } from '../api/sessions'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const member = ref(null)
const sessions = ref([])
const loading = ref(false)
const rechargeVisible = ref(false)
const rechargeLoading = ref(false)
const rechargeAmount = ref(100)

const tiers = [
  { amount: 100, bonus: 30 },
  { amount: 200, bonus: 70 },
  { amount: 300, bonus: 120 },
  { amount: 500, bonus: 220 },
  { amount: 1000, bonus: 500 },
]

function getBonus(a) { for (const t of tiers) if (a >= t.amount) return t.bonus; return 0 }

function formatDateTime(dt) { if (!dt) return '-'; return dt.replace('T', ' ').substring(0, 19) }
function calcDuration(start, end) {
  if (!start || !end) return '-'
  return Math.round((new Date(end) - new Date(start)) / 60000)
}

async function loadData() {
  try {
    member.value = await getMemberDetail(authStore.user.user_id)
  } catch (e) { /* */ }
  loading.value = true
  try {
    sessions.value = await getSessions({ member_id: authStore.user.user_id })
  } finally { loading.value = false }
}

async function handleRecharge() {
  rechargeLoading.value = true
  try {
    await rechargeMember(authStore.user.user_id, { amount: rechargeAmount.value })
    ElMessage.success('充值成功')
    rechargeVisible.value = false
    loadData()
  } catch (e) { /* */ }
  finally { rechargeLoading.value = false }
}

onMounted(loadData)
</script>

<style scoped>
.info-card { text-align: center; }
.card-title { font-size: 13px; color: #909399; margin-bottom: 8px; }
.card-value { font-size: 28px; font-weight: bold; color: #303133; }
</style>
