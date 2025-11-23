<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Document /></el-icon>
          {{ title }}
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="stats-content">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item total">
            <div class="stat-number">{{ stats.total_count || 0 }}</div>
            <div class="stat-label">总查询数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item success">
            <div class="stat-number">{{ stats.success_count || 0 }}</div>
            <div class="stat-label">成功数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item failure">
            <div class="stat-number">{{ stats.failure_count || 0 }}</div>
            <div class="stat-label">失败数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item rate">
            <div class="stat-number">{{ stats.success_rate || 0 }}%</div>
            <div class="stat-label">成功率</div>
          </div>
        </el-col>
      </el-row>
      
      <!-- 成功率图表 -->
      <div class="chart-container" v-if="!loading && stats.total_count">
        <v-chart 
          class="chart" 
          :option="chartOption" 
          autoresize
        />
      </div>
    </div>
  </el-card>
</template>

<script>
import { computed } from 'vue'
import { Document } from '@element-plus/icons-vue'

export default {
  name: 'QueryStatsCard',
  components: {
    Document
  },
  props: {
    title: {
      type: String,
      required: true
    },
    stats: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    },
    type: {
      type: String,
      default: 'template'
    }
  },
  setup(props) {
    const chartOption = computed(() => {
      const successRate = props.stats.success_rate || 0
      const failureRate = 100 - successRate

      return {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          bottom: '0',
          left: 'center'
        },
        series: [
          {
            name: '查询结果',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '45%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              {
                value: props.stats.success_count || 0,
                name: '成功',
                itemStyle: { color: '#67C23A' }
              },
              {
                value: props.stats.failure_count || 0,
                name: '失败',
                itemStyle: { color: '#F56C6C' }
              }
            ]
          }
        ]
      }
    })

    return {
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

.stats-content {
  min-height: 200px;
}

.stat-item {
  text-align: center;
  padding: 20px 0;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-item.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-item.success {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  color: white;
}

.stat-item.failure {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #333;
}

.stat-item.rate {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #333;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.chart-container {
  margin-top: 20px;
  height: 250px;
}

.chart {
  height: 100%;
  width: 100%;
}
</style>

