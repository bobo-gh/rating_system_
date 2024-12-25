const { api } = require('../../utils/request');
const { checkLogin } = require('../../utils/auth');

Page({
  data: {
    groupId: null,
    members: [],
    currentMember: null,
    showScoreModal: false,
    score: '',
    loading: true
  },

  onLoad(options) {
    if (!checkLogin()) return;
    this.setData({
      groupId: options.groupId
    });
    this.fetchMembers();
  },

  onShow() {
    if (!checkLogin()) return;
    if (this.data.groupId) {
      this.fetchMembers();
    }
  },

  // 获取成员列表
  async fetchMembers() {
    this.setData({ loading: true });
    try {
      const res = await api.getGroupMembers(this.data.groupId);
      this.setData({
        members: res.data,
        loading: false
      });
    } catch (error) {
      if (error.code === 401) {
        // token失效，跳转到登录页
        wx.reLaunch({
          url: '/pages/login/login'
        });
      } else {
        wx.showToast({
          title: error.msg || '获取成员列表失败',
          icon: 'none'
        });
      }
      this.setData({ loading: false });
    }
  },

  // 打开评分弹窗
  openScoreModal(e) {
    const { memberId } = e.currentTarget.dataset;
    const currentMember = this.data.members.find(m => m.id === memberId);
    
    if (currentMember.score) {
      wx.showToast({
        title: '已经评过分了',
        icon: 'none'
      });
      return;
    }

    this.setData({
      currentMember,
      showScoreModal: true,
      score: ''
    });
  },

  // 关闭评分弹窗
  closeScoreModal() {
    this.setData({
      showScoreModal: false,
      currentMember: null,
      score: ''
    });
  },

  // 输入分数
  onScoreInput(e) {
    this.setData({
      score: e.detail.value
    });
  },

  // 提交评分
  async submitScore() {
    if (!checkLogin()) return;
    const { score, currentMember } = this.data;
    
    if (!score) {
      wx.showToast({
        title: '请输入分数',
        icon: 'none'
      });
      return;
    }

    const scoreNum = parseInt(score);
    if (isNaN(scoreNum) || scoreNum < 0 || scoreNum > 100) {
      wx.showToast({
        title: '分数必须在0-100之间',
        icon: 'none'
      });
      return;
    }

    try {
      await api.submitScore({
        member_id: currentMember.id,
        score: scoreNum
      });
      
      // 刷新成员列表
      await this.fetchMembers();
      
      this.closeScoreModal();
      wx.showToast({
        title: '评分成功',
        icon: 'success'
      });
    } catch (error) {
      if (error.code === 401) {
        // token失效，跳转到登录页
        wx.reLaunch({
          url: '/pages/login/login'
        });
      } else {
        wx.showToast({
          title: error.msg || '提交评分失败',
          icon: 'none'
        });
      }
    }
  }
}); 