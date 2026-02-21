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
      
      // 构建邮件HTML内容
      let htmlContent = `
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
          <h1 style="color: #333; text-align: center;">MyNews 每日新闻摘要</h1>
          <p style="color: #666; text-align: center;">${new Date().toLocaleDateString('zh-CN')}</p>
          <hr style="border: 1px solid #eee; margin: 20px 0;">
      `;
      
      // 添加各个领域的新闻
      for (const [category, newsList] of Object.entries(newsByCategory)) {
        htmlContent += `
          <h2 style="color: #333; margin-top: 30px;">${category}</h2>
          <div style="margin-left: 20px;">
        `;
        
        for (const news of newsList) {
          htmlContent += `
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #3498db; background-color: #f9f9f9;">
              <h3 style="margin: 0 0 10px 0; color: #333;">${news.title}</h3>
              <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">来源：${news.source} | ${news.publishedAt ? news.publishedAt.toLocaleDateString('zh-CN') : ''}</p>
              <p style="margin: 0 0 15px 0; color: #555;">${news.summary}</p>
              <a href="${news.url}" style="color: #3498db; text-decoration: none; font-weight: bold;">阅读原文</a>
            </div>
          `;
        }
        
        htmlContent += `
          </div>
        `;
      }
      
      htmlContent += `
          <hr style="border: 1px solid #eee; margin: 30px 0;">
          <p style="color: #999; font-size: 12px; text-align: center;">此邮件由 MyNews 自动生成，请勿直接回复。</p>
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