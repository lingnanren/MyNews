const express = require('express');
const n8nService = require('../services/workflow/n8nService');

const router = express.Router();

// 启动新闻处理工作流
router.post('/n8n/start-news-processing', async (req, res) => {
  try {
    const result = await n8nService.startNewsProcessing();
    if (result.success) {
      res.json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 检查n8n服务状态
router.get('/n8n/health', async (req, res) => {
  try {
    const result = await n8nService.checkHealth();
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 获取工作流状态
router.get('/n8n/workflow/:id', async (req, res) => {
  try {
    const result = await n8nService.getWorkflowStatus(req.params.id);
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