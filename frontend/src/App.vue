<template>
  <div id="app">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h1>
            <el-icon><DataAnalysis /></el-icon>
            大乔工具运营数据管理台
          </h1>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { DataAnalysis } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    DataAnalysis
  }
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  margin: 0;
  padding: 0;
}

body {
  margin: 0;
  padding: 0;
  background-color: #f5f5f5;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  height: 70px !important;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0 30px;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 70px);
}

.el-container {
  height: 100vh;
}
</style>

