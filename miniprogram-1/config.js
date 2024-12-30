const config = {
  // API接口基础路径
  baseUrl: 'http://111.230.96.110:4262/api',  // 使用IP地址和端口

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