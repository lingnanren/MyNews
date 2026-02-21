const express = require('express');
const aiService = require('../services/ai/aiService');

const router = express.Router();

// 生成单个新闻摘要
router.post('/summary/:newsId', async (req, res) => {
  try {
    const result = await aiService.generateSummary(req.params.newsId);
    if (result.success) {
      res.json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 批量生成新闻摘要
router.post('/summary/batch', async (req, res) => {
  try {
    const { newsIds } = req.body;
    if (!Array.isArray(newsIds)) {
      return res.status(400).json({ success: false, error: 'newsIds必须是数组' });
    }
    
    const result = await aiService.batchGenerateSummary(newsIds);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 处理未处理的新闻
router.post('/summary/process-unprocessed', async (req, res) => {
  try {
    const limit = req.query.limit || 10;
    const result = await aiService.processUnprocessedNews(limit);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;