<template>
  <el-card>
    <template #header>
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
        
        <!-- 步骤性能图表 -->
        <div class="chart-container">
          <v-chart 
            class="chart" 
            :option="chartOption" 
            autoresize
          />
        </div>
      </div>
    </div>
  </el-card>
</template>

<script>
import { computed } from 'vue'
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
    }
  },
  setup(props) {
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

    // 图表配置
    const chartOption = computed(() => {
      const sortedSteps = [...props.steps].sort((a, b) => b.avg_cost - a.avg_cost)
      
      return {
        title: {
          text: '各环节平均耗时对比',
          left: 'center',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const param = params[0]
            const value = param.value < 1000 ? 
              `${Math.round(param.value)}ms` : 
              `${(param.value / 1000).toFixed(2)}s`
            return `${param.axisValue}<br/>平均耗时: ${value}`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '耗时(ms)',
          axisLabel: {
            formatter: function(value) {
              if (value < 1000) return value + 'ms'
              return (value / 1000).toFixed(1) + 's'
            }
          }
        },
        yAxis: {
          type: 'category',
          data: sortedSteps.map(step => step.step_name_cn),
          axisLabel: {
            fontSize: 12
          }
        },
        series: [
          {
            type: 'bar',
            data: sortedSteps.map(step => ({
              value: step.avg_cost,
              itemStyle: {
                color: function(params) {
                  const value = params.value
                  if (value < 500) return '#67C23A'
                  if (value < 2000) return '#E6A23C'
                  if (value < 5000) return '#F56C6C'
                  return '#909399'
                }
              }
            })),
            barWidth: '60%',
            label: {
              show: true,
              position: 'right',
              formatter: function(params) {
                const value = params.value
                return value < 1000 ? 
                  `${Math.round(value)}ms` : 
                  `${(value / 1000).toFixed(2)}s`
              }
            }
          }
        ]
      }
    })

    return {
      formatTime,
      getPerformanceLevel,
      chartOption
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
  min-height: 500px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 500px;
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

.max-cost {
  color: #f56c6c;
  font-weight: bold;
}

.chart-container {
  margin-top: 20px;
  height: 400px;
}

.chart {
  height: 100%;
  width: 100%;
}

:deep(.el-table) {
  border-radius: 6px;
  margin-bottom: 20px;
}

:deep(.el-table .el-table__body tr:hover > td) {
  background-color: #f5f7fa;
}
</style>

