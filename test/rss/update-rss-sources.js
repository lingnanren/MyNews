const { RssSource } = require('./src/models');

async function updateRssSources() {
  try {
    console.log('正在更新RSS源配置为可靠的公共RSS源...');
    
    // 新的RSS源配置
    const newSources = [
      {
        id: 1,
        name: '财经新闻',
        url: 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL+MSFT+GOOGL&region=US&lang=en-US',
        category: '财经',
        isActive: true
      },
      {
        id: 2,
        name: '军事新闻',
        url: 'https://feeds.bbci.co.uk/news/world/rss.xml',
        category: '军事',
        isActive: true
      },
      {
        id: 3,
        name: '生活资讯',
        url: 'https://www.buzzfeed.com/world.xml',
        category: '生活',
        isActive: true
      },
      {
        id: 4,
        name: '科技新闻',
        url: 'https://feeds.arstechnica.com/arstechnica/index',
        category: '科技',
        isActive: true
      }
    ];
    
    for (const sourceData of newSources) {
      try {
        // 查找并更新现有源
        const existingSource = await RssSource.findByPk(sourceData.id);
        if (existingSource) {
          await existingSource.update(sourceData);
          console.log(`✅ 更新RSS源: ${sourceData.name}`);
        } else {
          // 创建新源
          await RssSource.create(sourceData);
          console.log(`✅ 创建RSS源: ${sourceData.name}`);
        }
      } catch (error) {
        console.error(`❌ 处理RSS源 ${sourceData.name} 时出错:`, error.message);
      }
    }
    
    console.log('\nRSS源配置更新完成！');
    console.log('\n新的RSS源配置:');
    const sources = await RssSource.findAll();
    sources.forEach(source => {
      console.log(`- ${source.name} (${source.category}): ${source.url}`);
    });
    
  } catch (error) {
    console.error('更新RSS源配置时出错:', error.message);
  }
}

updateRssSources();