const express = require('express');
const ttsService = require('../services/tts/ttsService');

const router = express.Router();

// 为指定新闻生成语音
router.post('/speech/:newsId', async (req, res) => {
  try {
    const result = await ttsService.generateSpeech(req.params.newsId);
    if (result.success) {
      res.json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 批量生成语音
router.post('/speech/batch', async (req, res) => {
  try {
    const { newsIds } = req.body;
    if (!Array.isArray(newsIds)) {
      return res.status(400).json({ success: false, error: 'newsIds必须是数组' });
    }
    
    const result = await ttsService.batchGenerateSpeech(newsIds);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 为已处理的新闻生成语音
router.post('/speech/process-processed', async (req, res) => {
  try {
    const limit = req.query.limit || 10;
    const result = await ttsService.generateSpeechForProcessedNews(limit);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 删除语音文件
router.delete('/speech/:newsId', async (req, res) => {
  try {
    const result = await ttsService.deleteSpeech(req.params.newsId);
    if (result.success) {
      res.json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;