<template>
  <div class="session-new">
    <el-card shadow="never">
      <template #header><h3>开卡上机</h3></template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" style="max-width: 600px">
        <!-- 用户类型 -->
        <el-form-item label="用户类型" prop="userType">
          <el-radio-group v-model="form.userType" @change="onUserTypeChange">
            <el-radio-button value="member">会员</el-radio-button>
            <el-radio-button value="guest">散客</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 会员选择 -->
        <template v-if="form.userType === 'member'">
          <el-form-item label="会员" prop="member_id">
            <el-select
              v-model="form.member_id"
              filterable
              remote
              :remote-method="searchMembers"
              :loading="memberSearching"
              placeholder="输入手机号或姓名搜索"
              style="width: 100%"
            >
              <el-option
                v-for="m in memberOptions"
                :key="m.member_id"
                :label="`${m.name} (${m.phone}) - 余额 ¥${m.balance}`"
                :value="m.member_id"
              />
            </el-select>
          </el-form-item>
        </template>

        <!-- 散客手机号 -->
        <template v-if="form.userType === 'guest'">
          <el-form-item label="手机号" prop="guest_phone">
            <el-input v-model="form.guest_phone" placeholder="请输入 11 位手机号" maxlength="11" />
          </el-form-item>
        </template>

        <!-- 区域选择 -->
        <el-form-item label="区域" prop="zone_id">
          <el-select v-model="form.zone_id" placeholder="选择区域" style="width: 100%" @change="onZoneChange">
            <el-option
              v-for="z in zones"
              :key="z.zone_id"
              :label="`${z.zone_name}（空闲 ${z.free_count || 0} 台）`"
              :value="z.zone_id"
            />
          </el-select>
        </el-form-item>

        <!-- 机器选择 -->
        <el-form-item label="机器" prop="computer_id">
          <el-select v-model="form.computer_id" placeholder="选择空闲机器" style="width: 100%">
            <el-option
              v-for="pc in availableComputers"
              :key="pc.computer_id"
              :label="`${pc.computer_no}${pc.room_no ? ' (' + pc.room_no + ')' : ''}`"
              :value="pc.computer_id"
            />
          </el-select>
        </el-form-item>

        <!-- 定价预览 -->
        <el-form-item v-if="selectedZone" label="定价">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="会员价">
              ¥{{ selectedZone.hourly_member }}/h
            </el-descriptions-item>
            <el-descriptions-item label="散客价">
              ¥{{ selectedZone.hourly_guest }}/h
            </el-descriptions-item>
            <el-descriptions-item label="包夜会员价">
              ¥{{ selectedZone.overnight_member }}
            </el-descriptions-item>
            <el-descriptions-item label="包夜散客价">
              ¥{{ selectedZone.overnight_guest }}
            </el-descriptions-item>
          </el-descriptions>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
            确认开卡
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getComputers } from '../api/computers'
import { getMembers } from '../api/members'
import { startSession } from '../api/sessions'
import { getZones } from '../api/computers'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const memberSearching = ref(false)
const memberOptions = ref([])
const zones = ref([])
const allComputers = ref([])

const form = reactive({
  userType: 'member',
  member_id: null,
  guest_phone: '',
  zone_id: null,
  computer_id: null,
})

const rules = {
  userType: [{ required: true }],
  member_id: [
    { required: true, message: '请选择会员', trigger: 'change' },
  ],
  guest_phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^\d{11}$/, message: '手机号格式错误', trigger: 'blur' },
  ],
  zone_id: [{ required: true, message: '请选择区域', trigger: 'change' }],
  computer_id: [{ required: true, message: '请选择机器', trigger: 'change' }],
}

const selectedZone = computed(() => {
  return zones.value.find(z => z.zone_id === form.zone_id) || null
})

const availableComputers = computed(() => {
  return allComputers.value.filter(
    pc => pc.zone_id === form.zone_id && pc.status === 'free'
  )
})

function onUserTypeChange() {
  form.member_id = null
  form.guest_phone = ''
}

function onZoneChange() {
  form.computer_id = null
}

async function searchMembers(query) {
  if (!query || query.length < 1) {
    memberOptions.value = []
    return
  }
  memberSearching.value = true
  try {
    memberOptions.value = await getMembers({ keyword: query })
  } finally {
    memberSearching.value = false
  }
}

async function handleSubmit() {
  // 动态校验条件
  const effectiveRules = { ...rules }
  if (form.userType === 'member') {
    effectiveRules.guest_phone = []
  } else {
    effectiveRules.member_id = []
  }

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await startSession({
      computer_id: form.computer_id,
      member_id: form.userType === 'member' ? form.member_id : null,
      is_guest: form.userType === 'guest',
      guest_phone: form.userType === 'guest' ? form.guest_phone : null,
    })
    ElMessage.success('开卡成功')
    router.push('/counter')
  } catch (e) {
    // handled by interceptor
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const [compRes, zoneRes] = await Promise.all([getComputers(), getZones()])
  allComputers.value = compRes
  // 统计每个区域的空闲机器数
  zones.value = zoneRes.map(z => ({
    ...z,
    free_count: compRes.filter(c => c.zone_id === z.zone_id && c.status === 'free').length,
  }))
})
</script>
