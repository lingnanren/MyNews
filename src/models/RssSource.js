const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const RssSource = sequelize.define('RssSource', {
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  url: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  },
  category: {
    type: DataTypes.STRING,
    allowNull: false
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  lastFetched: {
    type: DataTypes.DATE
  }
}, {
  tableName: 'rss_sources',
  timestamps: true
});

module.exports = RssSource;