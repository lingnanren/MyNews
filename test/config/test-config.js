const config = require('./src/config');

console.log('当前配置：');
console.log('SMTP服务器:', config.email.smtp.server);
console.log('SMTP端口:', config.email.smtp.port);
console.log('SMTP用户名:', config.email.smtp.username);
console.log('SMTP密码:', config.email.smtp.password ? '***已设置***' : '未设置');
console.log('发件人邮箱:', config.email.smtp.from);

// 测试环境变量是否正确加载
console.log('\n环境变量：');
console.log('SMTP_SERVER:', process.env.SMTP_SERVER);
console.log('SMTP_PORT:', process.env.SMTP_PORT);
console.log('SMTP_USERNAME:', process.env.SMTP_USERNAME);
console.log('SMTP_PASSWORD:', process.env.SMTP_PASSWORD ? '***已设置***' : '未设置');
console.log('FROM_EMAIL:', process.env.FROM_EMAIL);

console.log('\n配置检查完成！');
