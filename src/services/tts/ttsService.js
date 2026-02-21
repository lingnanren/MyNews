const fs = require('fs');
const path = require('path');
const { News } = require('../../models');

// 确保音频文件目录存在
const audioDir = path.join(__dirname, '../../../public/audio');
if (!fs.existsSync(audioDir)) {
  fs.mkdirSync(audioDir, { recursive: true });
}

class TtsService {
  // 生成语音文件（模拟实现，实际项目中需要集成Google TTS API）
  async generateSpeech(newsId) {
    try {
      const news = await News.findByPk(newsId);
      if (!news) {
        throw new Error('新闻不存在');
      }
      
      // 检查是否已有音频文件
      if (news.audioUrl) {
        return { success: true, audioUrl: news.audioUrl };
      }
      
      // 构建语音内容（使用摘要或标题）
      const speechContent = news.summary || news.title;
      
      // 生成唯一的音频文件名
      const audioFileName = `news_${newsId}_${Date.now()}.mp3`;
      const audioFilePath = path.join(audioDir, audioFileName);
      const audioUrl = `/audio/${audioFileName}`;
      
      // 模拟生成音频文件（实际项目中需要调用Google TTS API）
      // 这里创建一个空文件作为占位符
      fs.writeFileSync(audioFilePath, '');
      
      // 更新新闻的音频URL
      await news.update({ audioUrl: audioUrl });
      
      console.log(`语音文件生成成功: ${audioUrl}`);
      return { success: true, audioUrl: audioUrl };
    } catch (error) {
      console.error('生成语音失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 批量生成语音文件
  async batchGenerateSpeech(newsIds) {
    try {
      const results = [];
      
      for (const newsId of newsIds) {
        const result = await this.generateSpeech(newsId);
        results.push({ newsId, ...result });
      }
      
      return { success: true, results };
    } catch (error) {
      console.error('批量生成语音失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 为已处理的新闻生成语音
  async generateSpeechForProcessedNews(limit = 10) {
    try {
      const processedNews = await News.findAll({
        where: {
          isProcessed: true,
          audioUrl: null
        },
        limit: limit
      });
      
      const results = [];
      
      for (const news of processedNews) {
        const result = await this.generateSpeech(news.id);
        results.push({ newsId: news.id, ...result });
      }
      
      return { success: true, results, count: results.length };
    } catch (error) {
      console.error('为已处理新闻生成语音失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 获取语音文件路径
  getAudioFilePath(audioUrl) {
    if (!audioUrl) {
      return null;
    }
    
    // 从URL中提取文件名
    const fileName = audioUrl.split('/').pop();
    return path.join(audioDir, fileName);
  }
  
  // 删除语音文件
  deleteSpeech(newsId) {
    try {
      // 这里可以添加删除语音文件的逻辑
      console.log(`删除语音文件: ${newsId}`);
      return { success: true };
    } catch (error) {
      console.error('删除语音文件失败:', error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = new TtsService();