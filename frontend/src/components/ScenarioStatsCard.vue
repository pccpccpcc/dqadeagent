<template>
  <el-card>
    <template #header v-if="showHeader">
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
        <el-table
          :data="scenarios"
          style="width: 100%"
          stripe
          border
        >
          <el-table-column prop="scenario_name" label="场景" width="150">
            <template #default="{ row }">
              <div class="scenario-name">
                <el-icon><Document /></el-icon>
                <span>{{ row.scenario_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="总体" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="primary" class="count-tag">
                {{ row.count }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="项目组" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="success" class="count-tag">
                {{ row.member_count }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="非项目组" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" class="count-tag">
                {{ row.non_member_count }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </el-card>
</template>

<script>
import { Grid, Document } from '@element-plus/icons-vue'

export default {
  name: 'ScenarioStatsCard',
  components: {
    Grid,
    Document
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
    },
    showHeader: {
      type: Boolean,
      default: true
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
  min-height: 200px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.scenario-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
}

.count-tag {
  font-size: 14px;
  font-weight: bold;
  padding: 4px 12px;
}

:deep(.el-table) {
  border-radius: 6px;
}

:deep(.el-table th) {
  background: #f5f7fa;
  font-weight: 600;
  font-size: 14px;
}

:deep(.el-table .el-table__body tr:hover > td) {
  background-color: #f5f7fa;
}

:deep(.el-table td) {
  padding: 16px 0;
}
</style>
