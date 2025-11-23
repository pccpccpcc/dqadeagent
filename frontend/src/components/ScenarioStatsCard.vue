<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Grid /></el-icon>
          {{ title }}
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="scenario-content">
      <div v-if="!loading && scenarios.length === 0" class="no-data">
        <el-empty description="暂无场景数据" />
      </div>
      
      <div v-else-if="!loading" class="scenario-stats">
        <!-- 场景统计表格 -->
        <el-table
          :data="scenarios"
          style="width: 100%"
          size="small"
          stripe
          max-height="300"
        >
          <el-table-column prop="scenario_name" label="查询场景" width="120">
            <template #default="{ row }">
              <div class="scenario-name">
                <el-icon>
                  <component :is="getScenarioIcon(row.scenario)" />
                </el-icon>
                <span>{{ row.scenario_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="count" label="查询次数" align="center" width="100">
            <template #default="{ row }">
              <span class="count-number">{{ row.count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="占比" align="center" width="80">
            <template #default="{ row }">
              <span class="percentage">{{ getPercentage(row.count) }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="scenario" label="英文标识" min-width="120">
            <template #default="{ row }">
              <el-tag type="info" size="small">{{ row.scenario }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 场景分布图表 -->
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
import { 
  Grid, 
  Promotion, 
  QuestionFilled, 
  DataAnalysis, 
  Document, 
  List, 
  Clock, 
  Setting, 
  Tools, 
  Tickets, 
  MoreFilled 
} from '@element-plus/icons-vue'

export default {
  name: 'ScenarioStatsCard',
  components: {
    Grid,
    Promotion,
    QuestionFilled,
    DataAnalysis,
    Document,
    List,
    Clock,
    Setting,
    Tools,
    Tickets,
    MoreFilled
  },
  props: {
    title: {
      type: String,
      required: true
    },
    scenarios: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    // 获取场景图标
    const getScenarioIcon = (scenario) => {
      const iconMap = {
        'execution_plan': 'Promotion',
        'yn_query': 'QuestionFilled',
        'count_query': 'DataAnalysis',
        'table_structure': 'Document',
        'enum_query': 'List',
        'time_query': 'Clock',
        'config_query': 'Setting',
        'field_length': 'Tools',
        'ticket_related': 'Tickets',
        'other': 'MoreFilled'
      }
      return iconMap[scenario] || 'MoreFilled'
    }

    // 计算总数
    const totalCount = computed(() => {
      return props.scenarios.reduce((total, scenario) => total + scenario.count, 0)
    })

    // 计算百分比
    const getPercentage = (count) => {
      if (totalCount.value === 0) return 0
      return ((count / totalCount.value) * 100).toFixed(1)
    }

    // 图表数据
    const chartData = computed(() => {
      return props.scenarios
        .filter(scenario => scenario.count > 0)
        .map(scenario => ({
          name: scenario.scenario_name,
          value: scenario.count
        }))
    })

    // 图表配置
    const chartOption = computed(() => {
      return {
        title: {
          text: '查询场景分布',
          left: 'center',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            const percentage = ((params.value / totalCount.value) * 100).toFixed(1)
            return `${params.name}<br/>数量: ${params.value}<br/>占比: ${percentage}%`
          }
        },
        series: [
          {
            type: 'pie',
            radius: ['30%', '70%'],
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
              formatter: function(params) {
                const percentage = ((params.value / totalCount.value) * 100).toFixed(1)
                return `${params.name}\n${percentage}%`
              }
            },
            labelLine: {
              show: true
            }
          }
        ]
      }
    })

    return {
      getScenarioIcon,
      getPercentage,
      totalCount,
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

.scenario-content {
  min-height: 500px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 500px;
}

.scenario-name {
  display: flex;
  align-items: center;
  gap: 5px;
}

.count-number {
  font-weight: bold;
  color: #409eff;
}

.percentage {
  font-weight: bold;
  color: #67c23a;
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
  margin-bottom: 20px;
}

:deep(.el-table .el-table__body tr:hover > td) {
  background-color: #f5f7fa;
}
</style>
