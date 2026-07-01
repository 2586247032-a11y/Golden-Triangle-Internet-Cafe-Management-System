<template>
  <div class="session-end">
    <el-card shadow="never" v-loading="loading">
      <template #header>
        <h3>下机结算</h3>
      </template>

      <div v-if="result">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="机器号">{{ result.computer_id }}</el-descriptions-item>
          <el-descriptions-item label="用户">
            {{ result.is_guest ? `散客(${result.guest_phone})` : `会员 ID: ${result.member_id}` }}
          </el-descriptions-item>
          <el-descriptions-item label="上机时间">{{ formatDateTime(result.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="下机时间">{{ formatDateTime(result.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="使用时长">{{ result.total_minutes }} 分钟</el-descriptions-item>
          <el-descriptions-item label="计费模式">
            <el-tag :type="result.billing_mode === 'overnight' ? 'warning' : 'info'">
              {{ result.billing_mode === 'overnight' ? '包夜封顶' : '按时计费' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="计费明细" :span="2">
            {{ result.billing_detail }}
          </el-descriptions-item>
          <el-descriptions-item label="实际收费">
            <span style="font-size: 24px; color: #e74c3c; font-weight: bold">
              ¥{{ result.actual_amount.toFixed(2) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { endSession } from '../api/sessions'

const route = useRoute()
const loading = ref(true)
const result = ref(null)

function formatDateTime(dt) {
  if (!dt) return '-'
  return dt.replace('T', ' ').substring(0, 19)
}

onMounted(async () => {
  try {
    result.value = await endSession(Number(route.params.id))
  } catch (e) {
    // handled
  } finally {
    loading.value = false
  }
})
</script>
