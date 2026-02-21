const axios = require('axios');
const config = require('../../config');
const { News } = require('../../models');

class AIService {
  // 调用DeepSeek-R1 API生成新闻摘要
  async generateSummary(newsId) {
    try {
      const news = await News.findByPk(newsId);
      if (!news) {
        throw new Error('新闻不存在');
      }
      
      let summary;
      
      // 检查是否有DeepSeek API密钥
      if (config.deepseek.apiKey && config.deepseek.apiKey !== 'your-deepseek-api-key') {
        // 构建API请求
        const response = await axios.post(
          config.deepseek.apiUrl,
          {
            model: 'deepseek-ai/deepseek-r1',
            messages: [
              {
                role: 'system',
                content: '你是一个专业的新闻摘要助手，请将以下新闻内容浓缩为5分钟阅读量的精华摘要，保持关键信息完整，语言流畅自然。'
              },
              {
                role: 'user',
                content: `新闻标题：${news.title}\n\n新闻内容：${news.content}`
              }
            ],
            max_tokens: 1000,
            temperature: 0.7
          },
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${config.deepseek.apiKey}`
            }
          }
        );
        
        summary = response.data.choices[0].message.content;
      } else {
        // 模拟摘要生成（用于测试环境）
        console.log('使用模拟摘要生成（测试环境）');
        summary = `【摘要】${news.title}。这是一条关于${news.category}领域的重要新闻，来自${news.source}。详细内容请查看原文。`;
      }
      
      // 更新新闻摘要
      await news.update({ 
        summary: summary,
        isProcessed: true
      });
      
      return { success: true, summary };
    } catch (error) {
      console.error('生成摘要失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 批量处理新闻摘要
  async batchGenerateSummary(newsIds) {
    try {
      const results = [];
      
      for (const newsId of newsIds) {
        const result = await this.generateSummary(newsId);
        results.push({ newsId, ...result });
      }
      
      return { success: true, results };
    } catch (error) {
      console.error('批量生成摘要失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 处理未处理的新闻
  async processUnprocessedNews(limit = 10) {
    try {
      const unprocessedNews = await News.findAll({
        where: { isProcessed: false },
        limit: limit
      });
      
      const results = [];
      
      for (const news of unprocessedNews) {
        const result = await this.generateSummary(news.id);
        results.push({ newsId: news.id, ...result });
      }
      
      return { success: true, results, count: results.length };
    } catch (error) {
      console.error('处理未处理新闻失败:', error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = new AIService();