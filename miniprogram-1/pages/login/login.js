import request from '../../utils/request'
import config from '../../config'

Page({
  data: {
    username: '',
    password: '',
    loading: false
  },

  onLoad() {
    // 检查是否已登录
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    if (token && userInfo) {
      wx.reLaunch({
        url: '/pages/index/index'
      });
    }
  },

  // 输入用户名
  onUsernameInput(e) {
    this.setData({
      username: e.detail.value.trim()
    });
  },

  // 输入密码
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value.trim()
    });
  },

  // 登录
  async onLogin() {
    try {
      const { username, password } = this.data;
      
      // 表单验证
      if (!username || !password) {
        wx.showToast({
          title: '请输入用户名和密码',
          icon: 'none',
          duration: 2000
        });
        return;
      }

      // 显示加载中
      this.setData({ loading: true });
      wx.showLoading({
        title: '登录中...',
        mask: true
      });

      console.log('开始登录请求');
      console.log('请求数据:', { username, password });

      const res = await request(config.api.login, {
        method: 'POST',
        data: {
          username,
          password
        }
      });

      console.log('登录响应:', res);

      if (res.code === 0 && res.data) {
        // 保存登录信息
        try {
          const app = getApp();
          app.login(res.data.token, {
            id: res.data.user_id,
            username: res.data.username,
            role: res.data.role
          });
          
          console.log('登录信息已保存');

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
        } catch (storageErr) {
          console.error('保存登录信息失败:', storageErr);
          throw new Error('登录信息保存失败，请重试');
        }
      } else {
        throw new Error(res.msg || '登录失败');
      }
    } catch (err) {
      console.error('登录错误:', err);
      wx.showToast({
        title: err.msg || '登录失败，请重试',
        icon: 'none',
        duration: 2000
      });
    } finally {
      // 隐藏加载提示
      this.setData({ loading: false });
      wx.hideLoading();
    }
  }
}); 