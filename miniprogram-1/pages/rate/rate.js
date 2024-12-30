import request from '../../utils/request'
import config from '../../config'

Page({
  data: {
    groupId: null,
    members: [],
    filteredMembers: [],
    scores: {},
    submitting: false,
    searchKey: '',
    scored: 0,
    total: 0,
    progress: 0,
    hasNewScores: false
  },

  onLoad(options) {
    console.log('评分页面加载，参数:', options);
    this.setData({
      groupId: options.groupId
    })
    this.loadMembers()
  },

  // 下拉刷新
  async onPullDownRefresh() {
    await this.loadMembers()
    wx.stopPullDownRefresh()
  },

  // 加载成员列表
  async loadMembers() {
    const { groupId } = this.data
    try {
      console.log('开始加载成员列表, groupId:', groupId);
      const res = await request(`${config.api.members}/${groupId}`);
      console.log('成员列表数据:', res.data);
      
      const members = res.data;
      
      // 计算评分进度
      const scored = members.filter(m => m.score !== null && m.score !== undefined).length;
      console.log('已评分人数:', scored);
      const total = members.length;
      const progress = total ? Math.round(scored / total * 100) : 0;

      this.setData({
        members,
        filteredMembers: members,
        scored,
        total,
        progress,
        hasNewScores: false
      });
      
      console.log('页面数据更新后:', this.data);
    } catch (err) {
      console.error('加载成员列表失败:', err);
      wx.showToast({
        title: err.msg || '加载失败',
        icon: 'none'
      })
    }
  },

  // 搜索
  onSearch(e) {
    const searchKey = e.detail.value.toLowerCase()
    const { members } = this.data
    
    const filteredMembers = searchKey ? members.filter(m => 
      m.exam_number.toLowerCase().includes(searchKey) ||
      m.name.toLowerCase().includes(searchKey)
    ) : members

    this.setData({
      searchKey,
      filteredMembers
    })
  },

  // 输入分数
  onScoreInput(e) {
    const { id } = e.currentTarget.dataset
    let score = e.detail.value
    
    // 限制分数范围
    if (score > 100) score = 100
    if (score < 0) score = 0
    
    this.setData({
      [`scores.${id}`]: score,
      hasNewScores: true
    })
  },

  // 提交所有评分
  async submitAllScores() {
    const { scores, members } = this.data
    const scoreEntries = Object.entries(scores)

    // 检查是否有分数需要提交
    if (!scoreEntries.length) {
      wx.showToast({
        title: '请先输入分数',
        icon: 'none'
      })
      return
    }

    // 验证所有分数
    for (const [id, score] of scoreEntries) {
      if (score === '' || score === undefined || isNaN(score)) {
        wx.showToast({
          title: '请完整填写所有分数',
          icon: 'none'
        })
        return
      }
      const scoreNum = parseInt(score)
      if (scoreNum < 0 || scoreNum > 100) {
        wx.showToast({
          title: '分数必须在0-100之间',
          icon: 'none'
        })
        return
      }
    }

    // 显示确认对话框
    wx.showModal({
      title: '确认提交',
      content: '评分提交后将无法修改，是否确认提交？',
      success: async (res) => {
        if (res.confirm) {
          await this.doSubmitScores(scoreEntries)
        }
      }
    })
  },

  // 执行提交评分
  async doSubmitScores(scoreEntries) {
    this.setData({ submitting: true })

    try {
      // 批量提交所有分数
      for (const [id, score] of scoreEntries) {
        const scoreNum = parseInt(score)
        await request(config.api.score, {
          method: 'POST',
          data: {
            member_id: id,
            score: scoreNum
          }
        })
      }

      wx.showToast({
        title: '评分提交成功',
        icon: 'success'
      })

      // 清除所有输入的分数
      this.setData({
        scores: {},
        hasNewScores: false
      })

      // 重新加载成员列表
      await this.loadMembers()

    } catch (err) {
      console.error('评分提交失败:', err)
      wx.showToast({
        title: err.msg || '评分提交失败',
        icon: 'none'
      })
    } finally {
      this.setData({ submitting: false })
    }
  }
}) 