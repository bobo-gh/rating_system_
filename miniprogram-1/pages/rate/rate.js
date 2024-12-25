import request from '../../utils/request'
import config from '../../config'

Page({
  data: {
    groupId: null,
    members: [],
    filteredMembers: [],
    scores: {},
    submitting: {},
    searchKey: '',
    scored: 0,
    total: 0,
    progress: 0
  },

  onLoad(options) {
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
      const res = await request(`${config.api.members}/${groupId}`)
      const members = res.data
      
      // 计算评分进度
      const scored = members.filter(m => m.score).length
      const total = members.length
      const progress = total ? Math.round(scored / total * 100) : 0

      this.setData({
        members,
        filteredMembers: members,
        scored,
        total,
        progress
      })
    } catch (err) {
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
      [`scores.${id}`]: score
    })
  },

  // 提交评分
  async submitScore(e) {
    const { id } = e.currentTarget.dataset
    const score = this.data.scores[id]

    if (!score) {
      wx.showToast({
        title: '请输入分数',
        icon: 'none'
      })
      return
    }

    this.setData({
      [`submitting.${id}`]: true
    })

    try {
      await request(config.api.score, {
        method: 'POST',
        data: {
          member_id: id,
          score: parseInt(score)
        }
      })

      wx.showToast({
        title: '评分成功'
      })

      // 清除输入的分数
      this.setData({
        [`scores.${id}`]: ''
      })

      // 重新加载成员列表
      this.loadMembers()

    } catch (err) {
      wx.showToast({
        title: err.msg || '评分失败',
        icon: 'none'
      })
    } finally {
      this.setData({
        [`submitting.${id}`]: false
      })
    }
  }
}) 