# 每天读报5分钟自动化系统

本仓库严格按 PRD 实现每日新闻自动化系统：采集国内、国际、财经新闻，调用 DeepSeek 生成 30-50 字摘要，按固定 HTML 邮件模板输出，并通过 SMTP 发送。

## 运行

安装依赖：

```bash
pip install -r requirements.txt
```

复制 `.env.example` 为 `.env` 并按 PRD 配置：

```bash
DEEPSEEK_API_KEY=sk-xxxxxx
DEEPSEEK_MODEL=deepseek-chat
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_password
RECIPIENT_EMAILS=test1@example.com,test2@example.com
RUN_TIME=06:00
DOMESTIC_NEWS_COUNT=15
INTERNATIONAL_NEWS_COUNT=10
FINANCE_NEWS_COUNT=10
MAX_HEADLINE_TITLE_LENGTH=10
```

生成预览：

```bash
python main.py --dry-run
```

发送邮件：

```bash
python main.py
```

发送完成后测试邮件会采集真实新闻并发送，不使用静态样例内容：

```bash
python scripts/send_test_email.py
```

如果本机没有 `DEEPSEEK_API_KEY`，测试邮件脚本会仅在测试邮件中使用真实新闻本地压缩摘要；正式 `main.py` 仍严格要求 DeepSeek。

## 目录

```text
daily-news-reader/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── .github/workflows/daily-news.yml
├── modules/
│   ├── date_calculator.py
│   ├── data_collector.py
│   ├── ai_processor.py
│   ├── formatter.py
│   └── email_sender.py
├── templates/
│   └── email_template.html
├── scripts/
│   └── send_test_email.py
├── utils/
│   ├── logger.py
│   ├── retry.py
│   └── validators.py
└── tests/
    ├── test_date_calc.py
    ├── test_formatting.py
    └── test_email.py
```

## 测试

```bash
python -m unittest
```

测试会 mock 外部 RSS、DeepSeek、SMTP 和日期依赖的关键路径，核心格式和错误处理不依赖真实网络。
