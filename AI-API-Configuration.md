# AI API密钥配置说明

## 概述

MyNews系统使用DeepSeek-R1 API进行新闻摘要生成。本文档将详细说明如何获取和配置DeepSeek-R1 API密钥。

## 获取DeepSeek-R1 API密钥

### 步骤1：注册DeepSeek账户

1. 访问 [DeepSeek官网](https://www.deepseek.com/)
2. 点击"Sign Up"或"注册"按钮
3. 填写注册信息并完成邮箱验证
4. 登录到DeepSeek控制台

### 步骤2：创建API密钥

1. 在DeepSeek控制台中，导航到"API Keys"或"API密钥"页面
2. 点击"Create New Key"或"创建新密钥"按钮
3. 为密钥添加描述（例如："MyNews系统"）
4. 点击"Generate"或"生成"按钮
5. 复制生成的API密钥（请妥善保存，密钥只会显示一次）

### 步骤3：配置API密钥权限

确保您的API密钥具有以下权限：
- Chat Completions API 权限
- 足够的API调用配额

## 配置AI API密钥

### 方法1：通过.env文件配置

1. 打开项目根目录中的 `.env` 文件
2. 找到 `DEEPSEEK_API_KEY` 配置项
3. 将您获取的API密钥填入该配置项

```env
# DeepSeek-R1 API配置
DEEPSEEK_API_KEY=your-deepseek-api-key  # 替换为真实的API密钥
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
```

### 方法2：通过环境变量配置

在启动应用前设置环境变量：

#### Linux/macOS
```bash
export DEEPSEEK_API_KEY=your-deepseek-api-key
npm start
```

#### Windows
```cmd
set DEEPSEEK_API_KEY=your-deepseek-api-key
npm start
```

## 验证API密钥配置

### 测试API密钥是否有效

1. 运行配置测试脚本：
   ```bash
   npm run test:config
   ```

2. 运行AI摘要测试脚本：
   ```bash
   npm run test:ai
   ```

3. 检查控制台输出，确认API密钥是否被正确加载

## 故障排除

### 常见问题

1. **API密钥无效**
   - 检查API密钥是否正确复制
   - 确认API密钥是否已过期
   - 验证API密钥是否有足够的权限

2. **API调用失败**
   - 检查网络连接是否正常
   - 确认DeepSeek API服务是否正常
   - 验证API密钥是否有足够的配额

3. **配置未生效**
   - 检查.env文件是否在正确的位置
   - 确认环境变量是否正确设置
   - 重启应用使配置生效

### 测试环境配置

如果您没有DeepSeek API密钥，可以使用系统的模拟摘要功能进行测试：

1. 保持.env文件中的默认配置：
   ```env
   DEEPSEEK_API_KEY=your-deepseek-api-key
   ```

2. 系统会自动使用模拟摘要生成功能，确保测试环境正常运行

## API调用示例

### DeepSeek-R1 API调用格式

```javascript
const response = await axios.post(
  config.deepseek.apiUrl,
  {
    model: 'deepseek-ai/deepseek-r1',
    messages: [
      {
        role: 'system',
        content: '你是一个专业的新闻摘要助手，请将以下新闻内容浓缩为5分钟阅读量的精华摘要，保持关键信息完整，语言流畅自然。'
      },
      {
        role: 'user',
        content: `新闻标题：${news.title}\n\n新闻内容：${news.content}`
      }
    ],
    max_tokens: 1000,
    temperature: 0.7
  },
  {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.deepseek.apiKey}`
    }
  }
);
```

## 最佳实践

1. **安全存储**：API密钥属于敏感信息，请勿在代码中硬编码
2. **定期轮换**：定期更新API密钥以提高安全性
3. **监控使用**：监控API调用情况，避免超出配额
4. **错误处理**：在代码中添加适当的错误处理，确保系统稳定性

## 联系支持

如果您在配置过程中遇到问题：

1. 查看 [DeepSeek官方文档](https://docs.deepseek.com/)
2. 联系DeepSeek技术支持
3. 查看项目的GitHub Issues页面

---

**注意**：本配置仅适用于生产环境。在开发和测试环境中，系统会自动使用模拟摘要功能，无需真实的API密钥。