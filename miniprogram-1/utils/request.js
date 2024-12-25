const BASE_URL = 'http://111.230.96.110:4262/api'; // 替换为你的实际API地址

const request = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token');
    
    wx.request({
      url: `${BASE_URL}${url}`,
      ...options,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token,
        ...options.header,
      },
      success: (res) => {
        if (res.data.code === 0) {
          resolve(res.data);
        } else if (res.data.code === 401) {
          // token过期或无效，跳转到登录页
          wx.removeStorageSync('token');
          wx.redirectTo({
            url: '/pages/login/login'
          });
          reject(res.data);
        } else {
          wx.showToast({
            title: res.data.msg || '请求失败',
            icon: 'none'
          });
          reject(res.data);
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

// API方法
const api = {
  // 登录
  login: (data) => {
    return request('/login', {
      method: 'POST',
      data
    });
  },

  // 获取分组列表
  getGroups: () => {
    return request('/groups', {
      method: 'GET'
    });
  },

  // 获取指定分组的成员列表
  getGroupMembers: (groupId) => {
    return request(`/members/${groupId}`, {
      method: 'GET'
    });
  },

  // 提交评分
  submitScore: (data) => {
    return request('/score', {
      method: 'POST',
      data
    });
  }
};

module.exports = {
  request,
  api
}; 