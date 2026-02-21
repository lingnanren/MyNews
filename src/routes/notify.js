const express = require('express');
const emailService = require('../services/notify/emailService');

const router = express.Router();

// 发送邮件给指定用户
router.post('/email/:userId', async (req, res) => {
  try {
    const result = await emailService.sendEmail(req.params.userId);
    if (result.success) {
      res.json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 发送测试邮件
router.post('/email/test', async (req, res) => {
  try {
    const { toEmail } = req.body;
    if (!toEmail) {
      return res.status(400).json({ success: false, error: '缺少目标邮箱' });
    }
    
    const result = await emailService.sendTestEmail(toEmail);
    if (result.success) {
      res.json(result);
    } else {
      res.status(400).json(result);
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 批量发送邮件给所有激活用户
router.post('/email/all', async (req, res) => {
  try {
    const result = await emailService.sendEmailToAllUsers();
    res.json(result);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;