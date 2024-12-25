const { api } = require('../../utils/request');

Page({
  data: {
    username: '',
    password: '',
    loading: false
  },

  onLoad() {
    // 检查是否已登录
    const app = getApp();
    if (app.globalData.isLoggedIn) {
      wx.reLaunch({
        url: '/pages/index/index'
      });
    }
  },

  // 输入用户名
  onUsernameInput(e) {
    this.setData({
      username: e.detail.value
    });
  },

  // 输入密码
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },

  // 提交登录
  async onLogin() {
    const { username, password } = this.data;
    
    if (!username || !password) {
      wx.showToast({
        title: '请输入用户名和密码',
        icon: 'none'
      });
      return;
    }

    this.setData({ loading: true });

    try {
      const res = await api.login({
        username,
        password
      });

      // 判断是否是评委
      if (res.data.role !== 'judge') {
        wx.showToast({
          title: '只有评委可以登录',
          icon: 'none'
        });
        return;
      }

      // 保存登录状态
      const app = getApp();
      app.login(res.data.token, {
        id: res.data.user_id,
        username: res.data.username,
        role: res.data.role
      });
      
      // 显示成功提示
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500
      });

      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        wx.reLaunch({
          url: '/pages/index/index'
        });
      }, 1500);

    } catch (err) {
      wx.showToast({
        title: err.msg || '登录失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
  }
}); 