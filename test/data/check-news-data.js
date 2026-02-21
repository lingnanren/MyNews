const { sequelize, News, RssSource, User } = require('./src/models');

async function checkNewsData() {
  try {
    console.log('正在检查测试新闻数据...');
    
    // 检查用户数据
    const users = await User.findAll();
    console.log('用户数据:', users.length, '个用户');
    users.forEach(user => {
      console.log(`- 用户: ${user.name}, 邮箱: ${user.email}`);
    });
    
    // 检查RSS源数据
    const rssSources = await RssSource.findAll();
    console.log('\nRSS源数据:', rssSources.length, '个源');
    rssSources.forEach(source => {
      console.log(`- ${source.name} (${source.category}): ${source.url}`);
    });
    
    // 检查新闻数据
    const news = await News.findAll({
      order: [['publishedAt', 'DESC']],
      limit: 10
    });
    console.log('\n新闻数据:', news.length, '条新闻');
    news.forEach(item => {
      console.log(`- ${item.title} (${item.category}) - ${item.publishedAt}`);
    });
    
    console.log('\n数据检查完成！');
    
  } catch (error) {
    console.error('检查数据时出错:', error.message);
  } finally {
    await sequelize.close();
  }
}

checkNewsData();