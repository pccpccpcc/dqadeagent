<template>
  <el-card class="performance-details-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Timer /></el-icon>
          耗时明细数据
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="performance-details-content">
      <!-- 查询耗时明细 -->
      <el-row :gutter="20" class="query-performance">
        <!-- 模板查询耗时明细 -->
        <el-col :span="12">
          <PerformanceDetailSubCard
            title="模板查询耗时明细数据"
            :performance="templatePerformance"
            :loading="loading"
            @view-detail="$emit('view-detail', $event)"
          />
        </el-col>
        
        <!-- 非模板查询耗时明细 -->
        <el-col :span="12">
          <PerformanceDetailSubCard
            title="非模板查询耗时明细数据"
            :performance="nonTemplatePerformance"
            :loading="loading"
            @view-detail="$emit('view-detail', $event)"
          />
        </el-col>
      </el-row>

      <!-- 环节耗时明细 -->
      <el-row class="step-performance">
        <el-col :span="24">
          <StepPerformanceCard 
            title="环节耗时明细数据" 
            :steps="stepPerformance" 
            :loading="loading"
          />
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script>
import { Timer } from '@element-plus/icons-vue'
import PerformanceDetailSubCard from './PerformanceDetailSubCard.vue'
import StepPerformanceCard from './StepPerformanceCard.vue'

export default {
  name: 'PerformanceDetailsCard',
  components: {
    Timer,
    PerformanceDetailSubCard,
    StepPerformanceCard
  },
  props: {
    templatePerformance: {
      type: Array,
      default: () => []
    },
    nonTemplatePerformance: {
      type: Array,
      default: () => []
    },
    stepPerformance: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['view-detail']
}
</script>

<style scoped>
.performance-details-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 18px;
}

.performance-details-content {
  min-height: 200px;
}

.query-performance {
  margin-bottom: 20px;
}

.step-performance {
  margin-top: 0;
}

/* 子卡片样式优化 */
:deep(.step-performance .el-card) {
  box-shadow: none;
  border: 1px solid #ebeef5;
  background-color: #fafafa;
}

:deep(.step-performance .el-card__body) {
  padding: 15px;
}
</style>

