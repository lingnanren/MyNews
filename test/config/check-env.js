const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '.env') });

console.log('环境变量检查:');
console.log('SMTP_SERVER:', process.env.SMTP_SERVER);
console.log('SMTP_PORT:', process.env.SMTP_PORT);
console.log('SMTP_USERNAME:', process.env.SMTP_USERNAME);
console.log('SMTP_PASSWORD:', process.env.SMTP_PASSWORD);
console.log('FROM_EMAIL:', process.env.FROM_EMAIL);
console.log('CPOLAR_AUTHTOKEN:', process.env.CPOLAR_AUTHTOKEN);