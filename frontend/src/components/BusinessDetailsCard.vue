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
      <el-row :gutter="20">
        <!-- 左侧：渠道 + 免提单 -->
        <el-col :span="12">
          <div class="left-column">
            <!-- 渠道明细数据 -->
            <div class="channel-section">
              <ChannelStatsCard 
                title="渠道明细数据" 
                :channel-data="channelData" 
                :loading="loading"
              />
            </div>
            
            <!-- 免提单明细数据 -->
            <div class="no-ticket-section">
              <NoTicketStatsCard 
                title="免提单明细数据" 
                :stats="noTicketStats" 
                :loading="loading"
              />
            </div>
          </div>
        </el-col>

        <!-- 右侧：场景（查询类型） -->
        <el-col :span="12">
          <ScenarioStatsCard 
            title="场景明细数据" 
            :scenarios="scenarios" 
            :loading="loading"
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

.left-column {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.channel-section {
  flex: 1;
  margin-bottom: 20px;
}

.no-ticket-section {
  flex: 1;
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

/* 子卡片样式优化 */
:deep(.channel-section .el-card),
:deep(.no-ticket-section .el-card) {
  box-shadow: none;
  border: 1px solid #ebeef5;
  background-color: #fafafa;
  height: 100%;
}

:deep(.channel-section .el-card__body),
:deep(.no-ticket-section .el-card__body) {
  padding: 15px;
}

/* 右侧场景卡片样式 */
:deep(.el-col:last-child > .el-card) {
  box-shadow: none;
  border: 1px solid #ebeef5;
  background-color: #fafafa;
  height: 100%;
}

:deep(.el-col:last-child > .el-card__body) {
  padding: 15px;
}
</style>

