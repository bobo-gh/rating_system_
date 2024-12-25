import config from '../config'

// 请求封装
const request = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    wx.showLoading({ title: '加载中...' })
    
    // 获取存储的token
    const token = wx.getStorageSync('token')
    
    wx.request({
      url: `${config.baseUrl}${url}`,
      ...options,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token,
        ...options.header
      },
      success: (res) => {
        if (res.data.code === 401) {
          // token过期,跳转登录
          wx.removeStorageSync('token')
          wx.redirectTo({
            url: '/pages/login/login'
          })
          reject(res.data)
        } else if (res.data.code === 0) {
          resolve(res.data)
        } else {
          reject(res.data)
        }
      },
      fail: reject,
      complete: () => {
        wx.hideLoading()
      }
    })
  })
}

export default request 