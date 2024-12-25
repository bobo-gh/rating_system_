const { api } = require('../../utils/request');

Page({
  data: {
    groups: [],
    loading: true,
    userInfo: null
  },

  onLoad() {
    const app = getApp();
    if (!app.globalData.isLoggedIn) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }

    this.setData({
      userInfo: app.globalData.userInfo
    });
    this.fetchGroups();
  },

  onShow() {
    const app = getApp();
    if (!app.globalData.isLoggedIn) {
      wx.reLaunch({
        url: '/pages/login/login'
      });
      return;
    }
    // 每次显示页面时刷新数据
    this.fetchGroups();
  },

  // 获取分组列表
  async fetchGroups() {
    this.setData({ loading: true });
    try {
      const res = await api.getGroups();
      this.setData({
        groups: res.data,
        loading: false
      });
    } catch (error) {
      if (error.code === 401) {
        // token失效，登出并跳转到登录页
        const app = getApp();
        app.logout();
      } else {
        wx.showToast({
          title: error.msg || '获取分组失败',
          icon: 'none'
        });
      }
      this.setData({ loading: false });
    }
  },

  // 跳转到成员列表页面
  goToMembers(e) {
    const { groupId } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/members/members?groupId=${groupId}`
    });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          const app = getApp();
          app.logout();
        }
      }
    });
  }
}); 