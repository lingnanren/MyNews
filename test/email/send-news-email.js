const emailService = require('./src/services/notify/emailService');

async function sendNewsEmail() {
  try {
    console.log('正在发送包含具体新闻内容的邮件...');
    console.log('目标邮箱: yza15@qq.com');
    
    // 发送邮件给用户ID为1的用户（yza15@qq.com）
    const result = await emailService.sendEmail(1);
    
    if (result.success) {
      console.log('✅ 邮件发送成功！');
      console.log('邮件ID:', result.messageId);
      console.log('\n请检查您的邮箱（yza15@qq.com），邮件应该已经送达。');
      console.log('邮件包含了财经、军事、生活、科技四个领域的最新新闻摘要。');
    } else {
      console.error('❌ 邮件发送失败:', result.error);
      console.log('\n请检查以下可能的原因：');
      console.log('1. SMTP配置是否正确（.env文件中的邮箱设置）');
      console.log('2. 网络连接是否正常');
      console.log('3. 邮箱服务器是否允许第三方应用登录');
      console.log('4. 数据库中的用户和新闻数据是否存在');
    }
    
  } catch (error) {
    console.error('发送邮件时发生错误:', error.message);
  }
}

sendNewsEmail();