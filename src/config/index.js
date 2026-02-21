const path = require('path');
const dotenv = require('dotenv');

// 尝试加载不同位置的.env文件
const envPaths = [
  path.resolve(__dirname, '../../.env'),
  path.resolve(process.cwd(), '.env')
];

let envLoaded = false;
for (const envPath of envPaths) {
  try {
    const result = dotenv.config({ path: envPath });
    if (!result.error) {
      console.log(`环境变量加载成功: ${envPath}`);
      envLoaded = true;
      break;
    }
  } catch (error) {
    console.log(`尝试加载 ${envPath} 失败:`, error.message);
  }
}

if (!envLoaded) {
  console.log('未找到.env文件，使用默认环境变量');
  dotenv.config();
}

const config = {
  // 系统配置
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  
  // 数据库配置
  db: {
    path: process.env.DB_PATH || './database.sqlite'
  },
  
  // 邮件配置
  email: {
    service: process.env.EMAIL_SERVICE || 'Gmail',
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
    smtp: {
      server: process.env.SMTP_SERVER,
      port: process.env.SMTP_PORT,
      username: process.env.SMTP_USERNAME,
      password: process.env.SMTP_PASSWORD,
      from: process.env.FROM_EMAIL
    }
  },
  
  // DeepSeek-R1 API配置
  deepseek: {
    apiKey: process.env.DEEPSEEK_API_KEY,
    apiUrl: process.env.DEEPSEEK_API_URL || 'https://api.deepseek.com/v1/chat/completions'
  },
  
  // Google TTS API配置
  google: {
    credentials: process.env.GOOGLE_APPLICATION_CREDENTIALS
  },
  
  // 推送配置
  push: {
    time: process.env.PUSH_TIME || '08:00'
  },
  
  // 兴趣领域配置
  interests: process.env.INTERESTS ? process.env.INTERESTS.split(',') : ['财经', '军事', '生活', '科技']
};

module.exports = config;