import request from '../../utils/request'
import config from '../../config'

Page({
  data: {
    userInfo: null
  },

  onLoad() {
    const app = getApp();
    const userInfo = wx.getStorageSync('userInfo');
    
    if (!userInfo) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }

    this.setData({
      userInfo
    });

    // 直接跳转到分组列表页
    wx.redirectTo({
      url: '/pages/group-list/group-list'
    });
  },

  // 登出
  handleLogout() {
    const app = getApp();
    app.logout();
  }
}); 