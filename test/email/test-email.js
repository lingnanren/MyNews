const nodemailer = require('nodemailer');
require('dotenv').config();

async function testEmail() {
  try {
    // 创建邮件传输器
    const transporter = nodemailer.createTransporter({
      host: process.env.SMTP_SERVER,
      port: process.env.SMTP_PORT,
      secure: false, // 587端口使用STARTTLS
      auth: {
        user: process.env.SMTP_USERNAME,
        pass: process.env.SMTP_PASSWORD
      }
    });

    // 邮件选项
    const mailOptions = {
      from: process.env.FROM_EMAIL,
      to: process.env.FROM_EMAIL, // 发送给自己
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

    // 发送邮件
    const info = await transporter.sendMail(mailOptions);
    console.log('邮件发送成功:', info.messageId);
    console.log('邮件已发送到:', process.env.FROM_EMAIL);
  } catch (error) {
    console.error('邮件发送失败:', error);
  }
}

// 运行测试
testEmail();