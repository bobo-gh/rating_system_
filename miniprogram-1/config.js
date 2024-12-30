const config = {
  // API接口基础路径
  baseUrl: 'https://www.aibobo.tech/api',  // 生产环境使用HTTPS域名

  // API路由
  api: {
    login: '/login',
    groups: '/groups',
    members: '/members',
    score: '/score',
    submitAllScores: '/submit_all_scores'
  }
}

export default config 