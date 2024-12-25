App({
  globalData: {
    userInfo: null,
    token: null
  },

  onLaunch() {
    // 检查是否有存储的token
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
    }
  },

  // 检查登录状态
  checkLogin() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.redirectTo({
        url: '/pages/login/login'
      })
      return false
    }
    return true
  },

  // 清除登录状态
  clearLogin() {
    this.globalData.userInfo = null
    this.globalData.token = null
    wx.removeStorageSync('token')
    wx.redirectTo({
      url: '/pages/login/login'
    })
  }
}) 