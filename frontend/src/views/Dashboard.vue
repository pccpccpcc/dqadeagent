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

    <!-- 概览统计 -->
    <el-row :gutter="20" class="overview-stats">
      <el-col :span="12">
        <QueryStatsCard 
          title="模板查询统计" 
          :stats="templateStats" 
          :loading="loading"
          type="template"
        />
      </el-col>
      <el-col :span="12">
        <QueryStatsCard 
          title="非模板查询统计" 
          :stats="nonTemplateStats" 
          :loading="loading"
          type="non-template"
        />
      </el-col>
    </el-row>

    <!-- 错误分析 -->
    <el-row :gutter="20" class="error-analysis">
      <el-col :span="12">
        <ErrorAnalysisCard 
          title="模板查询错误分析" 
          :errors="templateErrors" 
          :loading="loading"
        />
      </el-col>
      <el-col :span="12">
        <ErrorAnalysisCard 
          title="非模板查询错误分析" 
          :errors="nonTemplateErrors" 
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 性能分析 -->
    <el-row :gutter="20" class="performance-analysis">
      <el-col :span="12">
        <PerformanceCard 
          title="模板查询性能分析" 
          :performance="templatePerformance" 
          :loading="loading"
          @view-detail="viewPerformanceDetail"
        />
      </el-col>
      <el-col :span="12">
        <PerformanceCard 
          title="非模板查询性能分析" 
          :performance="nonTemplatePerformance" 
          :loading="loading"
          @view-detail="viewPerformanceDetail"
        />
      </el-col>
    </el-row>

    <!-- 步骤性能分析 -->
    <el-row class="step-performance">
      <el-col :span="24">
        <StepPerformanceCard 
          title="各环节耗时统计" 
          :steps="stepPerformance" 
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 其他统计 -->
    <el-row :gutter="20" class="other-stats">
      <el-col :span="8">
        <ChannelStatsCard 
          title="渠道查询统计" 
          :channels="channelStats" 
          :loading="loading"
        />
      </el-col>
      <el-col :span="8">
        <ScenarioStatsCard 
          title="场景查询统计" 
          :scenarios="scenarioStats" 
          :loading="loading"
        />
      </el-col>
      <el-col :span="8">
        <NoTicketStatsCard 
          title="免提单统计" 
          :stats="noTicketStats" 
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 用户统计 -->
    <el-row class="user-stats">
      <el-col :span="24">
        <UserStatsCard 
          title="用户使用统计" 
          :users="userStats" 
          :loading="loading"
        />
      </el-col>
    </el-row>

    <!-- 趋势图表 -->
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
import QueryStatsCard from '@/components/QueryStatsCard.vue'
import ErrorAnalysisCard from '@/components/ErrorAnalysisCard.vue'
import PerformanceCard from '@/components/PerformanceCard.vue'
import StepPerformanceCard from '@/components/StepPerformanceCard.vue'
import ChannelStatsCard from '@/components/ChannelStatsCard.vue'
import ScenarioStatsCard from '@/components/ScenarioStatsCard.vue'
import NoTicketStatsCard from '@/components/NoTicketStatsCard.vue'
import UserStatsCard from '@/components/UserStatsCard.vue'
import PerformanceDetailDialog from '@/components/PerformanceDetailDialog.vue'
import WeeklyTrendCards from '@/components/WeeklyTrendCards.vue'

export default {
  name: 'Dashboard',
  components: {
    Refresh,
    QueryStatsCard,
    ErrorAnalysisCard,
    PerformanceCard,
    StepPerformanceCard,
    ChannelStatsCard,
    ScenarioStatsCard,
    NoTicketStatsCard,
    UserStatsCard,
    PerformanceDetailDialog,
    WeeklyTrendCards
  },
  setup() {
    // 响应式数据
    const loading = ref(false)
    const selectedDate = ref('2025-10-21') // 默认有数据的日期
    
    // 统计数据
    const templateStats = ref({})
    const nonTemplateStats = ref({})
    const templateErrors = ref([])
    const nonTemplateErrors = ref([])
    const templatePerformance = ref([])
    const nonTemplatePerformance = ref([])
    const stepPerformance = ref([])
    const channelStats = ref([])
    const scenarioStats = ref([])
    const noTicketStats = ref({})
    const userStats = ref([])
    
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
          templateStatsRes,
          nonTemplateStatsRes,
          templateErrorsRes,
          nonTemplateErrorsRes,
          templatePerformanceRes,
          nonTemplatePerformanceRes,
          stepPerformanceRes,
          channelStatsRes,
          scenarioStatsRes,
          noTicketStatsRes,
          userStatsRes,
          weeklyQueryTrendRes,
          weeklyStepTrendRes,
          weeklyChannelTrendRes
        ] = await Promise.all([
          dashboardApi.getTemplateQueryStats(date),
          dashboardApi.getNonTemplateQueryStats(date),
          dashboardApi.getTemplateQueryErrors(date),
          dashboardApi.getNonTemplateQueryErrors(date),
          dashboardApi.getTemplateQueryPerformance(date),
          dashboardApi.getNonTemplateQueryPerformance(date),
          dashboardApi.getStepPerformance(date),
          dashboardApi.getChannelStats(date),
          dashboardApi.getScenarioStats(date),
          dashboardApi.getNoTicketStats(date),
          dashboardApi.getUserStats(date),
          // 趋势图使用今天的日期，而不是查询日期
          dashboardApi.getWeeklyQueryTrend({ endDate: new Date().toISOString().split('T')[0] }),
          dashboardApi.getWeeklyStepTrend({ endDate: new Date().toISOString().split('T')[0] }),
          dashboardApi.getWeeklyChannelTrend({ endDate: new Date().toISOString().split('T')[0] })
        ])

        // 更新数据
        templateStats.value = templateStatsRes || {}
        nonTemplateStats.value = nonTemplateStatsRes || {}
        templateErrors.value = templateErrorsRes || []
        nonTemplateErrors.value = nonTemplateErrorsRes || []
        templatePerformance.value = templatePerformanceRes || []
        nonTemplatePerformance.value = nonTemplatePerformanceRes || []
        stepPerformance.value = stepPerformanceRes || []
        channelStats.value = channelStatsRes || []
        scenarioStats.value = scenarioStatsRes || []
        noTicketStats.value = noTicketStatsRes || {}
        userStats.value = userStatsRes || []
        weeklyQueryTrend.value = weeklyQueryTrendRes || []
        weeklyStepTrend.value = weeklyStepTrendRes || []
        weeklyChannelTrend.value = weeklyChannelTrendRes || []

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
      templateStats,
      nonTemplateStats,
      templateErrors,
      nonTemplateErrors,
      templatePerformance,
      nonTemplatePerformance,
      stepPerformance,
      channelStats,
      scenarioStats,
      noTicketStats,
      userStats,
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
.error-analysis,
.performance-analysis,
.other-stats {
  margin-bottom: 20px;
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

