const Parser = require('rss-parser');
const { RssSource } = require('./src/models');

const parser = new Parser();

async function testRssSources() {
  try {
    console.log('正在验证RSS源配置...');
    
    // 获取所有RSS源
    const sources = await RssSource.findAll();
    console.log(`发现 ${sources.length} 个RSS源配置`);
    
    for (const source of sources) {
      console.log(`\n测试RSS源: ${source.name} (${source.category})`);
      console.log(`URL: ${source.url}`);
      
      try {
        // 测试URL是否可访问
        const feed = await parser.parseURL(source.url);
        console.log(`✅ 成功获取RSS内容！`);
        console.log(`- 标题: ${feed.title}`);
        console.log(`- 条目数: ${feed.items.length}`);
        
        if (feed.items.length > 0) {
          console.log(`- 最新新闻: ${feed.items[0].title}`);
          console.log(`- 发布时间: ${feed.items[0].isoDate || '未知'}`);
        }
        
        // 标记为可访问
        await source.update({ isActive: true });
        console.log(`✅ 已激活RSS源`);
        
      } catch (error) {
        console.error(`❌ 测试失败: ${error.message}`);
        console.log(`⚠️  可能的原因:`);
        console.log(`1. 网络连接问题`);
        console.log(`2. URL格式不正确`);
        console.log(`3. RSS源服务不可用`);
        console.log(`4. 防火墙限制`);
        
        // 标记为不可访问
        await source.update({ isActive: false });
        console.log(`⚠️  已禁用RSS源`);
      }
    }
    
    console.log('\nRSS源测试完成！');
    
  } catch (error) {
    console.error('验证RSS源配置时出错:', error.message);
  }
}

testRssSources();