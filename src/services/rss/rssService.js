const Parser = require('rss-parser');
const { RssSource, News } = require('../../models');

const parser = new Parser();

class RssService {
  // 抓取单个RSS源
  async fetchRssSource(sourceId) {
    try {
      const source = await RssSource.findByPk(sourceId);
      if (!source || !source.isActive) {
        throw new Error('RSS源不存在或未激活');
      }
      
      const feed = await parser.parseURL(source.url);
      const newsItems = [];
      
      for (const item of feed.items) {
        // 检查是否已存在
        const existingNews = await News.findOne({
          where: { url: item.link }
        });
        
        if (!existingNews) {
          const news = await News.create({
            title: item.title || '',
            content: item.content || item.description || '',
            url: item.link || '',
            source: source.name,
            category: source.category,
            publishedAt: item.isoDate ? new Date(item.isoDate) : new Date()
          });
          newsItems.push(news);
        }
      }
      
      // 更新最后抓取时间
      await source.update({ lastFetched: new Date() });
      
      return { success: true, newsItems, count: newsItems.length };
    } catch (error) {
      console.error(`抓取RSS源失败 (${sourceId}):`, error);
      return { success: false, error: error.message };
    }
  }
  
  // 抓取所有激活的RSS源
  async fetchAllRssSources() {
    try {
      const sources = await RssSource.findAll({ where: { isActive: true } });
      const results = [];
      
      for (const source of sources) {
        const result = await this.fetchRssSource(source.id);
        results.push({ sourceId: source.id, sourceName: source.name, ...result });
      }
      
      return { success: true, results };
    } catch (error) {
      console.error('抓取所有RSS源失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 获取所有RSS源
  async getAllSources() {
    try {
      return await RssSource.findAll();
    } catch (error) {
      console.error('获取RSS源失败:', error);
      return [];
    }
  }
  
  // 添加RSS源
  async addSource(sourceData) {
    try {
      const [source, created] = await RssSource.findOrCreate({
        where: { url: sourceData.url },
        defaults: sourceData
      });
      
      if (!created) {
        throw new Error('RSS源已存在');
      }
      
      return { success: true, source };
    } catch (error) {
      console.error('添加RSS源失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 更新RSS源
  async updateSource(sourceId, updateData) {
    try {
      const source = await RssSource.findByPk(sourceId);
      if (!source) {
        throw new Error('RSS源不存在');
      }
      
      await source.update(updateData);
      return { success: true, source };
    } catch (error) {
      console.error('更新RSS源失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 删除RSS源
  async deleteSource(sourceId) {
    try {
      const source = await RssSource.findByPk(sourceId);
      if (!source) {
        throw new Error('RSS源不存在');
      }
      
      await source.destroy();
      return { success: true };
    } catch (error) {
      console.error('删除RSS源失败:', error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = new RssService();