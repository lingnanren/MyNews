const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const User = sequelize.define('User', {
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true
  },
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  },
  interests: {
    type: DataTypes.STRING,
    allowNull: false,
    defaultValue: '财经,军事,生活,科技'
  },
  pushTime: {
    type: DataTypes.STRING,
    allowNull: false,
    defaultValue: '08:00'
  },
  pushMethod: {
    type: DataTypes.STRING,
    allowNull: false,
    defaultValue: 'email'
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  }
}, {
  tableName: 'users',
  timestamps: true
});

module.exports = User;