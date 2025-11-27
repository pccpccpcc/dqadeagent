<template>
  <el-card>
    <template #header>
      <div class="card-header-level-1">
        <span class="card-title-level-1">
          <el-icon><DataAnalysis /></el-icon>
          总体明细数据
        </span>
      </div>
    </template>
    
    <div v-loading="loading" class="stats-content">
      <!-- 1. 总体统计 -->
      <div class="section">
        <div class="section-title">
          <el-icon><TrendCharts /></el-icon>
          总体查询统计
        </div>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item total">
              <div class="stat-number">{{ stats.total_count || 0 }}</div>
              <div class="stat-label">总查询数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item success">
              <div class="stat-number">{{ stats.success_count || 0 }}</div>
              <div class="stat-label">总成功数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item failure">
              <div class="stat-number">{{ stats.failure_count || 0 }}</div>
              <div class="stat-label">总失败数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item rate">
              <div class="stat-number">{{ stats.success_rate || 0 }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 2. 总体错误统计 -->
      <div class="section">
        <div class="section-title">
          <el-icon><Warning /></el-icon>
          总体错误统计
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="error-card business-error">
              <div class="error-header">
                <el-icon><DocumentChecked /></el-icon>
                业务错误
              </div>
              <div class="error-content">
                <div class="error-item">
                  <span class="error-label">错误数量：</span>
                  <span class="error-value">{{ stats.business_error_count || 0 }}</span>
                </div>
                <div class="error-item">
                  <span class="error-label">业务成功率：</span>
                  <span class="error-value success-rate">{{ stats.business_success_rate || 0 }}%</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="error-card system-error">
              <div class="error-header">
                <el-icon><Monitor /></el-icon>
                系统错误
              </div>
              <div class="error-content">
                <div class="error-item">
                  <span class="error-label">错误数量：</span>
                  <span class="error-value">{{ stats.system_error_count || 0 }}</span>
                </div>
                <div class="error-item">
                  <span class="error-label">系统成功率：</span>
                  <span class="error-value success-rate">{{ stats.system_success_rate || 0 }}%</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 3. Agent子系统统计 -->
      <div class="section">
        <div class="section-title">
          <el-icon><Service /></el-icon>
          Agent子系统错误统计
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="subsystem-card agent-business">
              <div class="subsystem-header">业务错误</div>
              <div class="subsystem-content">
                <div class="subsystem-item">
                  <span class="subsystem-label">错误数量：</span>
                  <span class="subsystem-value">{{ stats.agent_business_error_count || 0 }}</span>
                </div>
                <div class="subsystem-item">
                  <span class="subsystem-label">业务成功率：</span>
                  <span class="subsystem-value success-rate">{{ stats.agent_business_success_rate || 0 }}%</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="subsystem-card agent-system">
              <div class="subsystem-header">系统错误</div>
              <div class="subsystem-content">
                <div class="subsystem-item">
                  <span class="subsystem-label">错误数量：</span>
                  <span class="subsystem-value">{{ stats.agent_system_error_count || 0 }}</span>
                </div>
                <div class="subsystem-item">
                  <span class="subsystem-label">系统成功率：</span>
                  <span class="subsystem-value success-rate">{{ stats.agent_system_success_rate || 0 }}%</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 4. DS子系统统计 -->
      <div class="section">
        <div class="section-title">
          <el-icon><Connection /></el-icon>
          DS子系统错误统计
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="subsystem-card ds-business">
              <div class="subsystem-header">业务错误</div>
              <div class="subsystem-content">
                <div class="subsystem-item">
                  <span class="subsystem-label">错误数量：</span>
                  <span class="subsystem-value">{{ stats.ds_business_error_count || 0 }}</span>
                </div>
                <div class="subsystem-item">
                  <span class="subsystem-label">业务成功率：</span>
                  <span class="subsystem-value success-rate">{{ stats.ds_business_success_rate || 0 }}%</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="subsystem-card ds-system">
              <div class="subsystem-header">系统错误</div>
              <div class="subsystem-content">
                <div class="subsystem-item">
                  <span class="subsystem-label">错误数量：</span>
                  <span class="subsystem-value">{{ stats.ds_system_error_count || 0 }}</span>
                </div>
                <div class="subsystem-item">
                  <span class="subsystem-label">系统成功率：</span>
                  <span class="subsystem-value success-rate">{{ stats.ds_system_success_rate || 0 }}%</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

    </div>
  </el-card>
</template>

<script>
import { 
  DataAnalysis, 
  TrendCharts, 
  Warning, 
  DocumentChecked, 
  Monitor, 
  Service, 
  Connection
} from '@element-plus/icons-vue'

export default {
  name: 'ComprehensiveStatsCard',
  components: {
    DataAnalysis,
    TrendCharts,
    Warning,
    DocumentChecked,
    Monitor,
    Service,
    Connection
  },
  props: {
    stats: {
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
@import '@/styles/card-header.css';

.stats-content {
  min-height: 300px;
}

.section {
  margin-bottom: 30px;
}

.section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #EBEEF5;
}

/* 总体统计样式 */
.stat-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-item.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-item.success {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  color: white;
}

.stat-item.failure {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #333;
}

.stat-item.rate {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #333;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* 错误卡片样式 */
.error-card {
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.error-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.1);
}

.error-card.business-error {
  background: linear-gradient(135deg, #FFF5E6 0%, #FFE6CC 100%);
  border-left: 4px solid #E6A23C;
}

.error-card.system-error {
  background: linear-gradient(135deg, #FFE6E6 0%, #FFCCCC 100%);
  border-left: 4px solid #F56C6C;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
}

.error-content {
  padding-left: 10px;
}

.error-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
}

.error-label {
  color: #606266;
}

.error-value {
  font-weight: 500;
  color: #303133;
}

.error-value.success-rate {
  color: #67C23A;
  font-weight: bold;
}

/* 子系统卡片样式 */
.subsystem-card {
  border-radius: 8px;
  padding: 15px;
  background: #F5F7FA;
  border: 1px solid #DCDFE6;
  transition: all 0.3s ease;
}

.subsystem-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
}

.subsystem-card.agent-business {
  border-left: 3px solid #409EFF;
}

.subsystem-card.agent-system {
  border-left: 3px solid #909399;
}

.subsystem-card.ds-business {
  border-left: 3px solid #E6A23C;
}

.subsystem-card.ds-system {
  border-left: 3px solid #F56C6C;
}

.subsystem-header {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 10px;
}

.subsystem-content {
  padding-left: 5px;
}

.subsystem-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.subsystem-label {
  color: #606266;
}

.subsystem-value {
  font-weight: 500;
  color: #303133;
}

.subsystem-value.success-rate {
  color: #67C23A;
  font-weight: bold;
}
</style>

