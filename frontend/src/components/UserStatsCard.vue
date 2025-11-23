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
        <!-- 用户排行榜 -->
        <div class="user-ranking">
          <h4 class="section-title">
            <el-icon><TrophyBase /></el-icon>
            用户活跃度排行榜
          </h4>
          
          <div class="top-users">
            <div 
              v-for="(user, index) in topUsers" 
              :key="user.user_id"
              class="top-user-item"
              :class="getRankClass(user.rank)"
            >
              <div class="rank-badge">
                <el-icon v-if="user.rank <= 3">
                  <component :is="getRankIcon(user.rank)" />
                </el-icon>
                <span v-else class="rank-number">{{ user.rank }}</span>
              </div>
              <div class="user-info">
                <div class="user-name">{{ user.user_id || '未知用户' }}</div>
                <div class="user-count">{{ user.count }}次查询</div>
              </div>
              <div class="usage-bar">
                <el-progress 
                  :percentage="getUsagePercentage(user.count)" 
                  :show-text="false"
                  :color="getRankColor(user.rank)"
                />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 用户统计表格 -->
        <div class="user-table">
          <el-table
            :data="paginatedUsers"
            style="width: 100%"
            size="small"
            stripe
            max-height="300"
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
            <el-table-column prop="user_id" label="用户ID" min-width="150">
              <template #default="{ row }">
                <div class="user-cell">
                  <el-icon><Avatar /></el-icon>
                  <span>{{ row.user_id || '未知用户' }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="查询次数" width="120" align="center">
              <template #default="{ row }">
                <span class="count-number">{{ row.count }}</span>
              </template>
            </el-table-column>
            <el-table-column label="活跃度" width="150" align="center">
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
              layout="prev, pager, next"
              small
            />
          </div>
        </div>
        
        <!-- 用户分布图表 -->
        <div class="chart-container">
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
import { computed, ref } from 'vue'
import { User, TrophyBase, Avatar } from '@element-plus/icons-vue'

export default {
  name: 'UserStatsCard',
  components: {
    User,
    TrophyBase,
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

    // 前5名用户
    const topUsers = computed(() => {
      return props.users.slice(0, 5)
    })

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

    // 获取排名类型
    const getRankClass = (rank) => {
      if (rank === 1) return 'gold'
      if (rank === 2) return 'silver'  
      if (rank === 3) return 'bronze'
      return 'normal'
    }

    // 获取排名图标
    const getRankIcon = (rank) => {
      const icons = ['', 'TrophyBase', 'TrophyBase', 'TrophyBase']
      return icons[rank] || 'TrophyBase'
    }

    // 获取排名颜色
    const getRankColor = (rank) => {
      if (rank === 1) return '#FFD700'
      if (rank === 2) return '#C0C0C0'
      if (rank === 3) return '#CD7F32'
      return '#409EFF'
    }

    // 获取排名标签类型
    const getRankTagType = (rank) => {
      if (rank <= 3) return 'danger'
      if (rank <= 10) return 'warning'
      return 'info'
    }

    // 图表配置
    const chartOption = computed(() => {
      const topUsersData = props.users.slice(0, 10)
      
      return {
        title: {
          text: 'TOP 10 活跃用户',
          left: 'center',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const param = params[0]
            return `${param.axisValue}<br/>查询次数: ${param.value}`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '查询次数'
        },
        yAxis: {
          type: 'category',
          data: topUsersData.map(user => user.user_id || '未知用户'),
          axisLabel: {
            fontSize: 11,
            formatter: function(value) {
              return value.length > 10 ? value.substring(0, 10) + '...' : value
            }
          }
        },
        series: [
          {
            type: 'bar',
            data: topUsersData.map((user, index) => ({
              value: user.count,
              itemStyle: {
                color: function() {
                  const colors = ['#FFD700', '#C0C0C0', '#CD7F32', '#409EFF', '#67C23A', 
                                 '#E6A23C', '#F56C6C', '#909399', '#5470C6', '#91CC75']
                  return colors[index] || '#409EFF'
                }
              }
            })),
            barWidth: '60%',
            label: {
              show: true,
              position: 'right',
              formatter: '{c}'
            }
          }
        ]
      }
    })

    return {
      currentPage,
      pageSize,
      topUsers,
      paginatedUsers,
      maxCount,
      getUsagePercentage,
      getRankClass,
      getRankIcon,
      getRankColor,
      getRankTagType,
      chartOption
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
  min-height: 600px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 600px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 15px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.top-users {
  margin-bottom: 30px;
}

.top-user-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.top-user-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.top-user-item.gold {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  color: white;
}

.top-user-item.silver {
  background: linear-gradient(135deg, #C0C0C0 0%, #A9A9A9 100%);
  color: white;
}

.top-user-item.bronze {
  background: linear-gradient(135deg, #CD7F32 0%, #B8860B 100%);
  color: white;
}

.rank-badge {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  font-size: 20px;
  font-weight: bold;
}

.rank-number {
  font-size: 16px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.user-count {
  font-size: 12px;
  opacity: 0.8;
}

.usage-bar {
  width: 100px;
}

.user-table {
  margin-bottom: 30px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 5px;
}

.count-number {
  font-weight: bold;
  color: #409eff;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.chart-container {
  height: 400px;
}

.chart {
  height: 100%;
  width: 100%;
}

:deep(.el-table) {
  border-radius: 6px;
}

:deep(.el-table .el-table__body tr:hover > td) {
  background-color: #f5f7fa;
}

:deep(.el-progress-bar__outer) {
  border-radius: 10px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 10px;
}
</style>

