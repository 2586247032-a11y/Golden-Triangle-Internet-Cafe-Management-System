<template>
  <div class="counter">
    <!-- 顶部操作栏 -->
    <div class="counter-header">
      <div class="header-left">
        <h2>收银台</h2>
        <el-button type="primary" @click="router.push('/session/new')">
          <el-icon><Plus /></el-icon> 开卡上机
        </el-button>
      </div>
      <div class="header-right">
        <span class="status-dot free"></span> 空闲
        <span class="status-dot using"></span> 使用中
        <span class="status-dot fault"></span> 故障
      </div>
    </div>

    <!-- ====== 区域一：普通大厅区 (A001-A096) ====== -->
    <div class="floor-section hall-section">
      <div class="section-header">
        <span class="section-label">普通大厅区</span>
        <el-tag size="small" effect="plain">{{ hallComputers.length }} 台</el-tag>
      </div>
      <div class="hall-layout">
        <div v-for="(row, ri) in hallRows" :key="'row'+ri" class="hall-row">
          <span class="row-label" v-if="ri % 2 === 0">{{ ['A区前排', 'C区中排', 'E区后排', 'G区后后排'][ri / 2] || '' }}</span>
          <span class="row-label" v-else></span>
          <div class="hall-seats">
            <div
              v-for="pc in row"
              :key="pc.computer_id"
              :class="['seat-card', pc.status]"
              @click="onCardClick(pc)"
              :title="pc.computer_no + (pc.status === 'using' && pc.session ? ' - ' + (pc.session.member_name || '散客') : '')"
            >
              <div class="seat-no">{{ pc.computer_no.replace('A0', 'A').replace('A00', 'A') }}</div>
              <div v-if="pc.status === 'using' && pc.session" class="seat-user">
                {{ formatTime(pc.session.elapsed_minutes) }}
              </div>
              <div v-if="pc.status === 'using' && pc.session" class="seat-price">
                ¥{{ pc.session.estimated_amount.toFixed(1) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ====== 区域二：电竞大厅区 (B001-B034) ====== -->
    <div class="floor-section hall-section">
      <div class="section-header">
        <span class="section-label">电竞大厅区</span>
        <el-tag size="small" effect="plain" type="warning">{{ esportsComputers.length }} 台</el-tag>
      </div>
      <div class="esports-layout">
        <div class="esports-row">
          <div class="esports-group" v-for="(group, gi) in esportsGroups" :key="'eg'+gi">
            <div class="group-label">{{ ['五连座 A', '五连座 B', '五连座 C', '五连座 D', '五连座 E', '四连座 F', '五连座 G'][gi] || '' }}</div>
            <div class="group-seats">
              <div
                v-for="pc in group"
                :key="pc.computer_id"
                :class="['seat-card', 'esports-seat', pc.status]"
                @click="onCardClick(pc)"
                :title="pc.computer_no"
              >
                <div class="seat-no">{{ pc.computer_no }}</div>
                <div v-if="pc.status === 'using' && pc.session" class="seat-user">{{ formatTime(pc.session.elapsed_minutes) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ====== 区域三&四&五：包间区 ====== -->
    <div class="floor-section rooms-section">
      <div class="section-header">
        <span class="section-label">包间区</span>
        <el-tag size="small" effect="plain" type="info">{{ roomComputers.length }} 台</el-tag>
      </div>
      <div class="rooms-layout">
        <!-- 双人包间 C101-C108（8间）-->
        <div v-for="room in doubleRooms" :key="'d'+room.room_no" class="room-card double-room">
          <div class="room-header">
            <span>{{ room.room_no }} 双人包间</span>
            <el-tag size="small" :type="roomStatusType(room)">{{ roomStatusText(room) }}</el-tag>
          </div>
          <div class="room-seats">
            <div
              v-for="pc in room.computers"
              :key="pc.computer_id"
              :class="['seat-card', 'room-seat', pc.status]"
              @click="onCardClick(pc)"
            >
              <div class="seat-no">{{ pc.computer_no.split('-')[1] }}号机</div>
              <div v-if="pc.status === 'using' && pc.session" class="seat-user">
                {{ formatTime(pc.session.elapsed_minutes) }}
              </div>
              <div v-if="pc.status === 'using' && pc.session" class="seat-price">
                ¥{{ pc.session.estimated_amount.toFixed(1) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 五人战队包间 D201-D202（2间）-->
        <div v-for="room in teamRooms" :key="'t'+room.room_no" class="room-card team-room">
          <div class="room-header">
            <span>{{ room.room_no }} 五人战队包间</span>
            <el-tag size="small" :type="roomStatusType(room)">{{ roomStatusText(room) }}</el-tag>
          </div>
          <div class="room-seats team-seats">
            <div
              v-for="(pc, idx) in room.computers"
              :key="pc.computer_id"
              :class="['seat-card', 'room-seat', pc.status]"
              @click="onCardClick(pc)"
            >
              <div class="seat-no">{{ idx + 1 }}号位</div>
              <div v-if="pc.status === 'using' && pc.session" class="seat-user">{{ formatTime(pc.session.elapsed_minutes) }}</div>
            </div>
          </div>
        </div>

        <!-- 单人私密包间 E301-E304（4间）-->
        <div v-for="room in soloRooms" :key="'s'+room.room_no" class="room-card solo-room">
          <div class="room-header">
            <span>{{ room.room_no }} 单人包间</span>
            <el-tag size="small" :type="roomStatusType(room)">{{ roomStatusText(room) }}</el-tag>
          </div>
          <div class="room-seats solo-seat">
            <div
              v-for="pc in room.computers"
              :key="pc.computer_id"
              :class="['seat-card', 'room-seat', 'solo-card', pc.status]"
              @click="onCardClick(pc)"
            >
              <div class="seat-no">{{ pc.computer_no }}</div>
              <div v-if="pc.status === 'using' && pc.session" class="seat-user">{{ formatTime(pc.session.elapsed_minutes) }}</div>
              <div v-if="pc.status === 'using' && pc.session" class="seat-price">¥{{ pc.session.estimated_amount.toFixed(1) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 进行中的会话列表 -->
    <el-card class="active-sessions" shadow="never">
      <template #header>
        <span>当前上机列表（{{ activeSessions.length }} 人）</span>
        <el-button text size="small" @click="refreshActive" style="float: right">刷新</el-button>
      </template>
      <el-table :data="activeSessions" stripe size="small" style="width: 100%">
        <el-table-column prop="computer_no" label="机器号" width="100" />
        <el-table-column prop="zone_name" label="区域" width="120" />
        <el-table-column label="用户" width="130">
          <template #default="{ row }">
            {{ row.is_guest ? `散客(${row.guest_phone})` : (row.member_name || '-') }}
          </template>
        </el-table-column>
        <el-table-column label="上机时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.start_time) }}</template>
        </el-table-column>
        <el-table-column label="时长" width="90">
          <template #default="{ row }">{{ formatTime(row.elapsed_minutes) }}</template>
        </el-table-column>
        <el-table-column label="预估费用" width="90">
          <template #default="{ row }">¥{{ row.estimated_amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="操作" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleEndSession(row)">下机结算</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 结算对话框 -->
    <el-dialog v-model="settleVisible" title="下机结算" width="500px" @closed="settleResult = null">
      <div v-if="settleResult" class="settle-result">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="机器号">{{ settleResult.computer_no || settleResult.computer_id }}</el-descriptions-item>
          <el-descriptions-item label="上机时间">{{ formatDateTime(settleResult.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="下机时间">{{ formatDateTime(settleResult.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="使用时长">{{ settleResult.total_minutes }} 分钟</el-descriptions-item>
          <el-descriptions-item label="计费模式">
            <el-tag :type="settleResult.billing_mode === 'overnight' ? 'warning' : 'info'" size="small">
              {{ settleResult.billing_mode === 'overnight' ? '包夜封顶' : '按时计费' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实际收费">
            <span class="settle-amount">¥{{ settleResult.actual_amount.toFixed(2) }}</span>
          </el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <p class="billing-detail">{{ settleResult.billing_detail }}</p>
        <el-divider />
        <div class="payment-section">
          <el-form label-width="80px">
            <el-form-item label="支付方式">
              <el-select v-model="paymentMethod" placeholder="选择支付方式">
                <el-option label="现金" value="现金" />
                <el-option label="微信" value="微信" />
                <el-option label="支付宝" value="支付宝" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="paymentMethod === '现金'" label="收款金额">
              <el-input-number v-model="receivedAmount" :min="0" :step="10" />
              <span class="change-amount">
                找零：¥{{ Math.max(0, receivedAmount - settleResult.actual_amount).toFixed(2) }}
              </span>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <div v-else v-loading="settleLoading" style="min-height: 200px; text-align: center; padding-top: 80px;">
        <p>正在计算费用...</p>
      </div>
      <template #footer>
        <el-button @click="settleVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getComputers, getZones } from '../api/computers'
import { getActiveSessions, endSession } from '../api/sessions'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

const computers = ref([])
const activeSessions = ref([])
const settleVisible = ref(false)
const settleLoading = ref(false)
const settleResult = ref(null)
const paymentMethod = ref('现金')
const receivedAmount = ref(0)
let refreshTimer = null

// 带 session 信息的电脑列表
const computersWithSession = computed(() => {
  return computers.value.map(pc => ({
    ...pc,
    session: activeSessions.value.find(s => s.computer_id === pc.computer_id) || null,
  }))
})

// === 普通大厅区：8行×12列 ===
const hallComputers = computed(() => {
  return computersWithSession.value.filter(pc => pc.computer_no && pc.computer_no.startsWith('A'))
})

const hallRows = computed(() => {
  const pcs = [...hallComputers.value]
  const rows = []
  while (pcs.length > 0) {
    rows.push(pcs.splice(0, 12))
  }
  return rows
})

// === 电竞大厅区：按组排列 ===
const esportsComputers = computed(() => {
  return computersWithSession.value.filter(pc => pc.computer_no && pc.computer_no.startsWith('B'))
})

const esportsGroups = computed(() => {
  const pcs = [...esportsComputers.value]
  const groups = [[], [], [], [], [], [], []]
  // B001-B005 → 五连座A, B006-B010 → 五连座B, ... B026-B030 → 五连座E, B031-B034 → 四连座F
  const sizes = [5, 5, 5, 5, 5, 4, 5] // last group B031-B034 is actually 4
  let idx = 0
  for (let g = 0; g < 7; g++) {
    groups[g] = pcs.slice(idx, idx + sizes[g])
    idx += sizes[g]
  }
  return groups.filter(g => g.length > 0)
})

// === 包间区 ===
const roomComputers = computed(() => {
  return computersWithSession.value.filter(pc => pc.room_no)
})

// 按房间号分组
const roomsGrouped = computed(() => {
  const map = {}
  roomComputers.value.forEach(pc => {
    if (!map[pc.room_no]) map[pc.room_no] = { room_no: pc.room_no, computers: [] }
    map[pc.room_no].computers.push(pc)
  })
  return Object.values(map).sort((a, b) => a.room_no.localeCompare(b.room_no))
})

const doubleRooms = computed(() => roomsGrouped.value.filter(r => r.room_no.startsWith('C')))
const teamRooms = computed(() => roomsGrouped.value.filter(r => r.room_no.startsWith('D')))
const soloRooms = computed(() => roomsGrouped.value.filter(r => r.room_no.startsWith('E')))

function roomStatusType(room) {
  const hasUsing = room.computers.some(pc => pc.status === 'using')
  const allFree = room.computers.every(pc => pc.status === 'free')
  const hasFault = room.computers.some(pc => pc.status === 'fault')
  if (hasUsing) return 'primary'
  if (allFree) return 'success'
  if (hasFault) return 'danger'
  return 'info'
}

function roomStatusText(room) {
  const free = room.computers.filter(pc => pc.status === 'free').length
  const using = room.computers.filter(pc => pc.status === 'using').length
  const fault = room.computers.filter(pc => pc.status === 'fault').length
  const parts = []
  if (using > 0) parts.push(`${using}人使用中`)
  if (free > 0) parts.push(`${free}空闲`)
  if (fault > 0) parts.push(`${fault}故障`)
  return parts.join(' / ') || '空闲'
}

function formatTime(minutes) {
  if (!minutes && minutes !== 0) return '-'
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h${m}m` : `${m}m`
}

function formatDateTime(dt) {
  if (!dt) return '-'
  return dt.replace('T', ' ').substring(0, 19)
}

function onCardClick(pc) {
  if (pc.status === 'free') {
    router.push('/session/new')
  } else if (pc.status === 'using' && pc.session) {
    handleEndSession(pc.session)
  }
}

async function handleEndSession(session) {
  const ok = await ElMessageBox.confirm(
    `确定要结束 ${session.computer_no}（${session.member_name || '散客'}）的上机吗？`,
    '下机确认',
    { confirmButtonText: '确认下机', cancelButtonText: '取消', type: 'warning' }
  ).catch(() => false)
  if (!ok) return

  settleVisible.value = true
  settleLoading.value = true
  settleResult.value = null
  paymentMethod.value = '现金'
  receivedAmount.value = 0

  try {
    const res = await endSession(session.record_id)
    settleResult.value = { ...res, computer_no: session.computer_no }
    await refreshAll()
  } catch (e) {
    settleVisible.value = false
  } finally {
    settleLoading.value = false
  }
}

async function refreshActive() {
  try {
    activeSessions.value = await getActiveSessions()
  } catch (e) { /* ignore */ }
}

async function loadComputers() {
  computers.value = await getComputers()
}

async function refreshAll() {
  await Promise.all([loadComputers(), refreshActive()])
}

onMounted(() => {
  refreshAll()
  refreshTimer = setInterval(refreshActive, 3000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.counter {
  max-width: 1400px;
}

.counter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px 16px;
  font-size: 13px;
  color: #606266;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 4px;
}

.status-dot.free { background: #67c23a; }
.status-dot.using { background: #409eff; }
.status-dot.fault { background: #f56c6c; }

/* ===== 区域标题 ===== */
.floor-section {
  margin-bottom: 28px;
  background: #fff;
  border-radius: 10px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.section-label {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

/* ===== 普通大厅：行列布局 ===== */
.hall-layout {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hall-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.row-label {
  width: 70px;
  font-size: 11px;
  color: #909399;
  text-align: right;
  flex-shrink: 0;
}

.hall-seats {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* ===== 电竞区 ===== */
.esports-layout {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.esports-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.esports-group {
  border: 1px dashed #e4e7ed;
  border-radius: 8px;
  padding: 8px;
  background: #fafafa;
}

.group-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
  text-align: center;
}

.group-seats {
  display: flex;
  gap: 4px;
}

/* ===== 包间 ===== */
.rooms-layout {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.room-card {
  border: 2px solid #e4e7ed;
  border-radius: 10px;
  padding: 10px 14px;
  background: #fafcff;
  min-width: 160px;
}

.room-card.double-room { border-color: #d3e4fd; background: #f5f9ff; }
.room-card.team-room { border-color: #fde2d3; background: #fffaf5; }
.room-card.solo-room { border-color: #d3fde2; background: #f5fff9; }

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.room-seats {
  display: flex;
  gap: 6px;
}

.solo-seat { justify-content: center; }

/* ===== 座位卡片（统一） ===== */
.seat-card {
  width: 52px;
  height: 64px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.12s, box-shadow 0.12s;
  position: relative;
}

.seat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 3px 10px rgba(0,0,0,0.12);
  z-index: 1;
}

.seat-card.free {
  background: #f0f9eb;
  border: 1.5px solid #b3e19d;
}

.seat-card.using {
  background: #ecf5ff;
  border: 1.5px solid #93c5fd;
}

.seat-card.fault {
  background: #fef0f0;
  border: 1.5px solid #fca5a5;
  cursor: default;
  opacity: 0.7;
}

.seat-no {
  font-size: 12px;
  font-weight: 700;
  color: #303133;
}

.seat-user {
  font-size: 10px;
  color: #409eff;
  margin-top: 1px;
}

.seat-price {
  font-size: 10px;
  color: #e74c3c;
  font-weight: 500;
}

/* 电竞区座位稍大 */
.esports-seat {
  width: 56px;
  height: 64px;
}

/* 包间座位 */
.room-seat {
  width: 58px;
  height: 66px;
}

.solo-card {
  width: 100px;
  height: 80px;
}

/* ===== 下方会话列表 ===== */
.active-sessions {
  margin-top: 20px;
}

.settle-amount {
  color: #e74c3c;
  font-size: 22px;
  font-weight: bold;
}

.billing-detail {
  color: #606266;
  line-height: 1.8;
  font-size: 14px;
}

.change-amount {
  margin-left: 12px;
  color: #67c23a;
  font-weight: 500;
}

.payment-section {
  margin-top: 8px;
}
</style>
