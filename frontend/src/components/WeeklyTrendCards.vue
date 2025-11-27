<template>
  <div class="weekly-trends">
    <!-- 趋势数据分析控制面板 -->
    <el-row :gutter="20" class="trend-controls">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header-level-1">
              <span class="card-title-level-1">
                <el-icon><Calendar /></el-icon>
                趋势数据分析
              </span>
            </div>
          </template>
          
          <div class="controls-content">
            <el-row :gutter="20" align="middle">
              <el-col :span="8">
                <div class="control-group">
                  <label>快捷选择：</label>
                  <el-radio-group v-model="dateRangeType" @change="onDateRangeTypeChange">
                    <el-radio-button label="week">最近一周</el-radio-button>
                    <el-radio-button label="month">最近一个月</el-radio-button>
                    <el-radio-button label="custom">自定义</el-radio-button>
                  </el-radio-group>
                </div>
              </el-col>
              
              <el-col :span="10" v-show="dateRangeType === 'custom'">
                <div class="control-group">
                  <label>自定义日期范围：</label>
                  <el-date-picker
                    v-model="customDateRange"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    @change="onCustomDateChange"
                  />
                </div>
              </el-col>
              
              <el-col :span="6">
                <el-button type="primary" @click="loadTrendData" :loading="loading">
                  <el-icon><Refresh /></el-icon>
                  更新趋势
                </el-button>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 查询总数趋势 -->
    <el-row :gutter="20" class="trend-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header-level-2">
              <span class="card-title-level-2">
                <el-icon><TrendCharts /></el-icon>
                {{ getTrendTitle('查询总数趋势') }}
              </span>
            </div>
          </template>
          
          <div v-loading="loading" class="trend-content">
            <div v-if="!loading && queryTrendData.length === 0" class="no-data">
              <el-empty description="暂无趋势数据" />
            </div>
            
            <div v-else-if="!loading" class="chart-container">
              <v-chart 
                class="chart" 
                :option="queryTrendOption" 
                autoresize
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 环节耗时趋势 -->
    <el-row :gutter="20" class="trend-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header-level-2">
              <span class="card-title-level-2">
                <el-icon><Operation /></el-icon>
                {{ getTrendTitle('各环节耗时趋势') }}
              </span>
            </div>
          </template>
          
          <div v-loading="loading" class="trend-content">
            <div v-if="!loading && stepTrendData.length === 0" class="no-data">
              <el-empty description="暂无趋势数据" />
            </div>
            
            <div v-else-if="!loading" class="chart-container">
              <v-chart 
                class="chart" 
                :option="stepTrendOption" 
                autoresize
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 渠道查询趋势 -->
    <el-row :gutter="20" class="trend-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header-level-2">
              <span class="card-title-level-2">
                <el-icon><Share /></el-icon>
                {{ getTrendTitle('各渠道查询趋势') }}
              </span>
              <div class="header-controls">
                <el-radio-group v-model="channelViewType" size="small">
                  <el-radio-button label="all">全部</el-radio-button>
                  <el-radio-button label="member">项目组成员</el-radio-button>
                  <el-radio-button label="non_member">非项目组成员</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </template>
          
          <div v-loading="loading" class="trend-content">
            <div v-if="!loading && channelTrendData.length === 0" class="no-data">
              <el-empty description="暂无趋势数据" />
            </div>
            
            <div v-else-if="!loading" class="chart-container">
              <v-chart 
                class="chart" 
                :option="channelTrendOption" 
                autoresize
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { computed, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts, Operation, Share, Calendar, Refresh } from '@element-plus/icons-vue'
import { dashboardApi } from '@/services/api'

export default {
  name: 'WeeklyTrendCards',
  components: {
    TrendCharts,
    Operation,
    Share,
    Calendar,
    Refresh
  },
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    queryTrendData: {
      type: Array,
      default: () => []
    },
    stepTrendData: {
      type: Array,
      default: () => []
    },
    channelTrendData: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:loading'],
  setup(props, { emit }) {
    // 响应式数据
    const dateRangeType = ref('week') // week, month, custom
    const customDateRange = ref([])
    const channelViewType = ref('all') // all, member, non_member
    // 组件内部维护趋势数据状态
    const queryTrendData = ref([])
    const stepTrendData = ref([])
    const channelTrendData = ref([])

    // 计算当前日期范围
    const getCurrentDateRange = () => {
      const today = new Date()
      const todayStr = today.toISOString().split('T')[0]
      
      if (dateRangeType.value === 'week') {
        const weekAgo = new Date(today)
        weekAgo.setDate(today.getDate() - 6)
        return {
          startDate: weekAgo.toISOString().split('T')[0],
          endDate: todayStr
        }
      } else if (dateRangeType.value === 'month') {
        const monthAgo = new Date(today)
        monthAgo.setDate(today.getDate() - 29) // 30天
        return {
          startDate: monthAgo.toISOString().split('T')[0],
          endDate: todayStr
        }
      } else if (dateRangeType.value === 'custom' && customDateRange.value.length === 2) {
        return {
          startDate: customDateRange.value[0],
          endDate: customDateRange.value[1]
        }
      }
      
      // 默认返回一周
      const weekAgo = new Date(today)
      weekAgo.setDate(today.getDate() - 6)
      return {
        startDate: weekAgo.toISOString().split('T')[0],
        endDate: todayStr
      }
    }

    // 获取趋势标题
    const getTrendTitle = (baseTitle) => {
      if (dateRangeType.value === 'week') {
        return `最近一周${baseTitle}`
      } else if (dateRangeType.value === 'month') {
        return `最近一个月${baseTitle}`
      } else if (dateRangeType.value === 'custom') {
        return `自定义期间${baseTitle}`
      }
      return baseTitle
    }

    // 日期范围类型变化
    const onDateRangeTypeChange = () => {
      if (dateRangeType.value !== 'custom') {
        loadTrendData()
      }
    }

    // 自定义日期范围变化
    const onCustomDateChange = (dates) => {
      if (dates && dates.length === 2) {
        loadTrendData()
      }
    }

    // 加载趋势数据
    const loadTrendData = async () => {
      try {
        emit('update:loading', true)
        
        const dateRange = getCurrentDateRange()
        const params = {
          startDate: dateRange.startDate,
          endDate: dateRange.endDate
        }

        // 并行加载三个趋势数据
        const [queryTrend, stepTrend, channelTrend] = await Promise.all([
          dashboardApi.getWeeklyQueryTrend(params),
          dashboardApi.getWeeklyStepTrend(params),
          dashboardApi.getWeeklyChannelTrend(params)
        ])

        // 更新趋势数据
        queryTrendData.value = queryTrend || []
        stepTrendData.value = stepTrend || []
        channelTrendData.value = channelTrend || []


        ElMessage.success('趋势数据加载成功')
      } catch (error) {
        console.error('加载趋势数据失败:', error)
        ElMessage.error('趋势数据加载失败')
      } finally {
        emit('update:loading', false)
      }
    }

    // 组件挂载时加载默认数据
    onMounted(() => {
      loadTrendData()
    })

    // 查询趋势图表配置
    const queryTrendOption = computed(() => {
      if (queryTrendData.value.length === 0) return {}

      const dates = [...new Set(queryTrendData.value.map(item => item.date))].sort()
      
      return {
        title: {
          text: '查询数量变化趋势',
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
          data: dates,
          axisLabel: {
            formatter: function(value) {
              return value.substring(5) // 只显示月-日
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '查询数量'
        },
        series: [
          {
            name: '总查询',
            type: 'line',
          data: dates.map(date => {
            const item = queryTrendData.value.find(d => d.date === date)
            return item ? item.total_count : 0
          }),
            itemStyle: { color: '#5470C6' },
            smooth: true
          },
          {
            name: '项目组查询',
            type: 'line',
            data: dates.map(date => {
              const item = queryTrendData.value.find(d => d.date === date)
              return item ? item.member_count : 0
            }),
            itemStyle: { color: '#67C23A' },
            smooth: true
          },
          {
            name: '非项目组查询',
            type: 'line',
            data: dates.map(date => {
              const item = queryTrendData.value.find(d => d.date === date)
              return item ? item.non_member_count : 0
            }),
            itemStyle: { color: '#E6A23C' },
            smooth: true
          }
        ]
      }
    })

    // 步骤趋势图表配置
    const stepTrendOption = computed(() => {
      if (!stepTrendData.value || stepTrendData.value.length === 0) return {}

      const dates = [...new Set(stepTrendData.value.map(item => item.date))].sort()
      const steps = [...new Set(stepTrendData.value.map(item => item.step_name_cn))]
      
      const colors = ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE', '#3BA272']
      
      return {
        title: {
          text: '各环节平均耗时变化趋势',
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
          left: 'center',
          type: 'scroll'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            formatter: function(value) {
              return value.substring(5) // 只显示月-日
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '平均耗时(ms)',
          axisLabel: {
            formatter: function(value) {
              if (value < 1000) return value + 'ms'
              return (value / 1000).toFixed(1) + 's'
            }
          }
        },
        series: steps.map((stepCn, index) => ({
          name: stepCn,
          type: 'line',
          data: dates.map(date => {
            const item = stepTrendData.value.find(d => d.date === date && d.step_name_cn === stepCn)
            return item ? item.avg_cost : null
          }),
          itemStyle: { color: colors[index % colors.length] },
          smooth: true,
          connectNulls: false
        }))
      }
    })

    // 渠道趋势图表配置
    const channelTrendOption = computed(() => {
      if (!channelTrendData.value || channelTrendData.value.length === 0) return {}

      const dates = [...new Set(channelTrendData.value.map(item => item.date))].sort()
      const channels = [...new Set(channelTrendData.value.map(item => item.channel_name))]
      
      const colors = ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE', '#3BA272', '#FC8452']
      
      // 根据选择的维度确定标题和数据字段
      let titleText = '各渠道查询数量变化趋势'
      let countField = 'count'
      
      if (channelViewType.value === 'member') {
        titleText = '各渠道查询数量变化趋势（项目组成员）'
        countField = 'member_count'
      } else if (channelViewType.value === 'non_member') {
        titleText = '各渠道查询数量变化趋势（非项目组成员）'
        countField = 'non_member_count'
      }
      
      return {
        title: {
          text: titleText,
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
          }
        },
        legend: {
          bottom: '0',
          left: 'center',
          type: 'scroll'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            formatter: function(value) {
              return value.substring(5) // 只显示月-日
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '查询数量'
        },
        series: channels.map((channelName, index) => ({
          name: channelName,
          type: 'line',
          data: dates.map(date => {
            const item = channelTrendData.value.find(d => d.date === date && d.channel_name === channelName)
            return item ? item[countField] : 0
          }),
          itemStyle: { color: colors[index % colors.length] },
          smooth: true
        }))
      }
    })

    return {
      // 响应式数据
      dateRangeType,
      customDateRange,
      channelViewType,
      queryTrendData,
      stepTrendData,
      channelTrendData,
      
      // 计算属性
      queryTrendOption,
      stepTrendOption,
      channelTrendOption,
      
      // 方法
      getTrendTitle,
      onDateRangeTypeChange,
      onCustomDateChange,
      loadTrendData
    }
  }
}
</script>

<style scoped>
@import '@/styles/card-header.css';

.weekly-trends {
  padding: 0;
}

.trend-row {
  margin-bottom: 20px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.trend-content {
  min-height: 400px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.chart-container {
  height: 400px;
}

.chart {
  height: 100%;
  width: 100%;
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
</style>
