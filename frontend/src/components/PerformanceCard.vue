<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Timer /></el-icon>
          {{ title }}
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="performance-content">
      <div v-if="!loading && performance.length === 0" class="no-data">
        <el-empty description="暂无性能数据" />
      </div>
      
      <div v-else-if="!loading" class="performance-stats">
        <!-- 性能表格 -->
        <el-table
          :data="performance"
          style="width: 100%"
          size="small"
          stripe
        >
          <el-table-column prop="category" label="查询类型" width="150">
            <template #default="{ row }">
              <el-tag :type="getTagType(row.db_type)" size="small">
                {{ row.category }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="avg_cost" label="平均耗时(ms)" width="120" align="center">
            <template #default="{ row }">
              <span class="avg-cost">{{ formatTime(row.avg_cost) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="max_cost" label="最大耗时(ms)" width="120" align="center">
            <template #default="{ row }">
              <span class="max-cost">{{ formatTime(row.max_cost) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button 
                v-if="row.max_cost_biz_seq"
                type="text" 
                size="small"
                @click="viewDetail(row.max_cost_biz_seq)"
              >
                <el-icon><View /></el-icon>
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 性能图表 -->
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
import { Timer, View } from '@element-plus/icons-vue'

export default {
  name: 'PerformanceCard',
  components: {
    Timer,
    View
  },
  props: {
    title: {
      type: String,
      required: true
    },
    performance: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['view-detail'],
  setup(props, { emit }) {
    // 格式化时间显示
    const formatTime = (time) => {
      if (!time) return '0'
      if (time < 1000) return `${Math.round(time)}`
      return `${(time / 1000).toFixed(2)}s`
    }

    // 获取标签类型
    const getTagType = (dbType) => {
      const typeMap = {
        'TDSQL': 'primary',
        'TIDB': 'success',
        'HIVE': 'warning'
      }
      return typeMap[dbType] || 'info'
    }

    // 查看详情
    const viewDetail = (bizSeq) => {
      emit('view-detail', bizSeq)
    }

    // 图表数据
    const chartData = computed(() => {
      return {
        categories: props.performance.map(item => item.category),
        avgData: props.performance.map(item => item.avg_cost),
        maxData: props.performance.map(item => item.max_cost)
      }
    })

    // 图表配置
    const chartOption = computed(() => {
      return {
        title: {
          text: '性能对比',
          left: 'center',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function(params) {
            let result = params[0].axisValue + '<br/>'
            params.forEach(param => {
              const value = param.value < 1000 ? 
                `${Math.round(param.value)}ms` : 
                `${(param.value / 1000).toFixed(2)}s`
              result += `${param.marker}${param.seriesName}: ${value}<br/>`
            })
            return result
          }
        },
        legend: {
          bottom: '0',
          left: 'center'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: chartData.value.categories,
          axisLabel: {
            interval: 0,
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: '耗时(ms)',
          axisLabel: {
            formatter: function(value) {
              if (value < 1000) return value + 'ms'
              return (value / 1000).toFixed(1) + 's'
            }
          }
        },
        series: [
          {
            name: '平均耗时',
            type: 'bar',
            data: chartData.value.avgData,
            itemStyle: {
              color: '#409EFF'
            }
          },
          {
            name: '最大耗时',
            type: 'bar',
            data: chartData.value.maxData,
            itemStyle: {
              color: '#F56C6C'
            }
          }
        ]
      }
    })

    return {
      formatTime,
      getTagType,
      viewDetail,
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

.performance-content {
  min-height: 400px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
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

:deep(.el-button--text) {
  padding: 0;
}
</style>

