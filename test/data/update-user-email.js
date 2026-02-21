const { User } = require('./src/models');
const { sequelize } = require('./src/config/database');

async function updateUserEmail() {
  try {
    // 更新默认用户的邮箱地址
    const user = await User.findOne({ where: { email: 'user@example.com' } });
    if (user) {
      await user.update({ email: 'yza15@qq.com' });
      console.log('用户邮箱已更新为: yza15@qq.com');
    } else {
      console.log('未找到默认用户，创建新用户');
      await User.create({
        email: 'yza15@qq.com',
        interests: '财经,军事,生活,科技',
        pushTime: '08:00',
        pushMethod: 'email',
        isActive: true
      });
      console.log('新用户已创建，邮箱: yza15@qq.com');
    }
  } catch (error) {
    console.error('更新用户邮箱失败:', error);
  } finally {
    await sequelize.close();
  }
}

// 运行脚本
updateUserEmail();