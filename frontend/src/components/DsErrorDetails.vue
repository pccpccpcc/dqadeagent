<template>
  <div class="subsystem-error-details">
    <div class="subsystem-header">
      <h3>DS子系统错误明细</h3>
      <div class="subsystem-summary">
        <el-tag type="warning">业务错误: {{ errorData.total_business_count || 0 }}</el-tag>
        <el-tag type="danger">系统错误: {{ errorData.total_system_count || 0 }}</el-tag>
      </div>
    </div>
    
    <el-tabs v-model="activeTab" class="error-tabs">
      <!-- 业务错误标签页 -->
      <el-tab-pane label="业务错误" name="business">
        <div v-if="!errorData.business_errors || errorData.business_errors.length === 0" class="empty-state">
          <el-empty description="暂无业务错误数据" :image-size="100" />
        </div>
        <el-collapse v-else v-model="activeBusinessCodes" accordion>
          <!-- 第一层：错误码 + 中文含义 -->
          <el-collapse-item 
            v-for="errorCode in errorData.business_errors" 
            :key="`business-${errorCode.code}`"
            :name="`business-${errorCode.code}`"
          >
            <template #title>
              <div class="error-code-title">
                <el-icon><Warning /></el-icon>
                <span class="code-badge">{{ errorCode.code }}</span>
                <span class="code-name">{{ errorCode.code_name }}</span>
                <el-tag size="small" type="warning">{{ errorCode.count }}条</el-tag>
              </div>
            </template>
            
            <!-- 第二层：错误详情表格 -->
            <div class="error-details-list">
              <el-table :data="errorCode.details" border stripe size="small">
                <el-table-column prop="biz_seq" label="业务流水号" width="250" />
                <el-table-column prop="create_time" label="时间" width="160" />
                <el-table-column label="用户请求" min-width="220">
                  <template #default="scope">
                    <div class="query-text">
                      {{ extractQuery(scope.row.req_info) }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="DS响应" min-width="220">
                  <template #default="scope">
                    <div class="query-text">
                      {{ extractQueryRsp(scope.row.rsp_info) }}
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-tab-pane>
      
      <!-- 系统错误标签页 -->
      <el-tab-pane label="系统错误" name="system">
        <div v-if="!errorData.system_errors || errorData.system_errors.length === 0" class="empty-state">
          <el-empty description="暂无系统错误数据" :image-size="100" />
        </div>
        <el-collapse v-else v-model="activeSystemCodes" accordion>
          <!-- 第一层：错误码 + 中文含义 -->
          <el-collapse-item 
            v-for="errorCode in errorData.system_errors" 
            :key="`system-${errorCode.code}`"
            :name="`system-${errorCode.code}`"
          >
            <template #title>
              <div class="error-code-title">
                <el-icon><CircleClose /></el-icon>
                <span class="code-badge">{{ errorCode.code }}</span>
                <span class="code-name">{{ errorCode.code_name }}</span>
                <el-tag size="small" type="danger">{{ errorCode.count }}条</el-tag>
              </div>
            </template>
            
            <!-- 第二层：错误详情表格 -->
            <div class="error-details-list">
              <el-table :data="errorCode.details" border stripe size="small">
                <el-table-column prop="biz_seq" label="业务流水号" width="250" />
                <el-table-column prop="create_time" label="时间" width="160" />
                <el-table-column label="用户请求" min-width="220">
                  <template #default="scope">
                    <div class="query-text">
                      {{ extractQuery(scope.row.req_info) }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="DS响应" min-width="220">
                  <template #default="scope">
                    <div class="query-text">
                      {{ extractQueryRsp(scope.row.rsp_info) }}
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref } from 'vue'
import { Warning, CircleClose } from '@element-plus/icons-vue'

export default {
  name: 'DsErrorDetails',
  components: {
    Warning,
    CircleClose
  },
  props: {
    errorData: {
      type: Object,
      default: () => ({
        business_errors: [],
        system_errors: [],
        total_business_count: 0,
        total_system_count: 0
      })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const activeTab = ref('business')
    const activeBusinessCodes = ref([])
    const activeSystemCodes = ref([])
    
    // 从req_info中提取query字段
    const extractQuery = (reqInfo) => {
      if (!reqInfo) return '无数据'
      try {
        const obj = typeof reqInfo === 'string' ? JSON.parse(reqInfo) : reqInfo
        return obj.query || '无查询信息'
      } catch (e) {
        return '解析失败'
      }
    }
    
    // 从rsp_info中提取queryRsp字段
    const extractQueryRsp = (rspInfo) => {
      if (!rspInfo) return '无数据'
      try {
        const obj = typeof rspInfo === 'string' ? JSON.parse(rspInfo) : rspInfo
        return obj.queryRsp || '无响应信息'
      } catch (e) {
        return '解析失败'
      }
    }
    
    return {
      activeTab,
      activeBusinessCodes,
      activeSystemCodes,
      extractQuery,
      extractQueryRsp
    }
  }
}
</script>

<style scoped>
.subsystem-error-details {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 15px;
  background: #FAFAFA;
}

.subsystem-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #EBEEF5;
}

.subsystem-header h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}

.subsystem-summary {
  display: flex;
  gap: 10px;
}

.error-tabs {
  background: white;
  border-radius: 4px;
  padding: 10px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.error-code-title {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  font-size: 14px;
}

.code-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  font-size: 13px;
}

.code-name {
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.error-details-list {
  padding: 15px;
  background: #F5F7FA;
  border-radius: 4px;
}

.query-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  word-break: break-word;
  padding: 4px 0;
}

:deep(.el-collapse-item__header) {
  padding: 12px 16px;
  background: #FAFAFA;
  border-bottom: 1px solid #EBEEF5;
  font-size: 14px;
  transition: all 0.3s;
}

:deep(.el-collapse-item__header:hover) {
  background: #F0F2F5;
}

:deep(.el-collapse-item__content) {
  padding: 0;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background: #F5F7FA;
  color: #606266;
  font-weight: 600;
}
</style>

