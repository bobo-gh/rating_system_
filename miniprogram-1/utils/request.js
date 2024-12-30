import config from '../config';

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const request = (url, options = {}, retryCount = 0) => {
  return new Promise((resolve, reject) => {
    // 获取存储的token
    const token = wx.getStorageSync('token');
    console.log('请求URL:', `${config.baseUrl}${url}`);
    console.log('请求方法:', options.method || 'GET');
    console.log('请求数据:', options.data);
    console.log('当前Token:', token);
    console.log('重试次数:', retryCount);

    const header = {
      'Content-Type': 'application/json'
    };

    // 如果有token，添加到Authorization头中
    if (token) {
      header.Authorization = `Bearer ${token}`;
    }

    console.log('请求头:', header);
    
    wx.request({
      url: `${config.baseUrl}${url}`,
      method: options.method || 'GET',
      data: options.data,
      header,
      enableHttp2: false,  // 关闭 HTTP2
      enableQuic: false,   // 关闭 QUIC
      timeout: 10000,      // 设置超时为10秒
      success: (res) => {
        console.log('响应状态码:', res.statusCode);
        console.log('响应数据:', res.data);
        if (res.statusCode === 200) {
          if (res.data.code === 0) {
            resolve(res.data);
          } else {
            console.error('业务错误:', res.data.msg);
            reject(res.data);
          }
        } else if (res.statusCode === 401) {
          console.log('Token无效，清除登录状态');
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          const app = getApp();
          app.logout();
          reject({ msg: '请重新登录' });
        } else {
          console.error('HTTP错误:', res.statusCode);
          reject(res.data || { msg: '请求失败' });
        }
      },
      fail: async (err) => {
        console.error('请求失败:', err);
        if (err.errMsg) {
          console.error('错误信息:', err.errMsg);
        }

        if (retryCount < MAX_RETRIES) {
          console.log(`第 ${retryCount + 1} 次重试`);
          await sleep(RETRY_DELAY);
          try {
            const result = await request(url, options, retryCount + 1);
            resolve(result);
          } catch (retryErr) {
            reject(retryErr);
          }
        } else {
          reject({
            msg: '网络请求失败，请检查网络连接'
          });
        }
      }
    });
  });
};

export default request;
