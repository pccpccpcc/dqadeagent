<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Grid /></el-icon>
          业务明细数据
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="business-content">
      <!-- 渠道和场景统计 -->
      <el-row :gutter="20" class="main-stats">
        <el-col :span="12">
          <ChannelStatsCard 
            title="渠道明细数据" 
            :channel-data="channelData" 
            :loading="loading"
            :show-header="false"
          />
        </el-col>
        <el-col :span="12">
          <ScenarioStatsCard 
            title="场景明细数据" 
            :scenarios="scenarios" 
            :loading="loading"
            :show-header="false"
          />
        </el-col>
      </el-row>

      <!-- 免提单统计 -->
      <el-row class="no-ticket-stats">
        <el-col :span="24">
          <NoTicketStatsCard 
            title="免提单明细数据" 
            :stats="noTicketStats" 
            :loading="loading"
            :show-header="false"
          />
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script>
import { Grid } from '@element-plus/icons-vue'
import ChannelStatsCard from './ChannelStatsCard.vue'
import ScenarioStatsCard from './ScenarioStatsCard.vue'
import NoTicketStatsCard from './NoTicketStatsCard.vue'

export default {
  name: 'BusinessDetailsCard',
  components: {
    Grid,
    ChannelStatsCard,
    ScenarioStatsCard,
    NoTicketStatsCard
  },
  props: {
    channelData: {
      type: Object,
      default: () => ({})
    },
    scenarios: {
      type: Array,
      default: () => []
    },
    noTicketStats: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 16px;
}

.business-content {
  min-height: 200px;
}

.main-stats {
  margin-bottom: 20px;
}

.no-ticket-stats {
  margin-top: 0;
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

/* 子卡片去掉外层card样式 */
:deep(.main-stats .el-card),
:deep(.no-ticket-stats .el-card) {
  box-shadow: none;
  border: 1px solid #ebeef5;
  background-color: #fafafa;
}

:deep(.main-stats .el-card__body),
:deep(.no-ticket-stats .el-card__body) {
  padding: 15px;
}
</style>

