import config from '../config';

const request = (url, method, data) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${config.baseUrl}${url}`,  // 使用 baseUrl
      method,
      data,
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else {
          reject(res.data || { message: '请求失败' });
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};

const api = {
  login: (data) => request(config.api.login, 'POST', data),
  getGroups: () => request(config.api.groups, 'GET'),
  getMembers: (groupId) => request(`${config.api.members}/${groupId}`, 'GET'),
  submitScore: (data) => request(config.api.score, 'POST', data)
};

export {
  api
};
