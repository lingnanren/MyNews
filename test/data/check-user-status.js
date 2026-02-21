const { User } = require('./src/models');
const { sequelize } = require('./src/config/database');

async function checkUserStatus() {
  try {
    // 查询所有用户
    const users = await User.findAll();
    console.log('数据库中的用户:');
    users.forEach(user => {
      console.log(`ID: ${user.id}, 邮箱: ${user.email}, 激活状态: ${user.isActive}`);
    });
  } catch (error) {
    console.error('检查用户状态失败:', error);
  } finally {
    await sequelize.close();
  }
}

// 运行脚本
checkUserStatus();