<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><User /></el-icon>
          {{ title }}
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
        <!-- 用户统计表格 -->
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
      </div>
    </div>
  </el-card>
</template>

<script>
import { computed, ref } from 'vue'
import { User, Avatar } from '@element-plus/icons-vue'

export default {
  name: 'UserStatsCard',
  components: {
    User,
    Avatar
  },
  props: {
    title: {
      type: String,
      required: true
    },
    users: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const currentPage = ref(1)
    const pageSize = ref(10)

    // 分页用户列表
    const paginatedUsers = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return props.users.slice(start, end)
    })

    // 最大查询次数
    const maxCount = computed(() => {
      return Math.max(...props.users.map(user => user.count), 1)
    })

    // 计算使用百分比
    const getUsagePercentage = (count) => {
      return Math.round((count / maxCount.value) * 100)
    }

    // 获取排名标签类型
    const getRankTagType = (rank) => {
      if (rank <= 3) return 'danger'
      if (rank <= 10) return 'warning'
      return 'info'
    }

    // 页码变化处理
    const handlePageChange = (page) => {
      currentPage.value = page
    }

    return {
      currentPage,
      pageSize,
      paginatedUsers,
      maxCount,
      getUsagePercentage,
      getRankTagType,
      handlePageChange
    }
  }
}
</script>

<style scoped>
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
  font-size: 16px;
}

.user-content {
  min-height: 400px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.count-tag {
  font-size: 14px;
  font-weight: bold;
  padding: 4px 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
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

:deep(.el-progress-bar__outer) {
  border-radius: 10px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 10px;
}

:deep(.el-pagination) {
  font-weight: 500;
}
</style>
