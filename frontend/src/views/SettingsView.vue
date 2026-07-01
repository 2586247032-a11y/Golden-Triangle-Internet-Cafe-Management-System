<template>
  <div class="settings-page">
    <!-- 区域定价 — 仅超级管理员可修改 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>区域定价管理</span>
          <el-tag v-if="!isSuper" type="info" size="small">仅超级管理员可修改</el-tag>
        </div>
      </template>
      <el-table :data="zones" stripe>
        <el-table-column prop="zone_name" label="区域" width="140" />
        <el-table-column label="会员价(元/h)" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.hourly_member" :min="1" :step="1" size="small" controls-position="right" :disabled="!isSuper" />
          </template>
        </el-table-column>
        <el-table-column label="散客价(元/h)" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.hourly_guest" :min="1" :step="1" size="small" controls-position="right" :disabled="!isSuper" />
          </template>
        </el-table-column>
        <el-table-column label="包夜会员价" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.overnight_member" :min="1" :step="1" size="small" controls-position="right" :disabled="!isSuper" />
          </template>
        </el-table-column>
        <el-table-column label="包夜散客价" width="130">
          <template #default="{ row }">
            <el-input-number v-model="row.overnight_guest" :min="1" :step="1" size="small" controls-position="right" :disabled="!isSuper" />
          </template>
        </el-table-column>
        <el-table-column v-if="isSuper" label="操作" width="80">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="saveZone(row)">保存</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 收银员账号管理 -->
    <el-card v-if="isSuper" shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>收银员账号管理</span>
          <el-button type="primary" size="small" @click="showAddOpDialog">添加收银员</el-button>
        </div>
      </template>
      <el-table :data="operators" stripe v-loading="opLoading">
        <el-table-column prop="operator_id" label="ID" width="60" />
        <el-table-column prop="login_name" label="登录账号" width="130" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'super_admin' ? 'danger' : 'warning'" size="small">
              {{ row.role === 'super_admin' ? '超级管理员' : '收银员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button v-if="row.role !== 'super_admin'" type="danger" size="small" @click="handleDeleteOp(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 系统配置 -->
    <el-card shadow="never" class="section-card">
      <template #header><span>系统配置</span></template>
      <el-form label-width="160px" style="max-width: 500px">
        <el-form-item v-for="cfg in configs" :key="cfg.config_key" :label="cfg.description || cfg.config_key">
          <template v-if="cfg.config_key === 'min_charge_threshold'">
            <el-input-number v-model="cfg.config_value" :min="0" :max="60" /> 分钟
          </template>
          <template v-else-if="cfg.config_key === 'holiday_surcharge'">
            <el-switch v-model="cfg.config_value" active-value="1" inactive-value="0" />
          </template>
          <template v-else>
            <el-input v-model="cfg.config_value" />
          </template>
          <el-button type="primary" size="small" style="margin-left: 12px" @click="saveConfig(cfg)">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 添加收银员对话框 -->
    <el-dialog v-model="addOpVisible" title="添加收银员" width="400px">
      <el-form ref="opFormRef" :model="opForm" :rules="opRules" label-width="80px">
        <el-form-item label="登录账号" prop="login">
          <el-input v-model="opForm.login" placeholder="英文或数字" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="opForm.name" placeholder="收银员姓名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="opForm.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addOpVisible = false">取消</el-button>
        <el-button type="primary" :loading="addOpLoading" @click="handleAddOp">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getSettings, updateSetting, getZoneSettings, updateZonePricing, getOperators, createOperator, deleteOperator } from '../api/rentals'
import { useAuthStore } from '../stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const isSuper = computed(() => authStore.role === 'super_admin')

const zones = ref([])
const configs = ref([])
const operators = ref([])
const opLoading = ref(false)

function formatDateTime(dt) { if (!dt) return '-'; return dt.replace('T', ' ').substring(0, 19) }

async function loadSettings() {
  const [zoneRes, configRes] = await Promise.all([getZoneSettings(), getSettings()])
  zones.value = zoneRes
  configs.value = configRes
  if (isSuper.value) loadOperators()
}

async function loadOperators() {
  opLoading.value = true
  try { operators.value = await getOperators() } catch (e) { /* */ }
  finally { opLoading.value = false }
}

async function saveZone(zone) {
  try {
    await updateZonePricing(zone.zone_id, {
      hourly_member: zone.hourly_member,
      hourly_guest: zone.hourly_guest,
      overnight_member: zone.overnight_member,
      overnight_guest: zone.overnight_guest,
    })
    ElMessage.success('定价已保存')
  } catch (e) { /* */ }
}

async function saveConfig(cfg) {
  try {
    await updateSetting(cfg.config_key, { config_value: String(cfg.config_value) })
    ElMessage.success('配置已保存')
  } catch (e) { /* */ }
}

// 收银员管理
const addOpVisible = ref(false)
const addOpLoading = ref(false)
const opFormRef = ref(null)
const opForm = reactive({ login: '', password: '', name: '' })
const opRules = {
  login: [{ required: true, message: '请输入账号', trigger: 'blur' }, { min: 3, message: '至少3位', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '至少6位', trigger: 'blur' }],
}

function showAddOpDialog() { opForm.login = ''; opForm.password = ''; opForm.name = ''; addOpVisible.value = true }
async function handleAddOp() {
  const valid = await opFormRef.value.validate().catch(() => false)
  if (!valid) return
  addOpLoading.value = true
  try {
    await createOperator(opForm.login, opForm.password, opForm.name)
    ElMessage.success('收银员账号已创建')
    addOpVisible.value = false
    loadOperators()
  } catch (e) { /* */ }
  finally { addOpLoading.value = false }
}

async function handleDeleteOp(op) {
  const ok = await ElMessageBox.confirm(`确定删除收银员 ${op.login_name} 吗？`, '确认删除', { type: 'warning' }).catch(() => false)
  if (!ok) return
  try {
    await deleteOperator(op.operator_id)
    ElMessage.success('已删除')
    loadOperators()
  } catch (e) { /* */ }
}

onMounted(loadSettings)
</script>

<style scoped>
.settings-page {
  max-width: 1100px;
}

.section-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
