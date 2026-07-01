<template>
  <div class="members-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>会员管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon> 注册新会员
          </el-button>
        </div>
      </template>

      <!-- 搜索 -->
      <el-input
        v-model="keyword"
        placeholder="搜索姓名或手机号"
        clearable
        style="width: 300px; margin-bottom: 16px"
        @input="debounceSearch"
      />

      <!-- 会员列表 -->
      <el-table :data="members" stripe v-loading="loading">
        <el-table-column prop="member_id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column label="余额" width="100">
          <template #default="{ row }">¥{{ row.balance.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="累计充值" width="100">
          <template #default="{ row }">¥{{ row.total_recharged.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="points" label="积分" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="showRechargeDialog(row)">充值</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 注册对话框 -->
    <el-dialog v-model="createVisible" title="注册新会员" width="450px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="80px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="createForm.phone" placeholder="请输入 11 位手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="createForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">确认注册</el-button>
      </template>
    </el-dialog>

    <!-- 充值对话框 -->
    <el-dialog v-model="rechargeVisible" title="会员充值" width="450px">
      <div v-if="rechargeMember" style="margin-bottom: 16px">
        <p>会员：<strong>{{ rechargeMember.name }}</strong></p>
        <p>当前余额：<strong style="color: #409eff">¥{{ rechargeMember.balance.toFixed(2) }}</strong></p>
      </div>
      <el-form label-width="80px">
        <el-form-item label="充值金额">
          <el-radio-group v-model="rechargeAmount" style="margin-bottom: 12px">
            <el-radio v-for="t in tiers" :key="t.amount" :value="t.amount" border size="small" style="margin-bottom: 8px">
              {{ t.amount }} 元
              <template v-if="t.bonus > 0">（送 {{ t.bonus }} 元）</template>
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="rechargeAmount > 0">
          <span>到账金额：<strong style="color: #67c23a">{{ rechargeAmount + getBonus(rechargeAmount) }} 元</strong></span>
          <span v-if="getBonus(rechargeAmount) > 0" style="margin-left: 12px; color: #e6a23c">
            （含赠送 {{ getBonus(rechargeAmount) }} 元）
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rechargeVisible = false">取消</el-button>
        <el-button type="primary" :loading="rechargeLoading" @click="handleRecharge">确认充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getMembers, createMember, rechargeMember as rechargeMemberApi } from '../api/members'
import { ElMessage } from 'element-plus'

const members = ref([])
const loading = ref(false)
const keyword = ref('')
let searchTimer = null

const tiers = [
  { amount: 100, bonus: 30 },
  { amount: 200, bonus: 70 },
  { amount: 300, bonus: 120 },
  { amount: 500, bonus: 220 },
  { amount: 1000, bonus: 500 },
]

function getBonus(amount) {
  let bonus = 0
  for (const t of tiers) {
    if (amount >= t.amount) bonus = t.bonus
  }
  return bonus
}

function debounceSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadMembers, 300)
}

async function loadMembers() {
  loading.value = true
  try {
    members.value = await getMembers({ keyword: keyword.value || undefined })
  } finally {
    loading.value = false
  }
}

// 注册
const createVisible = ref(false)
const createLoading = ref(false)
const createFormRef = ref(null)
const createForm = reactive({ name: '', phone: '', password: '' })
const createRules = {
  name: [{ required: true, message: '请输入姓名' }],
  phone: [
    { required: true, message: '请输入手机号' },
    { pattern: /^\d{11}$/, message: '手机号格式错误' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

function showCreateDialog() {
  createForm.name = ''
  createForm.phone = ''
  createForm.password = ''
  createVisible.value = true
}

async function handleCreate() {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return
  createLoading.value = true
  try {
    await createMember({ ...createForm })
    ElMessage.success('注册成功')
    createVisible.value = false
    loadMembers()
  } catch (e) { /* handled */ }
  finally { createLoading.value = false }
}

// 充值
const rechargeVisible = ref(false)
const rechargeLoading = ref(false)
const rechargeMember = ref(null)
const rechargeAmount = ref(0)

function showRechargeDialog(member) {
  rechargeMember.value = member
  rechargeAmount.value = 100
  rechargeVisible.value = true
}

async function handleRecharge() {
  if (rechargeAmount.value <= 0) {
    ElMessage.warning('请选择充值金额')
    return
  }
  rechargeLoading.value = true
  try {
    await rechargeMemberApi(rechargeMember.value.member_id, {
      amount: rechargeAmount.value,
      operator: '',
    })
    ElMessage.success('充值成功')
    rechargeVisible.value = false
    loadMembers()
  } catch (e) { /* handled */ }
  finally { rechargeLoading.value = false }
}

onMounted(loadMembers)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
