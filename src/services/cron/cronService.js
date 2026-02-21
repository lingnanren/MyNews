const cron = require('node-cron');
const rssService = require('../rss/rssService');
const aiService = require('../ai/aiService');
const ttsService = require('../tts/ttsService');
const emailService = require('../notify/emailService');
const { User } = require('../../models');

class CronService {
  // 初始化定时任务
  init() {
    console.log('初始化定时任务...');
    
    // 每天凌晨2点抓取RSS源
    cron.schedule('0 2 * * *', async () => {
      console.log('执行定时RSS抓取任务...');
      await this.fetchRssSources();
    });
    
    // 每天凌晨3点处理未处理的新闻
    cron.schedule('0 3 * * *', async () => {
      console.log('执行定时新闻处理任务...');
      await this.processNews();
    });
    
    // 每天凌晨4点生成语音文件
    cron.schedule('0 4 * * *', async () => {
      console.log('执行定时语音生成任务...');
      await this.generateSpeech();
    });
    
    // 每天早上8点推送邮件
    cron.schedule('0 8 * * *', async () => {
      console.log('执行定时邮件推送任务...');
      await this.sendEmails();
    });
    
    console.log('定时任务初始化完成');
  }
  
  // 抓取RSS源
  async fetchRssSources() {
    try {
      const result = await rssService.fetchAllRssSources();
      console.log('RSS抓取任务完成:', result);
    } catch (error) {
      console.error('RSS抓取任务失败:', error);
    }
  }
  
  // 处理未处理的新闻
  async processNews() {
    try {
      const result = await aiService.processUnprocessedNews(20);
      console.log('新闻处理任务完成:', result);
    } catch (error) {
      console.error('新闻处理任务失败:', error);
    }
  }
  
  // 生成语音文件
  async generateSpeech() {
    try {
      const result = await ttsService.generateSpeechForProcessedNews(20);
      console.log('语音生成任务完成:', result);
    } catch (error) {
      console.error('语音生成任务失败:', error);
    }
  }
  
  // 发送邮件
  async sendEmails() {
    try {
      const result = await emailService.sendEmailToAllUsers();
      console.log('邮件推送任务完成:', result);
    } catch (error) {
      console.error('邮件推送任务失败:', error);
    }
  }
  
  // 手动触发所有任务（用于测试）
  async triggerAllTasks() {
    console.log('手动触发所有任务...');
    
    await this.fetchRssSources();
    await new Promise(resolve => setTimeout(resolve, 2000)); // 等待2秒
    
    await this.processNews();
    await new Promise(resolve => setTimeout(resolve, 2000)); // 等待2秒
    
    await this.generateSpeech();
    await new Promise(resolve => setTimeout(resolve, 2000)); // 等待2秒
    
    await this.sendEmails();
    
    console.log('所有任务触发完成');
  }
}

module.exports = new CronService();