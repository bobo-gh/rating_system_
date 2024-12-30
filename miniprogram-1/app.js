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
      this.globalData.userInfo = userInfo;
      this.globalData.isLoggedIn = true;
    }
  },

  login(token, userInfo) {
    this.globalData.userInfo = userInfo;
    this.globalData.isLoggedIn = true;
    wx.setStorageSync('token', token);
    wx.setStorageSync('userInfo', userInfo);
  },

  logout() {
    this.globalData.userInfo = null;
    this.globalData.isLoggedIn = false;
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    wx.reLaunch({
      url: '/pages/login/login'
    });
  }
}); 