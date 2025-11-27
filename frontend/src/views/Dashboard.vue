<template>
  <div class="dashboard">
    <!-- 日期选择器 -->
    <div class="date-selector">
      <el-card>
        <el-row align="middle">
          <el-col :span="4">
            <span class="label">选择查询日期：</span>
          </el-col>
          <el-col :span="6">
            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="onDateChange"
            />
          </el-col>
          <el-col :span="4" :offset="1">
            <el-button type="primary" @click="loadAllData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- ==================== 天级明细数据区域 ==================== -->
    
    <!-- 1. 总体明细数据 -->
    <el-row class="comprehensive-stats">
      <el-col :span="24">
        <ComprehensiveStatsCard 
          :stats="comprehensiveStats" 
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 2. 错误明细数据 -->
    <el-row class="error-details-section">
      <el-col :span="24">
        <ErrorDetailsCard
          :agent-error-data="agentErrorData"
          :ds-error-data="dsErrorData"
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 3. 性能明细数据 -->
    <!-- 3.1 查询耗时明细数据 -->
    <el-row class="performance-details-section">
      <el-col :span="24">
        <PerformanceDetailsCard
          :template-performance="templatePerformance"
          :non-template-performance="nonTemplatePerformance"
          :loading="loading"
          @view-detail="viewPerformanceDetail"
        />
      </el-col>
    </el-row>

    <!-- 3.2 环节耗时明细数据 -->
    <el-row class="step-performance">
      <el-col :span="24">
        <StepPerformanceCard 
          title="环节耗时明细数据" 
          :steps="stepPerformance" 
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 4. 业务明细数据 -->
    <el-row class="business-details-section">
      <el-col :span="24">
        <BusinessDetailsCard
          :channel-data="channelStats"
          :scenarios="scenarioStats"
          :no-ticket-stats="noTicketStats"
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 5. 用户明细数据 -->
    <el-row class="user-stats">
      <el-col :span="24">
        <UserStatsCard 
          :users="userStats" 
          :retention-stats="retentionStats"
          :churned-users="churnedUsers"
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- ==================== 趋势数据分析区域 ==================== -->
    
    <!-- 6. 趋势数据分析 -->
    <el-row class="weekly-trends">
      <el-col :span="24">
        <WeeklyTrendCards 
          :query-trend-data="weeklyQueryTrend"
          :step-trend-data="weeklyStepTrend"
          :channel-trend-data="weeklyChannelTrend"
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 性能详情对话框 -->
    <PerformanceDetailDialog 
      v-model="detailDialogVisible"
      :biz-seq="selectedBizSeq"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { dashboardApi } from '@/services/api'
import ComprehensiveStatsCard from '@/components/ComprehensiveStatsCard.vue'
import ErrorDetailsCard from '@/components/ErrorDetailsCard.vue'
import PerformanceDetailsCard from '@/components/PerformanceDetailsCard.vue'
import StepPerformanceCard from '@/components/StepPerformanceCard.vue'
import BusinessDetailsCard from '@/components/BusinessDetailsCard.vue'
import UserStatsCard from '@/components/UserStatsCard.vue'
import PerformanceDetailDialog from '@/components/PerformanceDetailDialog.vue'
import WeeklyTrendCards from '@/components/WeeklyTrendCards.vue'

export default {
  name: 'Dashboard',
  components: {
    Refresh,
    ComprehensiveStatsCard,
    ErrorDetailsCard,
    PerformanceDetailsCard,
    StepPerformanceCard,
    BusinessDetailsCard,
    UserStatsCard,
    PerformanceDetailDialog,
    WeeklyTrendCards
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const selectedDate = ref('2025-10-21') // 默认有数据的日期
    
    // 统计数据
    const comprehensiveStats = ref({})
    const templatePerformance = ref([])
    const nonTemplatePerformance = ref([])
    const stepPerformance = ref([])
    const channelStats = ref({ member_stats: [], non_member_stats: [] })
    const scenarioStats = ref([])
    const noTicketStats = ref({})
    const userStats = ref([])
    const retentionStats = ref({})
    const churnedUsers = ref({})
    
    // 错误明细数据
    const agentErrorData = ref({})
    const dsErrorData = ref({})
    
    // 趋势数据
    const weeklyQueryTrend = ref([])
    const weeklyStepTrend = ref([])
    const weeklyChannelTrend = ref([])
    
    // 性能详情对话框
    const detailDialogVisible = ref(false)
    const selectedBizSeq = ref('')

    // 日期变化处理
    const onDateChange = (date) => {
      if (date) {
        loadAllData()
      }
    }

    // 查看性能详情
    const viewPerformanceDetail = (bizSeq) => {
      selectedBizSeq.value = bizSeq
      detailDialogVisible.value = true
    }

    // 加载所有数据
    const loadAllData = async () => {
      if (!selectedDate.value) {
        ElMessage.warning('请选择查询日期')
        return
      }

      loading.value = true
      
      try {
        const date = selectedDate.value

        // 并行加载所有数据
        const [
          comprehensiveStatsRes,
          templatePerformanceRes,
          nonTemplatePerformanceRes,
          stepPerformanceRes,
          channelStatsRes,
          scenarioStatsRes,
          noTicketStatsRes,
          userStatsRes,
          retentionStatsRes,
          churnedUsersRes,
          weeklyQueryTrendRes,
          weeklyStepTrendRes,
          weeklyChannelTrendRes,
          agentErrorDataRes,
          dsErrorDataRes
        ] = await Promise.all([
          dashboardApi.getTemplateQueryStats(date), // 现在返回综合统计数据
          dashboardApi.getTemplateQueryPerformance(date),
          dashboardApi.getNonTemplateQueryPerformance(date),
          dashboardApi.getStepPerformance(date),
          dashboardApi.getChannelStats(date),
          dashboardApi.getScenarioStats(date),
          dashboardApi.getNoTicketStats(date),
          dashboardApi.getUserStats(date),
          dashboardApi.getUserRetentionStats(date),
          dashboardApi.getChurnedUsers(date),
          // 趋势图使用今天的日期，而不是查询日期
          dashboardApi.getWeeklyQueryTrend({ endDate: new Date().toISOString().split('T')[0] }),
          dashboardApi.getWeeklyStepTrend({ endDate: new Date().toISOString().split('T')[0] }),
          dashboardApi.getWeeklyChannelTrend({ endDate: new Date().toISOString().split('T')[0] }),
          // 加载错误明细数据
          dashboardApi.getAgentErrorDetails(date),
          dashboardApi.getDsErrorDetails(date)
        ])

        // 更新数据
        comprehensiveStats.value = comprehensiveStatsRes || {}
        templatePerformance.value = templatePerformanceRes || []
        nonTemplatePerformance.value = nonTemplatePerformanceRes || []
        stepPerformance.value = stepPerformanceRes || []
        channelStats.value = channelStatsRes || { member_stats: [], non_member_stats: [] }
        scenarioStats.value = scenarioStatsRes || []
        noTicketStats.value = noTicketStatsRes || {}
        userStats.value = userStatsRes || []
        retentionStats.value = retentionStatsRes || {}
        churnedUsers.value = churnedUsersRes || {}
        weeklyQueryTrend.value = weeklyQueryTrendRes || []
        weeklyStepTrend.value = weeklyStepTrendRes || []
        weeklyChannelTrend.value = weeklyChannelTrendRes || []
        agentErrorData.value = agentErrorDataRes || {}
        dsErrorData.value = dsErrorDataRes || {}

        ElMessage.success('数据加载成功')
      } catch (error) {
        console.error('加载数据失败:', error)
        ElMessage.error('数据加载失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }

    // 组件挂载时加载数据
    onMounted(() => {
      loadAllData()
    })

    return {
      loading,
      selectedDate,
      comprehensiveStats,
      agentErrorData,
      dsErrorData,
      templatePerformance,
      nonTemplatePerformance,
      stepPerformance,
      channelStats,
      scenarioStats,
      noTicketStats,
      userStats,
      retentionStats,
      churnedUsers,
      weeklyQueryTrend,
      weeklyStepTrend,
      weeklyChannelTrend,
      detailDialogVisible,
      selectedBizSeq,
      onDateChange,
      loadAllData,
      viewPerformanceDetail
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.date-selector {
  margin-bottom: 20px;
}

.label {
  font-weight: 500;
  color: #333;
}

.overview-stats,
.comprehensive-stats,
.error-details-section,
.performance-details-section,
.channel-scenario-stats {
  margin-bottom: 20px;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-performance,
.user-stats,
.weekly-trends {
  margin-bottom: 20px;
}

:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  border: none;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #f0f0f0;
  padding: 18px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>

