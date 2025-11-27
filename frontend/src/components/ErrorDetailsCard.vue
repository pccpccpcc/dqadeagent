<template>
  <el-card class="error-details-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><DocumentCopy /></el-icon>
          错误明细数据
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="error-details-content">
      <el-row :gutter="20">
        <!-- Agent子系统错误明细 (三层结构) -->
        <el-col :span="12">
          <AgentErrorDetails
            :error-data="agentErrorData"
            :loading="loading"
          />
        </el-col>
        
        <!-- DS子系统错误明细 (两层结构) -->
        <el-col :span="12">
          <DsErrorDetails
            :error-data="dsErrorData"
            :loading="loading"
          />
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script>
import { DocumentCopy } from '@element-plus/icons-vue'
import AgentErrorDetails from './AgentErrorDetails.vue'
import DsErrorDetails from './DsErrorDetails.vue'

export default {
  name: 'ErrorDetailsCard',
  components: {
    DocumentCopy,
    AgentErrorDetails,
    DsErrorDetails
  },
  props: {
    agentErrorData: {
      type: Object,
      default: () => ({})
    },
    dsErrorData: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.error-details-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 18px;
}

.error-details-content {
  min-height: 200px;
}
</style>

