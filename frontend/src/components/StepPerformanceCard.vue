<template>
  <el-card>
    <template #header v-if="showHeader">
      <div class="card-header">
        <span class="card-title">
          <el-icon><Histogram /></el-icon>
          {{ title }}
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="step-content">
      <div v-if="!loading && steps.length === 0" class="no-data">
        <el-empty description="暂无步骤数据" />
      </div>
      
      <div v-else-if="!loading" class="step-stats">
        <!-- 步骤表格 -->
        <el-table
          :data="steps"
          style="width: 100%"
          size="small"
          stripe
        >
          <el-table-column prop="step_name_cn" label="环节名称" width="150">
            <template #default="{ row }">
              <div class="step-name">
                <el-icon><Operation /></el-icon>
                <span>{{ row.step_name_cn }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="avg_cost" label="平均耗时" width="120" align="center">
            <template #default="{ row }">
              <span class="avg-cost">{{ formatTime(row.avg_cost) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="p90_cost" label="P90耗时" width="120" align="center">
            <template #default="{ row }">
              <span class="p90-cost">{{ formatTime(row.p90_cost) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="max_cost" label="最大耗时" width="120" align="center">
            <template #default="{ row }">
              <span class="max-cost">{{ formatTime(row.max_cost) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="性能评级" width="100" align="center">
            <template #default="{ row }">
              <el-tag 
                :type="getPerformanceLevel(row.avg_cost).type" 
                size="small"
              >
                {{ getPerformanceLevel(row.avg_cost).label }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="step_name" label="英文标识" min-width="150">
            <template #default="{ row }">
              <el-tag type="info" size="small">{{ row.step_name }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </el-card>
</template>

<script>
import { Histogram, Operation } from '@element-plus/icons-vue'

export default {
  name: 'StepPerformanceCard',
  components: {
    Histogram,
    Operation
  },
  props: {
    title: {
      type: String,
      required: true
    },
    steps: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    showHeader: {
      type: Boolean,
      default: true
    }
  },
  setup() {
    // 格式化时间显示
    const formatTime = (time) => {
      if (!time) return '0ms'
      if (time < 1000) return `${Math.round(time)}ms`
      return `${(time / 1000).toFixed(2)}s`
    }

    // 获取性能等级
    const getPerformanceLevel = (avgCost) => {
      if (avgCost < 500) {
        return { type: 'success', label: '优秀' }
      } else if (avgCost < 2000) {
        return { type: 'warning', label: '良好' }
      } else if (avgCost < 5000) {
        return { type: 'danger', label: '一般' }
      } else {
        return { type: 'danger', label: '较慢' }
      }
    }

    return {
      formatTime,
      getPerformanceLevel
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 16px;
}

.step-content {
  min-height: 200px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.step-name {
  display: flex;
  align-items: center;
  gap: 5px;
}

.avg-cost {
  color: #409eff;
  font-weight: bold;
}

.p90-cost {
  color: #e6a23c;
  font-weight: bold;
}

.max-cost {
  color: #f56c6c;
  font-weight: bold;
}

:deep(.el-table) {
  border-radius: 6px;
}

:deep(.el-table .el-table__body tr:hover > td) {
  background-color: #f5f7fa;
}
</style>

