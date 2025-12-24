<template>
  <el-card>
    <template #header v-if="showHeader">
      <div class="card-header-level-2">
        <span class="card-title-level-2">
          <el-icon><Share /></el-icon>
          {{ title }}
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="channel-content">
      <div v-if="!loading" class="channel-stats">
        <el-table
          :data="tableData"
          style="width: 100%"
          stripe
          border
        >
          <el-table-column prop="channel_name" label="渠道" width="120">
            <template #default="{ row }">
              <div class="channel-name">
                <el-icon><Platform /></el-icon>
                <span>{{ row.channel_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="总体" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="primary" class="count-tag">
                {{ row.total_count }}
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
          <el-table-column label="占比" width="100" align="center">
            <template #default="{ row }">
              <span class="percentage-text">
                {{ formatPercentage(row.percentage) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </el-card>
</template>

<script>
import { computed } from 'vue'
import { Share, Platform } from '@element-plus/icons-vue'

export default {
  name: 'ChannelStatsCard',
  components: {
    Share,
    Platform
  },
  props: {
    title: {
      type: String,
      required: true
    },
    channelData: {
      type: Object,
      default: () => ({
        member_stats: [],
        non_member_stats: []
      })
    },
    loading: {
      type: Boolean,
      default: false
    },
    showHeader: {
      type: Boolean,
      default: true
    }
  },
  setup(props) {
    // 固定的渠道顺序和名称映射
    const channelOrder = [
      { channel: 'DQ_QW', name: 'DQ_QW' },
      { channel: 'DQ_WEB', name: 'DQ_WEB' },
      { channel: 'DKK', name: 'DKK' },
      { channel: 'XQ_WEB', name: 'XQ_WEB' }
    ]

    // 处理表格数据
    const tableData = computed(() => {
      const memberStats = props.channelData.member_stats || []
      const nonMemberStats = props.channelData.non_member_stats || []

      // 创建映射表
      const memberMap = {}
      const nonMemberMap = {}

      memberStats.forEach(item => {
        memberMap[item.channel] = item.count
      })

      nonMemberStats.forEach(item => {
        nonMemberMap[item.channel] = item.count
      })

      // 按固定顺序生成基础表格数据
      const rows = channelOrder.map(ch => {
        const memberCount = memberMap[ch.channel] || 0
        const nonMemberCount = nonMemberMap[ch.channel] || 0
        const totalCount = memberCount + nonMemberCount

        return {
          channel: ch.channel,
          channel_name: ch.name,
          total_count: totalCount,
          member_count: memberCount,
          non_member_count: nonMemberCount
        }
      })

      const grandTotal = rows.reduce((sum, row) => sum + row.total_count, 0)
      const totalMember = rows.reduce((sum, row) => sum + row.member_count, 0)
      const totalNonMember = rows.reduce((sum, row) => sum + row.non_member_count, 0)

      const rowsWithPercentage = rows.map(row => ({
        ...row,
        percentage: grandTotal ? (row.total_count / grandTotal) * 100 : 0
      }))

      const totalRow = {
        channel: 'TOTAL',
        channel_name: '合计',
        total_count: grandTotal,
        member_count: totalMember,
        non_member_count: totalNonMember,
        percentage: grandTotal ? 100 : 0
      }

      // 合计行在最上方
      return [totalRow, ...rowsWithPercentage]
    })

    const formatPercentage = (value) => {
      if (!Number.isFinite(value)) {
        return '-'
      }
      if (value === 0) {
        return '0%'
      }
      return `${value.toFixed(1)}%`
    }

    return {
      tableData,
      formatPercentage
    }
  }
}
</script>

<style scoped>
@import '@/styles/card-header.css';

.channel-content {
  min-height: 200px;
}

.channel-name {
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

.percentage-text {
  font-size: 14px;
  font-weight: 500;
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
