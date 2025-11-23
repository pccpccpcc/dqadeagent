<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Unlock /></el-icon>
          {{ title }}
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="no-ticket-content">
      <div v-if="!loading" class="no-ticket-stats">
        <!-- 免提单统计 -->
        <div class="stats-display">
          <div class="main-stat">
            <div class="stat-icon">
              <el-icon><Ticket /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.count || 0 }}</div>
              <div class="stat-label">免提单查询次数</div>
            </div>
          </div>
          
          <div class="date-info">
            <el-tag type="info" size="small">
              查询日期: {{ stats.query_date || '未知' }}
            </el-tag>
          </div>
        </div>
        
        <!-- 免提单说明 -->
        <div class="description">
          <el-alert
            title="免提单说明"
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>免提单查询指不需要提交生产权限访问单就能直接查询的操作，通常用于:</p>
              <ul>
                <li>预配置的系统查询</li>
                <li>无需权限的公共数据查询</li>
                <li>系统内置的查询模板</li>
              </ul>
            </template>
          </el-alert>
        </div>
        
        <!-- 趋势图表 -->
        <div class="chart-container" v-if="stats.count > 0">
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
import { Unlock, Ticket } from '@element-plus/icons-vue'

export default {
  name: 'NoTicketStatsCard',
  components: {
    Unlock,
    Ticket
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
    }
  },
  setup(props) {
    // 图表配置
    const chartOption = computed(() => {
      const count = props.stats.count || 0
      
      return {
        title: {
          text: '免提单查询占比',
          left: 'center',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
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
            name: '查询类型',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '45%'],
            data: [
              {
                value: count,
                name: '免提单查询',
                itemStyle: { color: '#67C23A' }
              },
              {
                value: Math.max(100 - count, 0),
                name: '其他查询',
                itemStyle: { color: '#E6E6E6' }
              }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              formatter: function(params) {
                if (params.name === '免提单查询') {
                  return `${params.name}\n${params.value}次`
                }
                return params.name
              }
            }
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

.no-ticket-content {
  min-height: 400px;
}

.stats-display {
  margin-bottom: 20px;
}

.main-stat {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 15px;
}

.stat-icon {
  font-size: 48px;
  opacity: 0.9;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 16px;
  opacity: 0.9;
}

.date-info {
  text-align: center;
}

.description {
  margin-bottom: 20px;
}

.description p {
  margin: 0 0 10px 0;
  color: #666;
}

.description ul {
  margin: 10px 0 0 20px;
  color: #666;
}

.description li {
  margin-bottom: 5px;
}

.chart-container {
  height: 250px;
}

.chart {
  height: 100%;
  width: 100%;
}

:deep(.el-alert) {
  border-radius: 8px;
}

:deep(.el-alert__content) {
  padding-right: 0;
}
</style>

