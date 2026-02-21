const { News } = require('./src/models');
const { sequelize } = require('./src/config/database');

async function addTestNews() {
  try {
    // 测试新闻数据
    const testNews = [
      {
        title: '2024年经济展望：全球经济增长预期上调',
        content: '国际货币基金组织(IMF)最新报告显示，2024年全球经济增长预期从3.2%上调至3.5%。报告指出，美国经济表现强于预期，中国经济复苏势头良好，欧洲经济逐步走出通胀阴影，成为全球经济增长的三大引擎。同时，新兴市场和发展中经济体增长预期也有所上调，预计将达到4.8%。IMF警告称，全球经济仍面临地缘政治冲突、通胀压力和金融市场波动等风险，政策制定者需保持警惕。',
        summary: '国际货币基金组织(IMF)上调2024年全球经济增长预期至3.5%，美国、中国和欧洲成为增长引擎。新兴市场预计增长4.8%，但仍面临地缘政治冲突、通胀和金融市场波动等风险。',
        url: 'https://example.com/news/1',
        source: '财经日报',
        category: '财经',
        publishedAt: new Date(),
        isProcessed: true
      },
      {
        title: '我国新型驱逐舰下水，海军实力再提升',
        content: '我国自主设计建造的新型驱逐舰今日在某造船厂正式下水。该驱逐舰采用了多项先进技术，包括新型相控阵雷达、综合电力系统和新一代舰载武器系统，具备更强的防空、反导、反潜和对海打击能力。军事专家表示，该型驱逐舰的服役将显著提升我国海军的远洋作战能力，为维护国家海洋权益提供更有力的保障。',
        summary: '我国自主设计建造的新型驱逐舰正式下水，采用多项先进技术，包括新型相控阵雷达、综合电力系统和新一代舰载武器系统，将显著提升海军远洋作战能力。',
        url: 'https://example.com/news/2',
        source: '军事新闻',
        category: '军事',
        publishedAt: new Date(),
        isProcessed: true
      },
      {
        title: '健康生活新趋势：城市公园成为市民休闲首选',
        content: '随着人们健康意识的提高，城市公园成为越来越多市民休闲娱乐的首选场所。数据显示，周末城市公园的客流量比去年同期增长了30%以上。各地政府也加大了对城市公园的建设和改造力度，增加了健身设施、休息区域和文化活动空间。专家建议，市民应保持每周至少3次、每次30分钟以上的户外活动，以提高身体素质和心理健康水平。',
        summary: '城市公园成为市民休闲娱乐首选，周末客流量增长30%以上。各地政府加大公园建设力度，专家建议每周至少3次、每次30分钟以上户外活动。',
        url: 'https://example.com/news/3',
        source: '生活资讯',
        category: '生活',
        publishedAt: new Date(),
        isProcessed: true
      },
      {
        title: '人工智能技术在医疗领域取得重大突破',
        content: '近日，研究人员开发的人工智能系统在医学影像诊断方面取得重大突破。该系统能够准确识别多种癌症的早期病变，准确率达到95%以上，超过了人类专家的平均水平。此外，AI技术在药物研发、个性化治疗方案制定和医院管理等方面也展现出巨大潜力。专家预测，未来5年内，AI将成为医疗领域的重要工具，显著提高医疗效率和诊疗效果。',
        summary: 'AI系统在医学影像诊断方面取得重大突破，癌症早期病变识别准确率超95%，超过人类专家水平。AI在药物研发、个性化治疗和医院管理等方面也展现巨大潜力。',
        url: 'https://example.com/news/4',
        source: '科技新闻',
        category: '科技',
        publishedAt: new Date(),
        isProcessed: true
      }
    ];

    // 添加测试新闻
    for (const news of testNews) {
      await News.create(news);
      console.log(`添加测试新闻: ${news.title}`);
    }

    console.log('测试新闻添加完成！');
  } catch (error) {
    console.error('添加测试新闻失败:', error);
  } finally {
    await sequelize.close();
  }
}

// 运行脚本
addTestNews();