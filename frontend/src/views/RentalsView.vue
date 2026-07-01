<template>
  <div class="rentals-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>设备租借</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon> 新建租借
          </el-button>
        </div>
      </template>

      <el-table :data="rentals" stripe v-loading="loading">
        <el-table-column prop="rental_id" label="ID" width="60" />
        <el-table-column prop="member_name" label="会员" width="100" />
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
          <template #default="{ row }">
            {{ row.total_fee != null ? '¥' + row.total_fee.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'warning' : 'success'" size="small">
              {{ row.status === 'active' ? '租借中' : '已归还' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'active'" type="success" size="small" @click="showReturnDialog(row)">
              归还
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建租借对话框 -->
    <el-dialog v-model="createVisible" title="新建租借" width="450px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="会员" prop="member_id">
          <el-select
            v-model="createForm.member_id"
            filterable
            remote
            :remote-method="searchMembers"
            :loading="memberSearching"
            placeholder="搜索会员"
            style="width: 100%"
          >
            <el-option v-for="m in memberOptions" :key="m.member_id" :label="`${m.name} (${m.phone})`" :value="m.member_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备名称" prop="equipment_name">
          <el-select v-model="createForm.equipment_name" placeholder="选择设备" style="width: 100%" allow-create filterable>
            <el-option label="游戏耳机" value="游戏耳机" />
            <el-option label="机械键盘" value="机械键盘" />
            <el-option label="充电宝" value="充电宝" />
            <el-option label="鼠标" value="鼠标" />
            <el-option label="手柄" value="手柄" />
          </el-select>
        </el-form-item>
        <el-form-item label="日租费(元)" prop="rental_fee_per_day">
          <el-input-number v-model="createForm.rental_fee_per_day" :min="1" :step="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">确认</el-button>
      </template>
    </el-dialog>

    <!-- 归还对话框 -->
    <el-dialog v-model="returnVisible" title="归还设备" width="400px">
      <div v-if="returnRental">
        <p>设备：<strong>{{ returnRental.equipment_name }}</strong></p>
        <p>日租费：¥{{ returnRental.rental_fee_per_day.toFixed(2) }}/天</p>
        <p>租借时间：{{ formatDateTime(returnRental.start_time) }}</p>
        <el-form label-width="80px" style="margin-top: 16px">
          <el-form-item label="使用天数">
            <el-input-number v-model="returnDays" :min="1" />
          </el-form-item>
          <el-form-item v-if="returnDays > 0" label="费用">
            <span style="font-size: 18px; color: #e74c3c; font-weight: bold">
              ¥{{ (returnRental.rental_fee_per_day * returnDays).toFixed(2) }}
            </span>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="returnVisible = false">取消</el-button>
        <el-button type="primary" :loading="returnLoading" @click="handleReturn">确认归还</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getRentals, createRental, returnRental as returnRentalApi } from '../api/rentals'
import { getMembers } from '../api/members'
import { ElMessage } from 'element-plus'

const rentals = ref([])
const loading = ref(false)

function formatDateTime(dt) {
  if (!dt) return '-'
  return dt.replace('T', ' ').substring(0, 19)
}

async function loadRentals() {
  loading.value = true
  try {
    rentals.value = await getRentals()
  } finally {
    loading.value = false
  }
}

// 新建
const createVisible = ref(false)
const createLoading = ref(false)
const createFormRef = ref(null)
const memberOptions = ref([])
const memberSearching = ref(false)
const createForm = reactive({
  member_id: null,
  equipment_name: '',
  rental_fee_per_day: 10,
})
const createRules = {
  member_id: [{ required: true, message: '请选择会员' }],
  equipment_name: [{ required: true, message: '请输入设备名称' }],
  rental_fee_per_day: [{ required: true, message: '请输入日租费' }],
}

function showCreateDialog() {
  createForm.member_id = null
  createForm.equipment_name = ''
  createForm.rental_fee_per_day = 10
  createVisible.value = true
}

async function searchMembers(query) {
  if (!query) { memberOptions.value = []; return }
  memberSearching.value = true
  try {
    memberOptions.value = await getMembers({ keyword: query })
  } finally {
    memberSearching.value = false
  }
}

async function handleCreate() {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return
  createLoading.value = true
  try {
    await createRental({ ...createForm })
    ElMessage.success('租借成功')
    createVisible.value = false
    loadRentals()
  } catch (e) { /* handled */ }
  finally { createLoading.value = false }
}

// 归还
const returnVisible = ref(false)
const returnLoading = ref(false)
const returnRental = ref(null)
const returnDays = ref(1)

function showReturnDialog(rental) {
  returnRental.value = rental
  returnDays.value = 1
  returnVisible.value = true
}

async function handleReturn() {
  returnLoading.value = true
  try {
    await returnRentalApi(returnRental.value.rental_id, { actual_days: returnDays.value })
    ElMessage.success('归还成功')
    returnVisible.value = false
    loadRentals()
  } catch (e) { /* handled */ }
  finally { returnLoading.value = false }
}

onMounted(loadRentals)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
