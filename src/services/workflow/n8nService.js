const axios = require('axios');
const config = require('../../config');

class N8nService {
  constructor() {
    this.n8nUrl = process.env.N8N_URL || 'http://localhost:5678';
    this.apiKey = process.env.N8N_API_KEY;
  }
  
  // 启动n8n工作流
  async triggerWorkflow(workflowId) {
    try {
      const response = await axios.post(
        `${this.n8nUrl}/api/v1/workflows/${workflowId}/trigger`,
        {},
        {
          headers: {
            'Content-Type': 'application/json',
            'X-N8N-API-KEY': this.apiKey
          }
        }
      );
      
      console.log('工作流触发成功:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('触发工作流失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 获取工作流状态
  async getWorkflowStatus(workflowId) {
    try {
      const response = await axios.get(
        `${this.n8nUrl}/api/v1/workflows/${workflowId}`,
        {
          headers: {
            'X-N8N-API-KEY': this.apiKey
          }
        }
      );
      
      return { success: true, data: response.data };
    } catch (error) {
      console.error('获取工作流状态失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 启动新闻处理工作流
  async startNewsProcessing() {
    try {
      // 这里使用配置的工作流ID，实际项目中需要根据具体情况调整
      const workflowId = 'news-processing-workflow';
      const result = await this.triggerWorkflow(workflowId);
      return result;
    } catch (error) {
      console.error('启动新闻处理工作流失败:', error);
      return { success: false, error: error.message };
    }
  }
  
  // 检查n8n服务是否可用
  async checkHealth() {
    try {
      const response = await axios.get(`${this.n8nUrl}/healthz`);
      return { success: true, status: response.status };
    } catch (error) {
      console.error('n8n服务不可用:', error);
      return { success: false, error: error.message };
    }
  }
}

module.exports = new N8nService();