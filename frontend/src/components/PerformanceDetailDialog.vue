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
              <el-descriptions-item label="业务流水号" :span="2">
                <el-tag type="primary">{{ detailData.biz_seq }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="用户查询" :span="2">
                <div class="query-text">{{ userQuery }}</div>
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

        <!-- SQL执行详情 -->
        <div v-if="detailData.sql_details && detailData.sql_details.length > 0" class="sql-details">
          <el-card>
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><DocumentCopy /></el-icon>
                  SQL执行详情
                </span>
              </div>
            </template>
            
            <el-table
              :data="detailData.sql_details"
              style="width: 100%"
              size="small"
              stripe
              border
            >
              <el-table-column type="index" label="序号" width="60" align="center" />
              <el-table-column label="SQL语句" min-width="300">
                <template #default="{ row }">
                  <div class="sql-str-cell">
                    <div class="sql-preview">{{ truncateSql(row.sql_str, 80) }}</div>
                    <el-button 
                      size="small" 
                      text 
                      type="primary"
                      @click="viewSqlDetail(row.sql_str)"
                    >
                      查看完整SQL
                    </el-button>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="query_time" label="调用DS耗时(ms)" width="140" align="right">
                <template #default="{ row }">
                  <span class="cost-value query-time">{{ row.query_time || 0 }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="sql_execute_time" label="SQL实际执行耗时(ms)" width="180" align="right">
                <template #default="{ row }">
                  <span class="cost-value execute-time">{{ row.sql_execute_time || 0 }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="create_time" label="执行时间" width="160" align="center" />
            </el-table>
          </el-card>
        </div>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>

    <!-- SQL详情对话框 -->
    <el-dialog 
      v-model="sqlDialogVisible" 
      title="完整SQL语句"
      width="70%"
      :destroy-on-close="true"
    >
      <div class="sql-detail-content">
        <pre>{{ currentSql }}</pre>
      </div>
      <template #footer>
        <el-button @click="sqlDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="copySql">复制</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  InfoFilled, 
  Operation,
  Timer,
  DocumentCopy
} from '@element-plus/icons-vue'
import { dashboardApi } from '@/services/api'

export default {
  name: 'PerformanceDetailDialog',
  components: {
    InfoFilled,
    Operation,
    Timer,
    DocumentCopy
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
    const sqlDialogVisible = ref(false)
    const currentSql = ref('')

    // 对话框可见性
    const dialogVisible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    // 提取用户查询query字段
    const userQuery = computed(() => {
      if (!detailData.value || !detailData.value.req_info) {
        return '无查询信息'
      }
      try {
        const reqInfo = typeof detailData.value.req_info === 'string' 
          ? JSON.parse(detailData.value.req_info) 
          : detailData.value.req_info
        return reqInfo.query || '无查询信息'
      } catch (e) {
        console.error('解析req_info失败:', e)
        return '解析失败'
      }
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

    // 截断SQL显示
    const truncateSql = (sql, maxLength) => {
      if (!sql) return '无SQL'
      const str = String(sql)
      if (str.length <= maxLength) return str
      return str.substring(0, maxLength) + '...'
    }

    // 查看SQL详情
    const viewSqlDetail = (sql) => {
      currentSql.value = sql
      sqlDialogVisible.value = true
    }

    // 复制SQL
    const copySql = () => {
      navigator.clipboard.writeText(currentSql.value).then(() => {
        ElMessage.success('已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    }

    // 格式化时间
    const formatTime = (time) => {
      if (!time) return '0ms'
      if (time < 1000) return `${Math.round(time)}ms`
      return `${(time / 1000).toFixed(2)}s`
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

    // 关闭对话框
    const handleClose = () => {
      dialogVisible.value = false
      detailData.value = null
    }

    return {
      loading,
      detailData,
      dialogVisible,
      userQuery,
      sqlDialogVisible,
      currentSql,
      truncateSql,
      viewSqlDetail,
      copySql,
      formatTime,
      getStepPercentage,
      getProgressColor,
      handleClose
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
.sql-details {
  margin-bottom: 20px;
}

.query-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  padding: 8px 0;
}

.total-cost {
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
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

.step-code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.sql-str-cell {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.sql-preview {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #606266;
  word-break: break-all;
  line-height: 1.4;
}

.cost-value {
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.cost-value.query-time {
  color: #409EFF;
}

.cost-value.execute-time {
  color: #E6A23C;
}

.sql-detail-content {
  max-height: 600px;
  overflow-y: auto;
  background: #F5F7FA;
  padding: 20px;
  border-radius: 4px;
  border: 1px solid #DCDFE6;
}

.sql-detail-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-wrap: break-word;
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
