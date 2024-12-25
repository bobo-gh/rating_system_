import request from '../../utils/request'
import config from '../../config'

Page({
  data: {
    groups: []
  },

  onLoad() {
    this.loadGroups()
  },

  // 下拉刷新
  async onPullDownRefresh() {
    await this.loadGroups()
    wx.stopPullDownRefresh()
  },

  // 加载分组列表
  async loadGroups() {
    try {
      const res = await request(config.api.groups)
      this.setData({
        groups: res.data
      })
    } catch (err) {
      wx.showToast({
        title: err.msg || '加载失败',
        icon: 'none'
      })
    }
  },

  // 进入评分页面
  goToRate(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/rate/rate?groupId=${id}`
    })
  }
}) 