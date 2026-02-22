const nodemailer = require('nodemailer');
const config = require('../../config');
const { User, News } = require('../../models');

class EmailService {
  // 创建邮件传输器
  createTransport() {
    return nodemailer.createTransport({
      host: config.email.smtp.server,
      port: config.email.smtp.port,
      secure: false, // 587端口使用STARTTLS
      auth: {
        user: config.email.smtp.username,
        pass: config.email.smtp.password
      }
    });
  }
  
  // 生成邮件内容
  async generateEmailContent(userId) {
    try {
      const user = await User.findByPk(userId);
      if (!user || !user.isActive) {
        throw new Error('用户不存在或未激活');
      }
      
      // 获取用户感兴趣的领域
      const interests = user.interests.split(',');
      
      // 获取每个领域的最新新闻（已处理过的）
      const newsByCategory = {};
      
      for (const interest of interests) {
        const news = await News.findAll({
          where: {
            category: interest,
            isProcessed: true
          },
          order: [['publishedAt', 'DESC']],
          limit: 3
        });
        
        if (news.length > 0) {
          newsByCategory[interest] = news;
        }
      }
      
      // 检查是否有足够的新闻内容
      let totalNewsCount = 0;
      for (const newsList of Object.values(newsByCategory)) {
        totalNewsCount += newsList.length;
      }
      
      // 如果没有新闻内容，返回错误
      if (totalNewsCount === 0) {
        return { success: false, error: '没有找到足够的新闻内容，无法生成邮件' };
      }
      
      // 构建邮件HTML内容 - 每日读报60秒形式
      let htmlContent = `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f9f9f9; padding: 20px; border-radius: 8px;">
          <div style="background-color: #3498db; color: white; padding: 15px; border-radius: 6px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">📰 每日读报60秒</h1>
            <p style="margin: 5px 0 0 0; font-size: 14px;">${new Date().toLocaleDateString('zh-CN')}</p>
          </div>
          
          <div style="background-color: white; padding: 20px; margin-top: 20px; border-radius: 6px;">
            <p style="color: #666; margin-bottom: 20px;">每天60秒，了解天下事！</p>
      `;
      
      // 添加各个领域的新闻 - 简洁列表形式
      let newsCount = 0;
      for (const [category, newsList] of Object.entries(newsByCategory)) {
        htmlContent += `
          <div style="margin-bottom: 20px;">
            <h2 style="color: #3498db; margin: 0 0 15px 0; font-size: 18px; border-bottom: 2px solid #3498db; padding-bottom: 5px;">${category}</h2>
        `;
        
        for (const news of newsList) {
          // 跳过测试数据和example链接
          if (news.url && (news.url.includes('example.com') || news.url.includes('example.org'))) {
            continue;
          }
          
          htmlContent += `
            <div style="margin-bottom: 12px; padding-left: 10px; border-left: 3px solid #e0e0e0;">
              <p style="margin: 0 0 5px 0; font-weight: bold; color: #333;">${news.title}</p>
              <p style="margin: 0 0 8px 0; font-size: 12px; color: #666;">${news.source}</p>
              <p style="margin: 0; font-size: 14px; color: #555; line-height: 1.4;">${news.summary || '暂无摘要'}</p>
            </div>
          `;
          newsCount++;
        }
        
        htmlContent += `
          </div>
        `;
      }
      
      htmlContent += `
          </div>
          
          <div style="margin-top: 20px; text-align: center; font-size: 12px; color: #999;">
            <p>此邮件由 MyNews 自动生成，请勿直接回复</p>
            <p>每天8点半，准时为您带来最新资讯</p>
          </div>
        </div>
      `;
      
      return { success: true, htmlContent, textContent: 'MyNews 每日新闻摘要', subject: `MyNews 每日新闻摘要 - ${new Date().toLocaleDateString('zh-CN')}` };
    } catch (error) {
      console.error('生成邮件内容失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 发送邮件
  async sendEmail(userId) {
    try {
      const user = await User.findByPk(userId);
      if (!user || !user.isActive) {
        throw new Error('用户不存在或未激活');
      }
      
      // 生成邮件内容
      const contentResult = await this.generateEmailContent(userId);
      if (!contentResult.success) {
        throw new Error(contentResult.error);
      }
      
      // 创建邮件传输器
      const transporter = this.createTransport();
      
      // 邮件选项
      const mailOptions = {
        from: config.email.smtp.from,
        to: user.email,
        subject: contentResult.subject,
        html: contentResult.htmlContent,
        text: contentResult.textContent
      };
      
      // 发送邮件
      const info = await transporter.sendMail(mailOptions);
      console.log('邮件发送成功:', info.messageId);
      
      return { success: true, messageId: info.messageId };
    } catch (error) {
      console.error('发送邮件失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 发送测试邮件
  async sendTestEmail(toEmail) {
    try {
      const transporter = this.createTransport();
      
      const mailOptions = {
        from: config.email.smtp.from,
        to: toEmail,
        subject: 'MyNews 测试邮件',
        html: `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #333; text-align: center;">MyNews 测试邮件</h1>
            <p style="color: #666; text-align: center;">${new Date().toLocaleString('zh-CN')}</p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #555;">这是一封测试邮件，表明 MyNews 的邮件发送功能正常工作。</p>
            <p style="color: #555;">如果您收到此邮件，说明邮件配置正确。</p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px; text-align: center;">此邮件由 MyNews 自动生成，请勿直接回复。</p>
          </div>
        `,
        text: 'MyNews 测试邮件 - 邮件发送功能正常'
      };
      
      const info = await transporter.sendMail(mailOptions);
      console.log('测试邮件发送成功:', info.messageId);
      
      return { success: true, messageId: info.messageId };
    } catch (error) {
      console.error('发送测试邮件失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 批量发送邮件给所有激活用户
  async sendEmailToAllUsers() {
    try {
      const users = await User.findAll({ where: { isActive: true } });
      const results = [];
      
      for (const user of users) {
        const result = await this.sendEmail(user.id);
        results.push({ userId: user.id, email: user.email, ...result });
      }
      
      return { success: true, results, count: results.length };
    } catch (error) {
      console.error('批量发送邮件失败:', error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = new EmailService();