<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Warning /></el-icon>
          {{ title }}
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="error-content">
      <div v-if="!loading && errors.length === 0" class="no-data">
        <el-empty description="暂无错误数据" />
      </div>
      
      <div v-else-if="!loading" class="error-stats">
        <!-- 错误总览 -->
        <div class="error-summary" v-if="totalErrors > 0">
          <el-alert
            :title="`总错误数：${totalErrors}`"
            type="warning"
            show-icon
            :closable="false"
          />
        </div>
        
        <!-- 子系统错误统计 -->
        <div class="subsystem-stats">
          <div v-for="subsystem in subsystems" :key="subsystem.name" class="subsystem-section">
            <h4 class="subsystem-title">
              <el-icon><DataAnalysis /></el-icon>
              {{ subsystem.name }}
              <span class="error-count">({{ subsystem.total }}个错误)</span>
            </h4>
            
            <el-table
              :data="subsystem.errors"
              style="width: 100%"
              size="small"
              :show-header="false"
            >
              <el-table-column prop="error_code" label="错误码" width="100">
                <template #default="{ row }">
                  <el-tag type="danger" size="small">{{ row.error_code }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="error_message" label="错误信息" min-width="200" />
              <el-table-column prop="count" label="数量" width="80" align="center">
                <template #default="{ row }">
                  <span class="error-count-number">{{ row.count }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="percentage" label="占比" width="80" align="center">
                <template #default="{ row }">
                  <span class="percentage">{{ row.percentage }}%</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        
        <!-- 错误分布图表 -->
        <div class="chart-container" v-if="chartData.length > 0">
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
import { Warning, DataAnalysis } from '@element-plus/icons-vue'

export default {
  name: 'ErrorAnalysisCard',
  components: {
    Warning,
    DataAnalysis
  },
  props: {
    title: {
      type: String,
      required: true
    },
    errors: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    // 计算总错误数
    const totalErrors = computed(() => {
      return props.errors.reduce((total, error) => total + error.count, 0)
    })

    // 按子系统分组错误
    const subsystems = computed(() => {
      const subsystemMap = {}
      
      props.errors.forEach(error => {
        if (!subsystemMap[error.subsystem]) {
          subsystemMap[error.subsystem] = {
            name: error.subsystem_name,
            errors: [],
            total: 0
          }
        }
        subsystemMap[error.subsystem].errors.push(error)
        subsystemMap[error.subsystem].total += error.count
      })
      
      return Object.values(subsystemMap)
    })

    // 图表数据
    const chartData = computed(() => {
      return props.errors.map(error => ({
        name: `${error.error_message}`,
        value: error.count,
        label: error.error_message
      }))
    })

    // 图表配置
    const chartOption = computed(() => {
      return {
        title: {
          text: '错误分布',
          left: 'center',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return `${params.name}<br/>数量: ${params.value}<br/>占比: ${params.percent}%`
          }
        },
        series: [
          {
            type: 'pie',
            radius: ['30%', '60%'],
            center: ['50%', '55%'],
            data: chartData.value,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              formatter: '{b}: {c}'
            }
          }
        ]
      }
    })

    return {
      totalErrors,
      subsystems,
      chartData,
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

.error-content {
  min-height: 300px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.error-summary {
  margin-bottom: 20px;
}

.subsystem-section {
  margin-bottom: 20px;
}

.subsystem-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.error-count {
  color: #999;
  font-weight: normal;
  font-size: 12px;
}

.error-count-number {
  font-weight: bold;
  color: #f56c6c;
}

.percentage {
  font-weight: bold;
  color: #409eff;
}

.chart-container {
  margin-top: 20px;
  height: 300px;
}

.chart {
  height: 100%;
  width: 100%;
}

:deep(.el-table) {
  border-radius: 6px;
}

:deep(.el-table .el-table__body tr:hover > td) {
  background-color: #f5f7fa;
}
</style>

