// app.js
App({
  globalData: {
    userInfo: null,
    isLoggedIn: false
  },

  onLaunch() {
    // 检查登录状态
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    
    if (token && userInfo) {
      this.globalData.isLoggedIn = true;
      this.globalData.userInfo = userInfo;
    } else {
      // 清除可能存在的无效数据
      wx.removeStorageSync('token');
      wx.removeStorageSync('userInfo');
      
      // 跳转到登录页
      wx.reLaunch({
        url: '/pages/login/login'
      });
    }
  },

  // 登录成功后调用
  login(token, userInfo) {
    this.globalData.isLoggedIn = true;
    this.globalData.userInfo = userInfo;
    wx.setStorageSync('token', token);
    wx.setStorageSync('userInfo', userInfo);
  },

  // 登出
  logout() {
    this.globalData.isLoggedIn = false;
    this.globalData.userInfo = null;
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    wx.reLaunch({
      url: '/pages/login/login'
    });
  }
}); 