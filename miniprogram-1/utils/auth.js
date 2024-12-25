// 检查登录状态
const checkLogin = () => {
  const token = wx.getStorageSync('token');
  if (!token) {
    wx.reLaunch({
      url: '/pages/login/login'
    });
    return false;
  }
  return true;
};

module.exports = {
  checkLogin
}; 