import request from '../../utils/request'
import config from '../../config'

Page({
  data: {
    groups: [],
    loading: true
  },

  onLoad() {
    this.fetchGroups();
  },

  onShow() {
    // 每次显示页面时刷新数据
    this.fetchGroups();
  },

  // 获取分组列表
  async fetchGroups() {
    this.setData({ loading: true });
    try {
      const res = await request(config.api.groups);
      console.log('获取到的分组数据:', res.data);
      
      this.setData({
        groups: res.data,
        loading: false
      });
    } catch (error) {
      console.error('获取分组失败:', error);
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
    if (!groupId) {
      wx.showToast({
        title: '分组信息错误',
        icon: 'none'
      });
      return;
    }

    wx.navigateTo({
      url: `/pages/member-list/member-list?groupId=${groupId}`
    });
  },

  // 登出
  handleLogout() {
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