const rssService = require('../src/services/rss/rssService');
const aiService = require('../src/services/ai/aiService');
const ttsService = require('../src/services/tts/ttsService');
const emailService = require('../src/services/notify/emailService');
const n8nService = require('../src/services/workflow/n8nService');

async function testCompleteFlow() {
  console.log('开始测试完整流程...');
  
  try {
    // 1. 测试RSS抓取
    console.log('\n1. 测试RSS抓取...');
    const rssResult = await rssService.fetchAllRssSources();
    console.log('RSS抓取结果:', rssResult);
    
    // 等待2秒
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 2. 测试新闻处理
    console.log('\n2. 测试新闻处理...');
    const aiResult = await aiService.processUnprocessedNews(5);
    console.log('新闻处理结果:', aiResult);
    
    // 等待2秒
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 3. 测试语音生成
    console.log('\n3. 测试语音生成...');
    const ttsResult = await ttsService.generateSpeechForProcessedNews(5);
    console.log('语音生成结果:', ttsResult);
    
    // 等待2秒
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 4. 测试邮件推送
    console.log('\n4. 测试邮件推送...');
    // 注意：这里只是测试邮件发送功能，实际发送需要配置正确的邮箱信息
    const emailTestResult = await emailService.sendTestEmail('test@example.com');
    console.log('邮件测试结果:', emailTestResult);
    
    // 5. 测试n8n工作流
    console.log('\n5. 测试n8n工作流...');
    const n8nHealthResult = await n8nService.checkHealth();
    console.log('n8n服务状态:', n8nHealthResult);
    
    console.log('\n完整流程测试完成！');
  } catch (error) {
    console.error('测试流程失败:', error);
  }
}

// 运行测试
if (require.main === module) {
  testCompleteFlow();
}

module.exports = { testCompleteFlow };