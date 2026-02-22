const axios = require('axios');
const config = require('../../config');
const { News } = require('../../models');

class AIService {
  // 检测文本是否为英文
  isEnglish(text) {
    return /^[a-zA-Z0-9\s.,!?'"()\[\]{}:;-]+$/.test(text.replace(/[\u4e00-\u9fa5]/g, ''));
  }

  // 生成备用摘要
  generateBackupSummary(news) {
    // 基于标题和内容生成摘要
    let summary = news.title;
    
    // 检查是否为英文，如果是则添加翻译标记
    if (this.isEnglish(news.title) || this.isEnglish(news.content)) {
      summary = `[翻译] ${summary}`;
    }
    
    // 根据新闻类别生成更具体的描述
    if (news.category === '财经') {
      if (news.title.includes('上涨') || news.title.includes('涨幅') || news.title.includes('涨停') || news.title.includes('rise') || news.title.includes('Rise')) {
        summary += `。${news.source}报道，该股票/指数上涨，市场表现强劲。`;
      } else if (news.title.includes('下跌') || news.title.includes('跌幅') || news.title.includes('跌停') || news.title.includes('down') || news.title.includes('Down')) {
        summary += `。${news.source}报道，该股票/指数下跌，市场表现疲软。`;
      } else if (news.title.includes('政策') || news.title.includes('Policy') || news.title.includes('policy')) {
        summary += `。${news.source}报道，相关部门出台新政策，对市场产生重要影响。`;
      } else {
        summary += `。${news.source}报道了这一财经动态，为投资者提供重要信息。`;
      }
    } else if (news.category === '科技') {
      if (news.title.includes('发布') || news.title.includes('推出') || news.title.includes('launch') || news.title.includes('Launch')) {
        summary += `。${news.source}报道，该公司发布了新产品/技术，引领行业创新。`;
      } else if (news.title.includes('突破') || news.title.includes('创新') || news.title.includes('breakthrough') || news.title.includes('Breakthrough')) {
        summary += `。${news.source}报道，该领域取得重大突破，技术发展进入新阶段。`;
      } else {
        summary += `。${news.source}报道了这一科技领域的最新进展，反映了行业发展趋势。`;
      }
    } else if (news.category === '军事') {
      summary += `。${news.source}报道了这一军事相关新闻，反映了国际局势的最新变化。`;
    } else if (news.category === '生活') {
      if (news.title.includes('热搜') || news.title.includes('热门') || news.title.includes('hot') || news.title.includes('Hot')) {
        summary += `。${news.source}报道，这一话题成为热门讨论，引发广泛关注。`;
      } else if (news.title.includes('健康') || news.title.includes('医疗') || news.title.includes('health') || news.title.includes('Health')) {
        summary += `。${news.source}报道了这一健康相关信息，对民众生活有重要参考价值。`;
      } else {
        summary += `。${news.source}报道了这一生活领域的新闻，与民众日常生活密切相关。`;
      }
    } else {
      summary += `。${news.source}报道了这一${news.category}领域的最新动态。`;
    }
    
    return summary;
  }

  // 调用DeepSeek API生成新闻摘要
  async generateSummary(newsId) {
    try {
      const news = await News.findByPk(newsId);
      if (!news) {
        throw new Error('新闻不存在');
      }
      
      let summary;
      let apiSuccess = false;
      
      // 检查是否有DeepSeek API密钥
      if (config.deepseek.apiKey && config.deepseek.apiKey !== 'your-deepseek-api-key') {
        try {
          // 构建API请求 - 使用官方推荐的URL和参数
          const response = await axios.post(
            config.deepseek.apiUrl, // 使用配置文件中的API URL
            {
              model: 'deepseek-chat', // 官方推荐的模型名称
              messages: [
                {
                  role: 'system',
                  content: '你是一个专业的新闻摘要助手，请将以下新闻内容浓缩为60秒阅读量的精华摘要，保持关键信息完整，语言简洁有力，直接切入主题，不使用任何引言或开场白。如果新闻内容是英文，请先完整翻译为中文，然后再生成摘要。摘要中必须包含新闻来源。'
                },
                {
                  role: 'user',
                  content: `新闻标题：${news.title}\n\n新闻内容：${news.content || '暂无详细内容'}\n\n新闻来源：${news.source}`
                }
              ],
              max_tokens: 1000,
              temperature: 0.7,
              stream: false
            },
            {
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.deepseek.apiKey}`
              }
            }
          );
          
          summary = response.data.choices[0].message.content;
          apiSuccess = true;
        } catch (apiError) {
          console.error('API调用失败，使用备用摘要生成:', apiError.message);
          // 使用备用摘要生成
          summary = this.generateBackupSummary(news);
        }
      } else {
        // 模拟摘要生成（用于测试环境）
        console.log('使用模拟摘要生成（测试环境）');
        summary = this.generateBackupSummary(news);
      }
      
      // 更新新闻摘要
      await news.update({ 
        summary: summary,
        isProcessed: true
      });
      
      return { success: true, summary, apiSuccess };
    } catch (error) {
      console.error('生成摘要失败:', error);
      // 即使出错，也尝试生成备用摘要
      try {
        const news = await News.findByPk(newsId);
        if (news) {
          const backupSummary = this.generateBackupSummary(news);
          await news.update({ 
            summary: backupSummary,
            isProcessed: true
          });
          return { success: true, summary: backupSummary, apiSuccess: false };
        }
      } catch (backupError) {
        console.error('备用摘要生成也失败:', backupError.message);
      }
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