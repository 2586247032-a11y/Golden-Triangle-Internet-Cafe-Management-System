<template>
  <div class="dashboard">
    <!-- KPI 卡片 -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <el-card shadow="never" class="kpi-card">
          <div class="kpi-label">今日上网营收</div>
          <div class="kpi-value">¥{{ revenue.session.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="kpi-card">
          <div class="kpi-label">今日商品营收</div>
          <div class="kpi-value">¥{{ revenue.product.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="kpi-card">
          <div class="kpi-label">今日租借营收</div>
          <div class="kpi-value">¥{{ revenue.rental.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never" class="kpi-card">
          <div class="kpi-label">总营收 / 上座率</div>
          <div class="kpi-value">
            ¥{{ revenue.total.toFixed(2) }}
            <span style="font-size: 14px; color: #909399; margin-left: 8px">
              {{ occupancy }}%
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 各区域状态 -->
    <el-card shadow="never" class="section-card">
      <template #header><span>各区域机器状态</span></template>
      <el-table :data="zoneOverview" stripe size="small">
        <el-table-column prop="zone_name" label="区域" />
        <el-table-column prop="total" label="总数" width="80" />
        <el-table-column label="空闲" width="80">
          <template #default="{ row }">
            <el-tag type="success" size="small">{{ row.free }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="使用中" width="80">
          <template #default="{ row }">
            <el-tag type="primary" size="small">{{ row.using }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="故障" width="80">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ row.fault }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="使用率" min-width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.total > 0 ? Math.round(row.using / row.total * 100) : 0"
              :color="row.using / row.total > 0.8 ? '#f56c6c' : '#409eff'"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 最近上机记录 -->
    <el-card shadow="never" class="section-card">
      <template #header><span>最近上机记录</span></template>
      <el-table :data="recentSessions" stripe size="small" v-loading="sessionsLoading">
        <el-table-column prop="computer_no" label="机器号" width="100" />
        <el-table-column prop="member_name" label="用户" width="100" />
        <el-table-column label="上机时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.start_time) }}</template>
        </el-table-column>
        <el-table-column label="下机时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.end_time) }}</template>
        </el-table-column>
        <el-table-column prop="billing_mode" label="计费模式" width="100">
          <template #default="{ row }">
            <el-tag :type="row.billing_mode === 'overnight' ? 'warning' : 'info'" size="small">
              {{ row.billing_mode === 'overnight' ? '包夜' : '按时' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="80">
          <template #default="{ row }">
            ¥{{ row.actual_amount != null ? row.actual_amount.toFixed(2) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getDashboardRevenue, getSessions } from '../api/sessions'

const revenue = reactive({ session: 0, product: 0, rental: 0, total: 0 })
const occupancy = ref(0)
const zoneOverview = ref([])
const recentSessions = ref([])
const sessionsLoading = ref(false)

function formatDateTime(dt) {
  if (!dt) return '-'
  return dt.replace('T', ' ').substring(0, 19)
}

onMounted(async () => {
  try {
    const dash = await getDashboardRevenue()
    revenue.session = dash.today_revenue.session
    revenue.product = dash.today_revenue.product
    revenue.rental = dash.today_revenue.rental
    revenue.total = dash.today_revenue.total
    occupancy.value = dash.occupancy_rate
    zoneOverview.value = dash.zone_overview
  } catch (e) { /* ignore */ }

  sessionsLoading.value = true
  try {
    recentSessions.value = (await getSessions()).slice(0, 10)
  } finally {
    sessionsLoading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.kpi-row {
  margin-bottom: 20px;
}

.kpi-card {
  text-align: center;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.kpi-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.section-card {
  margin-bottom: 20px;
}
</style>
