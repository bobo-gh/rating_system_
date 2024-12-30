// pages/member-list/member-list.js
import request from '../../utils/request'
import config from '../../config'

Page({
  data: {
    groupId: null,
    members: [],
    filteredMembers: [],
    loading: true,
    submitting: false,
    searchText: '',
    scoredCount: 0,
    totalCount: 0,
    progressPercent: 0,
    isAllScored: false,
    allSubmitted: false,
    hasUnsavedScores: false
  },

  onLoad(options) {
    if (options.groupId) {
      this.setData({
        groupId: options.groupId
      });
      this.fetchMembers(options.groupId);
    } else {
      wx.showToast({
        title: '参数错误',
        icon: 'none'
      });
      wx.navigateBack();
    }
  },

  // 获取成员列表
  async fetchMembers(groupId) {
    this.setData({ loading: true });
    try {
      const res = await request(`${config.api.members}/${groupId}`);
      console.log('获取到的成员数据:', res.data);
      
      const members = res.data.map(member => ({
        ...member,
        score: member.score === 0 || member.score ? member.score : null,
        tempScore: ''
      }));

      // 计算评分进度
      const scoredCount = members.filter(m => m.score !== null).length;
      const totalCount = members.length;
      const progressPercent = totalCount > 0 ? Math.round((scoredCount / totalCount) * 100) : 0;
      const isAllScored = scoredCount === totalCount;

      console.log('评分统计:', {
        scoredCount,
        totalCount,
        progressPercent,
        members
      });

      this.setData({
        members,
        filteredMembers: members,
        loading: false,
        scoredCount,
        totalCount,
        progressPercent,
        isAllScored,
        allSubmitted: isAllScored,
        hasUnsavedScores: false
      });
    } catch (error) {
      console.error('获取成员列表失败:', error);
      if (error.code === 401) {
        const app = getApp();
        app.logout();
      } else {
        wx.showToast({
          title: error.msg || '获取成员列表失败',
          icon: 'none'
        });
      }
      this.setData({ loading: false });
    }
  },

  // 搜索功能
  onSearch(e) {
    const searchText = e.detail.value.toLowerCase().trim();
    const filteredMembers = this.data.members.filter(member => 
      member.name.toLowerCase().includes(searchText) ||
      member.exam_number.toLowerCase().includes(searchText)
    );
    this.setData({
      searchText,
      filteredMembers
    });
  },

  // 输入分数
  onScoreInput(e) {
    const { index } = e.currentTarget.dataset;
    const score = e.detail.value.trim();
    
    const members = [...this.data.members];
    members[index].tempScore = score;
    
    // 检查是否有未保存的有效分数
    const hasUnsavedScores = members.some(m => {
      if (m.score !== null) return false;
      const tempScore = parseInt(m.tempScore);
      return !isNaN(tempScore) && tempScore >= 0 && tempScore <= 100;
    });

    this.setData({ 
      members,
      filteredMembers: this.getFilteredMembers(members),
      hasUnsavedScores
    });
  },

  // 获取过滤后的成员列表
  getFilteredMembers(members) {
    const searchText = this.data.searchText.toLowerCase().trim();
    if (!searchText) return members;
    
    return members.filter(member => 
      member.name.toLowerCase().includes(searchText) ||
      member.exam_number.toLowerCase().includes(searchText)
    );
  },

  // 提交全部评分
  async submitAllScores() {
    if (this.data.isAllScored || this.data.allSubmitted) {
      wx.showToast({
        title: '所有成员已评分',
        icon: 'none'
      });
      return;
    }

    // 获取所有需要提交的分数
    const scoresToSubmit = this.data.members
      .filter(m => m.score === null && m.tempScore !== '')
      .map(m => ({
        member_id: m.id,
        score: parseInt(m.tempScore)
      }));

    console.log('待提交的分数:', scoresToSubmit);

    if (scoresToSubmit.length === 0) {
      wx.showToast({
        title: '请输入评分',
        icon: 'none'
      });
      return;
    }

    // 验证分数
    const invalidScores = scoresToSubmit.some(item => {
      const score = item.score;
      return isNaN(score) || score < 0 || score > 100;
    });

    if (invalidScores) {
      wx.showToast({
        title: '请输入0-100的有效分数',
        icon: 'none'
      });
      return;
    }

    const that = this;
    wx.showModal({
      title: '确认提交',
      content: '评分提交后将无法修改，是否确认提交？',
      success: async (res) => {
        if (res.confirm) {
          that.setData({ submitting: true });
          try {
            console.log('开始提交分数:', {
              group_id: that.data.groupId,
              scores: scoresToSubmit
            });

            // 使用循环逐个提交分数
            for (const scoreData of scoresToSubmit) {
              await request(config.api.score, {
                method: 'POST',
                data: {
                  member_id: scoreData.member_id,
                  score: scoreData.score
                }
              });
            }

            // 更新所有成员状态
            const members = [...that.data.members];
            scoresToSubmit.forEach(item => {
              const index = members.findIndex(m => m.id === item.member_id);
              if (index !== -1) {
                members[index].score = item.score;
                members[index].tempScore = '';
              }
            });

            // 重新计算统计数据
            const scoredCount = members.filter(m => m.score !== null).length;
            const progressPercent = Math.round((scoredCount / that.data.totalCount) * 100);
            const isAllScored = scoredCount === that.data.totalCount;

            that.setData({
              members,
              filteredMembers: that.getFilteredMembers(members),
              scoredCount,
              progressPercent,
              isAllScored,
              allSubmitted: true,
              hasUnsavedScores: false,
              submitting: false
            });

            wx.showToast({
              title: '提交成功',
              icon: 'success'
            });

            // 如果全部评分完成，延迟返回上一页
            if (isAllScored) {
              setTimeout(() => {
                wx.navigateBack();
              }, 1500);
            }

          } catch (error) {
            console.error('提交评分失败:', error);
            wx.showToast({
              title: error.msg || '提交失败，请重试',
              icon: 'none',
              duration: 2000
            });
            that.setData({ 
              submitting: false,
              allSubmitted: false
            });
          }
        }
      }
    });
  }
});