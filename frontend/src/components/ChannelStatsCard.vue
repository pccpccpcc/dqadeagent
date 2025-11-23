<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span class="card-title">
          <el-icon><Share /></el-icon>
          {{ title }}
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="channel-content">
      <div v-if="!loading && channels.length === 0" class="no-data">
        <el-empty description="暂无渠道数据" />
      </div>
      
      <div v-else-if="!loading" class="channel-stats">
        <!-- 渠道统计列表 -->
        <div class="channel-list">
          <div 
            v-for="(channel, index) in channels" 
            :key="channel.channel"
            class="channel-item"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <div class="channel-info">
              <div class="channel-name">
                <el-icon><Platform /></el-icon>
                {{ channel.channel_name }}
              </div>
              <div class="channel-code">{{ channel.channel }}</div>
            </div>
            <div class="channel-count">
              <span class="count-number">{{ channel.count }}</span>
              <span class="count-label">次查询</span>
            </div>
          </div>
        </div>
        
        <!-- 渠道分布图表 -->
        <div class="chart-container" v-if="chartData.length > 0">
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
    channels: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    // 图表数据
    const chartData = computed(() => {
      return props.channels.map(channel => ({
        name: channel.channel_name,
        value: channel.count
      }))
    })

    // 图表配置
    const chartOption = computed(() => {
      const colors = ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE', '#3BA272', '#FC8452']
      
      return {
        title: {
          text: '渠道查询分布',
          left: 'center',
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          bottom: '0',
          left: 'center',
          type: 'scroll'
        },
        color: colors,
        series: [
          {
            name: '渠道查询',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '45%'],
            data: chartData.value,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              formatter: '{b}\n{c}次'
            }
          }
        ]
      }
    })

    return {
      chartData,
      chartOption
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

.channel-content {
  min-height: 400px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.channel-list {
  margin-bottom: 20px;
}

.channel-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  margin-bottom: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease;
}

.channel-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.channel-info {
  flex: 1;
}

.channel-name {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.channel-code {
  font-size: 12px;
  color: #666;
  font-family: 'Monaco', 'Consolas', monospace;
}

.channel-count {
  text-align: right;
}

.count-number {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  display: block;
}

.count-label {
  font-size: 12px;
  color: #666;
}

.chart-container {
  height: 300px;
}

.chart {
  height: 100%;
  width: 100%;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

