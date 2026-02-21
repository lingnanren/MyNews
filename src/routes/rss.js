const express = require('express');
const rssService = require('../services/rss/rssService');

const router = express.Router();

// 获取所有RSS源
router.get('/sources', async (req, res) => {
  try {
    const sources = await rssService.getAllSources();
    res.json({ success: true, sources });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 添加RSS源
router.post('/sources', async (req, res) => {
  try {
    const result = await rssService.addSource(req.body);
    if (result.success) {
      res.status(201).json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 更新RSS源
router.put('/sources/:id', async (req, res) => {
  try {
    const result = await rssService.updateSource(req.params.id, req.body);
    if (result.success) {
      res.json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 删除RSS源
router.delete('/sources/:id', async (req, res) => {
  try {
    const result = await rssService.deleteSource(req.params.id);
    if (result.success) {
      res.json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 抓取单个RSS源
router.post('/sources/:id/fetch', async (req, res) => {
  try {
    const result = await rssService.fetchRssSource(req.params.id);
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 抓取所有RSS源
router.post('/sources/fetch-all', async (req, res) => {
  try {
    const result = await rssService.fetchAllRssSources();
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;