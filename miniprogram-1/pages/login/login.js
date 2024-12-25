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
    const token = wx.getStorageSync('token')
    if (token) {
      wx.reLaunch({
        url: '/pages/group-list/group-list'
      })
    }
  },

  // 输入用户名
  onUsernameInput(e) {
    this.setData({
      username: e.detail.value
    })
  },

  // 输入密码
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    })
  },

  // 提交登录
  async onSubmit() {
    const { username, password } = this.data
    
    if (!username || !password) {
      wx.showToast({
        title: '请输入用户名和密码',
        icon: 'none'
      })
      return
    }

    this.setData({ loading: true })

    try {
      const res = await request(config.api.login, {
        method: 'POST',
        data: {
          username,
          password
        }
      })

      // 保存token
      wx.setStorageSync('token', res.data.token)
      
      // 跳转到分组列表
      wx.reLaunch({
        url: '/pages/group-list/group-list'
      })

    } catch (err) {
      wx.showToast({
        title: err.msg || '登录失败',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  }
}) 