import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:9000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    // 中间层返回格式: {"code":200,"data":{...}}
    const result = response.data
    if (result && result.code === 200) {
      return result.data
    }
    return result
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 统一API调用函数
const callApi = async (path, params = {}) => {
  const requestData = {
    path,
    queryDate: params.queryDate || null,
    startDate: params.startDate || null,
    endDate: params.endDate || null,
    bizSeq: params.bizSeq || null
  }
  
  // 移除null值
  Object.keys(requestData).forEach(key => {
    if (requestData[key] === null || requestData[key] === undefined) {
      delete requestData[key]
    }
  })
  
  return api.post('/api/proxy', requestData)
}

export const dashboardApi = {
  // 获取模板查询统计
  getTemplateQueryStats: (queryDate) => 
    callApi('/api/template-query/stats', { queryDate }),
  
  // 获取非模板查询统计
  getNonTemplateQueryStats: (queryDate) => 
    callApi('/api/non-template-query/stats', { queryDate }),
  
  // 获取模板查询错误统计
  getTemplateQueryErrors: (queryDate) => 
    callApi('/api/template-query/errors', { queryDate }),
  
  // 获取非模板查询错误统计
  getNonTemplateQueryErrors: (queryDate) => 
    callApi('/api/non-template-query/errors', { queryDate }),
  
  // 获取模板查询性能统计
  getTemplateQueryPerformance: (queryDate) => 
    callApi('/api/template-query/performance', { queryDate }),
  
  // 获取非模板查询性能统计
  getNonTemplateQueryPerformance: (queryDate) => 
    callApi('/api/non-template-query/performance', { queryDate }),
  
  // 获取步骤性能统计
  getStepPerformance: (queryDate) => 
    callApi('/api/step-performance', { queryDate }),
  
  // 获取渠道统计
  getChannelStats: (queryDate) => 
    callApi('/api/channel-stats', { queryDate }),
  
  // 获取免提单统计
  getNoTicketStats: (queryDate) => 
    callApi('/api/no-ticket-stats', { queryDate }),
  
  // 获取场景统计
  getScenarioStats: (queryDate) => 
    callApi('/api/scenario-stats', { queryDate }),
  
  // 获取用户统计
  getUserStats: (queryDate) => 
    callApi('/api/user-stats', { queryDate }),
  
  // 获取性能详细分析
  getPerformanceDetail: (bizSeq) => 
    callApi('/api/performance-detail', { bizSeq }),
  
  // 获取查询趋势（支持自定义日期范围）
  getWeeklyQueryTrend: (params = {}) => 
    callApi('/api/weekly-query-trend', params),
  
  // 获取各环节的耗时趋势（支持自定义日期范围）
  getWeeklyStepTrend: (params = {}) => 
    callApi('/api/weekly-step-trend', params),
  
  // 获取各渠道的查询趋势（支持自定义日期范围）
  getWeeklyChannelTrend: (params = {}) => 
    callApi('/api/weekly-channel-trend', params)
}

export default api

