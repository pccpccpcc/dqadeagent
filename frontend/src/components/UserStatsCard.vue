<template>
  <el-card>
    <template #header>
      <div class="card-header-level-1">
        <span class="card-title-level-1">
          <el-icon><User /></el-icon>
          用户明细数据
        </span>
        <div class="header-extra">
          <el-tag type="info" size="small">
            总用户数: {{ users.length }}
          </el-tag>
        </div>
      </div>
    </template>
    
    <div v-loading="loading" class="user-content">
      <div v-if="!loading && users.length === 0" class="no-data">
        <el-empty description="暂无用户数据" />
      </div>
      
      <div v-else-if="!loading" class="user-stats">
        <!-- 留存率统计卡片 -->
        <el-row :gutter="20" class="retention-section">
          <el-col :span="12">
            <div class="retention-card">
              <div class="retention-header">
                <el-icon class="retention-icon"><TrendCharts /></el-icon>
                <span class="retention-title">7日留存率</span>
              </div>
              <div class="retention-content">
                <div class="retention-rate">{{ retentionStats.day7_retention?.retention_rate || 0 }}%</div>
                <div class="retention-detail">
                  <span>基准用户: {{ retentionStats.day7_retention?.d0_users || 0 }}</span>
                  <span class="divider">|</span>
                  <span>留存用户: {{ retentionStats.day7_retention?.d7_retained || 0 }}</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="retention-card">
              <div class="retention-header">
                <el-icon class="retention-icon"><TrendCharts /></el-icon>
                <span class="retention-title">15日留存率</span>
              </div>
              <div class="retention-content">
                <div class="retention-rate">{{ retentionStats.day15_retention?.retention_rate || 0 }}%</div>
                <div class="retention-detail">
                  <span>基准用户: {{ retentionStats.day15_retention?.d0_users || 0 }}</span>
                  <span class="divider">|</span>
                  <span>留存用户: {{ retentionStats.day15_retention?.d15_retained || 0 }}</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- Tabs: 活跃用户 / 7日流失 / 15日流失 -->
        <el-tabs v-model="activeTab" class="user-tabs">
          <!-- 活跃用户列表 -->
          <el-tab-pane label="活跃用户列表" name="active">
            <el-table
              :data="paginatedUsers"
              style="width: 100%"
              stripe
              border
            >
              <el-table-column prop="rank" label="排名" width="80" align="center">
                <template #default="{ row }">
                  <el-tag 
                    :type="getRankTagType(row.rank)" 
                    size="small"
                  >
                    #{{ row.rank }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="user_id" label="用户ID" min-width="200">
                <template #default="{ row }">
                  <div class="user-cell">
                    <el-icon><Avatar /></el-icon>
                    <span>{{ row.user_id || '未知用户' }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="查询次数" width="150" align="center">
                <template #default="{ row }">
                  <el-tag type="primary" class="count-tag">
                    {{ row.count }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="活跃度" width="200" align="center">
                <template #default="{ row }">
                  <el-progress 
                    :percentage="getUsagePercentage(row.count)" 
                    :show-text="true"
                    :format="() => `${getUsagePercentage(row.count)}%`"
                  />
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 分页 -->
            <div class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="users.length"
                layout="total, prev, pager, next, jumper"
                @current-change="handlePageChange"
              />
            </div>
          </el-tab-pane>

          <!-- 7日流失用户 -->
          <el-tab-pane name="churned7">
            <template #label>
              <span>
                7日流失用户
                <el-badge :value="churnedUsers.churned_7_days?.count || 0" class="badge" />
              </span>
            </template>
            <el-table
              :data="paginatedChurned7Users"
              style="width: 100%"
              stripe
              border
            >
              <el-table-column prop="user_id" label="用户ID" min-width="200">
                <template #default="{ row }">
                  <div class="user-cell">
                    <el-icon><Avatar /></el-icon>
                    <span>{{ row.user_id }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="last_active_date" label="最后活跃日期" width="150" align="center" />
              <el-table-column prop="days_inactive" label="未活跃天数" width="120" align="center">
                <template #default="{ row }">
                  <el-tag type="danger">{{ row.days_inactive }} 天</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="total_queries" label="历史查询次数" width="130" align="center">
                <template #default="{ row }">
                  <el-tag type="info">{{ row.total_queries }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 分页 -->
            <div class="pagination">
              <el-pagination
                v-model:current-page="churned7Page"
                :page-size="pageSize"
                :total="churnedUsers.churned_7_days?.users?.length || 0"
                layout="total, prev, pager, next, jumper"
                @current-change="handleChurned7PageChange"
              />
            </div>
          </el-tab-pane>

          <!-- 15日流失用户 -->
          <el-tab-pane name="churned15">
            <template #label>
              <span>
                15日流失用户
                <el-badge :value="churnedUsers.churned_15_days?.count || 0" class="badge" />
              </span>
            </template>
            <el-table
              :data="paginatedChurned15Users"
              style="width: 100%"
              stripe
              border
            >
              <el-table-column prop="user_id" label="用户ID" min-width="200">
                <template #default="{ row }">
                  <div class="user-cell">
                    <el-icon><Avatar /></el-icon>
                    <span>{{ row.user_id }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="last_active_date" label="最后活跃日期" width="150" align="center" />
              <el-table-column prop="days_inactive" label="未活跃天数" width="120" align="center">
                <template #default="{ row }">
                  <el-tag type="danger">{{ row.days_inactive }} 天</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="total_queries" label="历史查询次数" width="130" align="center">
                <template #default="{ row }">
                  <el-tag type="info">{{ row.total_queries }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 分页 -->
            <div class="pagination">
              <el-pagination
                v-model:current-page="churned15Page"
                :page-size="pageSize"
                :total="churnedUsers.churned_15_days?.users?.length || 0"
                layout="total, prev, pager, next, jumper"
                @current-change="handleChurned15PageChange"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </el-card>
</template>

<script>
import { computed, ref } from 'vue'
import { User, Avatar, TrendCharts } from '@element-plus/icons-vue'

export default {
  name: 'UserStatsCard',
  components: {
    User,
    Avatar,
    TrendCharts
  },
  props: {
    users: {
      type: Array,
      default: () => []
    },
    retentionStats: {
      type: Object,
      default: () => ({})
    },
    churnedUsers: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const activeTab = ref('active')
    const currentPage = ref(1)
    const churned7Page = ref(1)
    const churned15Page = ref(1)
    const pageSize = 10

    // 计算活跃用户分页数据
    const paginatedUsers = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return props.users.slice(start, end)
    })

    // 计算7日流失用户分页数据
    const paginatedChurned7Users = computed(() => {
      const users = props.churnedUsers.churned_7_days?.users || []
      const start = (churned7Page.value - 1) * pageSize
      const end = start + pageSize
      return users.slice(start, end)
    })

    // 计算15日流失用户分页数据
    const paginatedChurned15Users = computed(() => {
      const users = props.churnedUsers.churned_15_days?.users || []
      const start = (churned15Page.value - 1) * pageSize
      const end = start + pageSize
      return users.slice(start, end)
    })

    const getRankTagType = (rank) => {
      if (rank === 1) return 'danger'
      if (rank === 2) return 'warning'
      if (rank === 3) return 'success'
      return 'info'
    }

    const getUsagePercentage = (count) => {
      if (props.users.length === 0) return 0
      const maxCount = Math.max(...props.users.map(u => u.count))
      return Math.round((count / maxCount) * 100)
    }

    const handlePageChange = (page) => {
      currentPage.value = page
    }

    const handleChurned7PageChange = (page) => {
      churned7Page.value = page
    }

    const handleChurned15PageChange = (page) => {
      churned15Page.value = page
    }

    return {
      activeTab,
      currentPage,
      churned7Page,
      churned15Page,
      pageSize,
      paginatedUsers,
      paginatedChurned7Users,
      paginatedChurned15Users,
      getRankTagType,
      getUsagePercentage,
      handlePageChange,
      handleChurned7PageChange,
      handleChurned15PageChange
    }
  }
}
</script>

<style scoped>
@import '@/styles/card-header.css';

.user-content {
  min-height: 400px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.user-stats {
  width: 100%;
}

.retention-section {
  margin-bottom: 20px;
}

.retention-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 20px;
  color: white;
}

.retention-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
}

.retention-icon {
  font-size: 20px;
}

.retention-title {
  font-size: 14px;
  font-weight: 500;
  opacity: 0.9;
}

.retention-content {
  text-align: center;
}

.retention-rate {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 10px;
}

.retention-detail {
  font-size: 12px;
  opacity: 0.8;
}

.retention-detail .divider {
  margin: 0 8px;
}

.user-tabs {
  margin-top: 20px;
}

.user-tabs :deep(.el-tabs__item) {
  font-size: 14px;
}

.badge {
  margin-left: 5px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-tag {
  font-weight: 500;
  font-size: 14px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
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

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}

:deep(.el-progress__text) {
  font-size: 12px !important;
}
</style>
