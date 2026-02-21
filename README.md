# MyNews 自定义新闻聚合系统

MyNews是一个个性化新闻聚合与推送系统，支持自定义RSS源、AI新闻摘要、语音合成和多渠道推送。

## 功能特性

- 📚 **自定义RSS源管理**：支持添加、编辑、删除RSS源，按分类管理
- 🤖 **AI新闻摘要**：使用DeepSeek-R1 API生成5分钟阅读量的精华摘要
- 🎤 **语音合成**：将新闻内容转换为语音，支持音频文件生成
- 📧 **邮件推送**：每日定时发送新闻摘要到指定邮箱
- 📱 **微信公众号推送**：未来扩展支持，发送图文+语音内容
- ⏰ **定时任务**：自动执行RSS抓取、新闻处理、推送等任务
- 🔄 **工作流引擎**：集成n8n，支持灵活的工作流配置

## 技术栈

- **后端**：Node.js + Express
- **数据库**：SQLite
- **ORM**：Sequelize
- **RSS解析**：rss-parser
- **邮件发送**：nodemailer
- **AI接口**：DeepSeek-R1 API
- **语音合成**：Google Text-to-Speech API
- **定时任务**：node-cron
- **工作流**：n8n

## 快速开始

### 1. 环境准备

- Node.js 14+
- npm 6+
- SQLite 3+

### 2. 安装依赖

```bash
npm install
```

### 3. 配置环境变量

复制 `.env.example` 文件为 `.env`，并填写相应的配置信息：

```bash
cp src/config/.env.example .env
```

主要配置项：

- `PORT`：服务器端口
- `DB_PATH`：SQLite数据库路径
- `EMAIL_SERVICE`：邮件服务提供商
- `EMAIL_USER`：发件人邮箱
- `EMAIL_PASS`：发件人邮箱密码
- `DEEPSEEK_API_KEY`：DeepSeek-R1 API密钥
- `PUSH_TIME`：每日推送时间

### 4. 启动服务

```bash
# 开发模式
npm run dev

# 生产模式
npm start
```

服务启动后，可访问 `http://localhost:3000` 查看系统状态。

## API接口

### RSS源管理

- `GET /api/rss/sources` - 获取所有RSS源
- `POST /api/rss/sources` - 添加RSS源
- `PUT /api/rss/sources/:id` - 更新RSS源
- `DELETE /api/rss/sources/:id` - 删除RSS源
- `POST /api/rss/sources/fetch-all` - 抓取所有RSS源

### AI处理

- `POST /api/ai/summary/:newsId` - 生成单个新闻摘要
- `POST /api/ai/summary/batch` - 批量生成新闻摘要
- `POST /api/ai/summary/process-unprocessed` - 处理未处理的新闻

### 邮件推送

- `POST /api/notify/email/:userId` - 发送邮件给指定用户
- `POST /api/notify/email/test` - 发送测试邮件
- `POST /api/notify/email/all` - 发送邮件给所有用户

### 语音合成

- `POST /api/tts/speech/:newsId` - 为指定新闻生成语音
- `POST /api/tts/speech/batch` - 批量生成语音
- `POST /api/tts/speech/process-processed` - 为已处理的新闻生成语音

### 工作流

- `POST /api/workflow/n8n/start-news-processing` - 启动新闻处理工作流
- `GET /api/workflow/n8n/health` - 检查n8n服务状态

## 项目结构

```
MyNews/
├── src/              # 源代码
│   ├── config/       # 配置文件
│   ├── controllers/  # 控制器
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   │   ├── rss/      # RSS处理
│   │   ├── ai/       # AI服务
│   │   ├── tts/      # 语音合成
│   │   ├── notify/   # 推送服务
│   │   ├── cron/     # 定时任务
│   │   └── workflow/ # 工作流服务
│   ├── routes/       # 路由
│   ├── utils/        # 工具函数
│   └── index.js      # 应用入口
├── public/           # 静态资源
├── views/            # 视图模板
├── n8n/              # n8n工作流配置
├── test/             # 测试脚本
├── package.json      # 项目配置
└── README.md         # 项目说明
```

## 部署说明

### 本地部署

1. 安装依赖
2. 配置环境变量
3. 启动服务

### 内网穿透

使用Cpolar进行内网穿透，实现公网访问：

1. 下载并安装Cpolar
2. 配置Cpolar隧道：
   ```bash
   cpolar http 3000
   ```
3. 使用生成的公网地址访问服务

### 定时任务

系统默认配置了以下定时任务：

- 每天凌晨2点：抓取RSS源
- 每天凌晨3点：处理未处理的新闻
- 每天凌晨4点：生成语音文件
- 每天早上8点：推送邮件

## 未来规划

- [ ] 微信公众号推送集成
- [ ] 移动应用客户端
- [ ] 多用户支持
- [ ] 个性化推荐算法
- [ ] 更多AI模型集成
- [ ] 数据可视化 dashboard

## 许可证

ISC License