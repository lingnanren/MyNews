const aiService = require('./src/services/ai/aiService');
const { News } = require('./src/models');

async function testAiSummary() {
  try {
    console.log('正在测试AI摘要服务...');
    
    // 统计未处理的新闻
    const unprocessedCount = await News.count({ where: { isProcessed: false } });
    console.log(`发现 ${unprocessedCount} 条未处理的新闻`);
    
    if (unprocessedCount > 0) {
      // 处理未处理的新闻摘要
      const result = await aiService.processUnprocessedNews(unprocessedCount);
      
      if (result.success) {
        console.log('✅ AI摘要处理完成！');
        console.log(`处理了 ${result.count} 条新闻`);
        
        // 验证处理结果
        const processedCount = await News.count({ where: { isProcessed: true } });
        const totalCount = await News.count();
        console.log(`\n处理状态：`);
        console.log(`- 已处理：${processedCount} 条`);
        console.log(`- 未处理：${totalCount - processedCount} 条`);
        console.log(`- 总计：${totalCount} 条`);
        
        // 查看处理后的新闻摘要
        const processedNews = await News.findAll({
          where: { isProcessed: true },
          order: [['updatedAt', 'DESC']],
          limit: 5
        });
        
        console.log('\n最新处理的5条新闻摘要：');
        for (const news of processedNews) {
          console.log(`[${news.category}] ${news.title}`);
          console.log(`摘要：${news.summary}`);
          console.log('---');
        }
        
      } else {
        console.error('❌ AI摘要处理失败:', result.error);
      }
    } else {
      console.log('⚠️  没有未处理的新闻需要摘要');
      
      // 查看已有的摘要
      const processedNews = await News.findAll({
        where: { isProcessed: true },
        order: [['updatedAt', 'DESC']],
        limit: 5
      });
      
      if (processedNews.length > 0) {
        console.log('\n已有的新闻摘要：');
        for (const news of processedNews) {
          console.log(`[${news.category}] ${news.title}`);
          console.log(`摘要：${news.summary}`);
          console.log('---');
        }
      }
    }
    
  } catch (error) {
    console.error('测试AI摘要服务时出错:', error.message);
  }
}

testAiSummary();