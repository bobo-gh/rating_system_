const config = {
  // API接口基础路径 - 生产环境
  baseUrl: 'https://your-project.vercel.app',  // 替换为你的 Vercel 域名
  
  // API路由
  api: {
    login: '/api/login',
    groups: '/api/groups',
    members: '/api/members',
    score: '/api/score'
  }
}

export default config 