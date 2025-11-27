<template>
  <div class="performance-detail-subcard">
    <div class="subcard-header">
      <h3>{{ title }}</h3>
    </div>
    
    <div v-loading="loading" class="performance-content">
      <div v-if="!performance || performance.length === 0" class="empty-state">
        <el-empty description="暂无耗时数据" :image-size="100" />
      </div>
      <el-table v-else :data="performance" border stripe size="small">
        <el-table-column prop="category" label="查询类型" width="180" />
        <el-table-column prop="avg_cost" label="平均耗时(ms)" width="120" align="right">
          <template #default="scope">
            <span class="cost-value">{{ scope.row.avg_cost }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="p90_cost" label="P90耗时(ms)" width="120" align="right">
          <template #default="scope">
            <span class="cost-value p90">{{ scope.row.p90_cost }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="max_cost" label="最大耗时(ms)" width="120" align="right">
          <template #default="scope">
            <span class="cost-value max">{{ scope.row.max_cost }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="scope">
            <el-button
              v-if="scope.row.max_cost_biz_seq"
              size="small"
              text
              type="primary"
              @click="$emit('view-detail', scope.row.max_cost_biz_seq)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PerformanceDetailSubCard',
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
  emits: ['view-detail']
}
</script>

<style scoped>
.performance-detail-subcard {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 15px;
  background: #FAFAFA;
}

.subcard-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #EBEEF5;
}

.subcard-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.performance-content {
  min-height: 200px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.cost-value {
  font-family: 'Courier New', monospace;
  font-weight: 500;
  color: #409EFF;
}

.cost-value.p90 {
  color: #E6A23C;
}

.cost-value.max {
  color: #F56C6C;
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

