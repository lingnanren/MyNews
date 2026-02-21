const rssService = require('./src/services/rss/rssService');
const { News } = require('./src/models');

async function fetchRssNews() {
  try {
    console.log('正在从RSS源获取真实新闻数据...');
    
    // 抓取所有激活的RSS源
    const result = await rssService.fetchAllRssSources();
    
    if (result.success) {
      console.log('✅ RSS新闻抓取完成！');
      console.log('\n抓取结果：');
      
      let totalNews = 0;
      for (const sourceResult of result.results) {
        console.log(`${sourceResult.sourceName}: ${sourceResult.count} 条新闻`);
        totalNews += sourceResult.count;
      }
      
      console.log(`\n总计获取 ${totalNews} 条新新闻`);
      
      // 验证数据库中的新闻数据
      const newsCount = await News.count();
      console.log(`\n数据库中共有 ${newsCount} 条新闻`);
      
      // 查看最新的10条新闻
      const latestNews = await News.findAll({
        order: [['publishedAt', 'DESC']],
        limit: 10
      });
      
      console.log('\n最新的10条新闻：');
      latestNews.forEach((news, index) => {
        console.log(`${index + 1}. [${news.category}] ${news.title}`);
        console.log(`   来源: ${news.source}`);
        console.log(`   发布时间: ${news.publishedAt ? news.publishedAt.toLocaleString() : '未知'}`);
        console.log(`   URL: ${news.url}`);
        console.log('');
      });
      
    } else {
      console.error('❌ RSS新闻抓取失败:', result.error);
    }
    
  } catch (error) {
    console.error('抓取RSS新闻时出错:', error.message);
  }
}

fetchRssNews();