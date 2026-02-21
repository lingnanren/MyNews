const express = require('express');
const { sequelize } = require('./config/database');
const config = require('./config');
const { RssSource, News, User } = require('./models');
const rssRoutes = require('./routes/rss');
const aiRoutes = require('./routes/ai');
const notifyRoutes = require('./routes/notify');
const ttsRoutes = require('./routes/tts');
const workflowRoutes = require('./routes/workflow');
const cronService = require('./services/cron/cronService');

// 初始化Express应用
const app = express();

// 中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.set('views', './views');
app.use(express.static('public'));

// 路由
app.get('/', (req, res) => {
  res.render('index', { title: 'MyNews' });
});

// API路由
app.use('/api/rss', rssRoutes);
app.use('/api/ai', aiRoutes);
app.use('/api/notify', notifyRoutes);
app.use('/api/tts', ttsRoutes);
app.use('/api/workflow', workflowRoutes);

// 初始化数据库
async function initDatabase() {
  try {
    // 同步数据库模型
    await sequelize.sync({ force: false });
    console.log('数据库模型同步成功');
    
    // 初始化默认RSS源
    const defaultSources = [
      {
        name: '财经日报',
        url: 'https://rsshub.app/finance/163/daily',
        category: '财经',
        isActive: true
      },
      {
        name: '军事新闻',
        url: 'https://rsshub.app/mil/81',
        category: '军事',
        isActive: true
      },
      {
        name: '生活资讯',
        url: 'https://rsshub.app/zhihu/daily',
        category: '生活',
        isActive: true
      },
      {
        name: '科技新闻',
        url: 'https://rsshub.app/tech/36kr',
        category: '科技',
        isActive: true
      }
    ];
    
    for (const source of defaultSources) {
      const [created] = await RssSource.findOrCreate({
        where: { url: source.url },
        defaults: source
      });
      if (created) {
        console.log(`添加默认RSS源: ${source.name}`);
      }
    }
    
    // 初始化默认用户
    const defaultUser = {
      email: 'user@example.com',
      interests: '财经,军事,生活,科技',
      pushTime: '08:00',
      pushMethod: 'email',
      isActive: true
    };
    
    const [userCreated] = await User.findOrCreate({
      where: { email: defaultUser.email },
      defaults: defaultUser
    });
    if (userCreated) {
      console.log('添加默认用户');
    }
    
  } catch (error) {
    console.error('数据库初始化失败:', error);
  }
}

// 启动服务器
app.listen(config.port, async () => {
  console.log(`服务器运行在端口 ${config.port}`);
  // 初始化数据库
  await initDatabase();
  // 初始化定时任务
  cronService.init();
});

module.exports = app;