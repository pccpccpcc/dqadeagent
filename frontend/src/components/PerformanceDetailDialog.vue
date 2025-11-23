<template>
  <el-dialog
    v-model="dialogVisible"
    title="性能详细分析"
    width="80%"
    :before-close="handleClose"
  >
    <div v-loading="loading" class="dialog-content">
      <div v-if="!loading && detailData" class="performance-detail">
        <!-- 基本信息 -->
        <div class="basic-info">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><InfoFilled /></el-icon>
                  基本信息
                </span>
              </div>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="业务流水号">
                <el-tag type="primary">{{ detailData.biz_seq }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="总耗时">
                <span class="total-cost">{{ formatTime(detailData.total_cost) }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>

        <!-- 步骤耗时分析 -->
        <div class="steps-analysis">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Operation /></el-icon>
                  步骤耗时分析
                </span>
              </div>
            </template>
            
            <el-table
              :data="detailData.steps"
              style="width: 100%"
              size="small"
              stripe
            >
              <el-table-column prop="step_name_cn" label="步骤名称" width="150">
                <template #default="{ row }">
                  <div class="step-name">
                    <el-icon><Timer /></el-icon>
                    {{ row.step_name_cn }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="sub_step_name" label="子步骤" width="120">
                <template #default="{ row }">
                  <el-tag size="small" type="info">{{ row.sub_step_name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="cost" label="耗时" width="120" align="center">
                <template #default="{ row }">
                  <span class="cost-time">{{ formatTime(row.cost) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="占比" width="150" align="center">
                <template #default="{ row }">
                  <el-progress 
                    :percentage="getStepPercentage(row.cost)" 
                    :show-text="true"
                    :format="() => `${getStepPercentage(row.cost)}%`"
                    :color="getProgressColor(getStepPercentage(row.cost))"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="step_name" label="英文标识" min-width="150">
                <template #default="{ row }">
                  <code class="step-code">{{ row.step_name }}</code>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <!-- DS请求步骤 -->
        <div v-if="detailData.req_ds_steps.length > 0" class="ds-steps">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Connection /></el-icon>
                  DS请求步骤耗时
                </span>
              </div>
            </template>
            
            <el-table
              :data="detailData.req_ds_steps"
              style="width: 100%"
              size="small"
              stripe
            >
              <el-table-column prop="step_name_cn" label="步骤名称" width="150" />
              <el-table-column prop="sub_step_name" label="子步骤" width="120">
                <template #default="{ row }">
                  <el-tag size="small" type="warning">{{ row.sub_step_name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="cost" label="耗时" width="120" align="center">
                <template #default="{ row }">
                  <span class="cost-time ds-cost">{{ formatTime(row.cost) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="step_name" label="英文标识" min-width="150">
                <template #default="{ row }">
                  <code class="step-code">{{ row.step_name }}</code>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <!-- SQL执行耗时 -->
        <div v-if="detailData.sql_execution_times.length > 0" class="sql-times">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><DocumentCopy /></el-icon>
                  SQL实际执行耗时
                </span>
              </div>
            </template>
            
            <div class="sql-times-list">
              <div 
                v-for="(time, index) in detailData.sql_execution_times" 
                :key="index"
                class="sql-time-item"
              >
                <div class="sql-index">SQL #{{ index + 1 }}</div>
                <div class="sql-time">
                  <el-tag type="success">{{ formatSqlTime(time) }}</el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 性能图表 -->
        <div class="performance-chart">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Histogram /></el-icon>
                  步骤耗时分布
                </span>
              </div>
            </template>
            
            <div class="chart-container">
              <v-chart 
                class="chart" 
                :option="chartOption" 
                autoresize
              />
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="exportDetail">导出详情</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  InfoFilled, 
  Operation, 
  Timer, 
  Connection, 
  DocumentCopy, 
  Histogram 
} from '@element-plus/icons-vue'
import { dashboardApi } from '@/services/api'

export default {
  name: 'PerformanceDetailDialog',
  components: {
    InfoFilled,
    Operation,
    Timer,
    Connection,
    DocumentCopy,
    Histogram
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    bizSeq: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const loading = ref(false)
    const detailData = ref(null)

    // 对话框可见性
    const dialogVisible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    // 监听bizSeq变化，加载详情数据
    watch(() => props.bizSeq, async (newBizSeq) => {
      if (newBizSeq && props.modelValue) {
        await loadDetailData(newBizSeq)
      }
    })

    // 监听对话框打开，加载数据
    watch(() => props.modelValue, async (visible) => {
      if (visible && props.bizSeq) {
        await loadDetailData(props.bizSeq)
      }
    })

    // 加载详情数据
    const loadDetailData = async (bizSeq) => {
      loading.value = true
      try {
        const data = await dashboardApi.getPerformanceDetail(bizSeq)
        detailData.value = data
      } catch (error) {
        console.error('加载性能详情失败:', error)
        ElMessage.error('加载性能详情失败')
      } finally {
        loading.value = false
      }
    }

    // 格式化时间
    const formatTime = (time) => {
      if (!time) return '0ms'
      if (time < 1000) return `${Math.round(time)}ms`
      return `${(time / 1000).toFixed(2)}s`
    }

    // 格式化SQL时间
    const formatSqlTime = (time) => {
      if (!time || time === 'null' || time === '0') return '0ms'
      const numTime = parseFloat(time)
      if (isNaN(numTime)) return time
      if (numTime < 1) return `${Math.round(numTime * 1000)}ms`
      return `${numTime.toFixed(2)}s`
    }

    // 计算步骤耗时占比
    const getStepPercentage = (cost) => {
      if (!detailData.value || detailData.value.total_cost === 0) return 0
      return Math.round((cost / detailData.value.total_cost) * 100)
    }

    // 获取进度条颜色
    const getProgressColor = (percentage) => {
      if (percentage < 20) return '#67C23A'
      if (percentage < 50) return '#E6A23C'
      return '#F56C6C'
    }

    // 图表配置
    const chartOption = computed(() => {
      if (!detailData.value) return {}

      const steps = detailData.value.steps || []
      
      return {
        title: {
          text: '步骤耗时分布',
          left: 'center'
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return `${params.name}<br/>耗时: ${formatTime(params.value)}<br/>占比: ${params.percent}%`
          }
        },
        series: [
          {
            type: 'pie',
            radius: ['30%', '70%'],
            center: ['50%', '60%'],
            data: steps.map(step => ({
              name: step.step_name_cn,
              value: step.cost
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              formatter: function(params) {
                return `${params.name}\n${formatTime(params.value)}`
              }
            }
          }
        ]
      }
    })

    // 关闭对话框
    const handleClose = () => {
      dialogVisible.value = false
      detailData.value = null
    }

    // 导出详情
    const exportDetail = () => {
      if (!detailData.value) return
      
      const data = {
        bizSeq: detailData.value.biz_seq,
        totalCost: detailData.value.total_cost,
        steps: detailData.value.steps,
        reqDsSteps: detailData.value.req_ds_steps,
        sqlExecutionTimes: detailData.value.sql_execution_times
      }
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `performance_detail_${detailData.value.biz_seq}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      ElMessage.success('性能详情已导出')
    }

    return {
      loading,
      detailData,
      dialogVisible,
      formatTime,
      formatSqlTime,
      getStepPercentage,
      getProgressColor,
      chartOption,
      handleClose,
      exportDetail
    }
  }
}
</script>

<style scoped>
.dialog-content {
  min-height: 400px;
}

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

.basic-info,
.steps-analysis,
.ds-steps,
.sql-times,
.performance-chart {
  margin-bottom: 20px;
}

.step-name {
  display: flex;
  align-items: center;
  gap: 5px;
}

.cost-time {
  font-weight: bold;
  color: #409eff;
}

.ds-cost {
  color: #e6a23c;
}

.step-code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.total-cost {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
}

.sql-times-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.sql-time-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.sql-index {
  font-weight: 500;
  color: #333;
}

.chart-container {
  height: 300px;
}

.chart {
  height: 100%;
  width: 100%;
}

:deep(.el-dialog) {
  border-radius: 8px;
}

:deep(.el-dialog__header) {
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

:deep(.el-card) {
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-table) {
  border-radius: 6px;
}

:deep(.el-progress-bar__outer) {
  border-radius: 10px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 10px;
}
</style>

