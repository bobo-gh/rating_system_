const config = {
  // API接口基础路径 - 开发环境
  baseUrl: 'http://localhost:6515',
  
  // API接口基础路径 - 生产环境
  // baseUrl: 'https://your-domain.com',
  
  // API路由
  api: {
    login: '/api/login',
    groups: '/api/groups',
    members: '/api/members',
    score: '/api/score'
  }
}

export default config 