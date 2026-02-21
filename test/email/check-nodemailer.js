const nodemailer = require('nodemailer');

console.log('Nodemailer version:', require('nodemailer/package.json').version);
console.log('Nodemailer object:', Object.keys(nodemailer));
console.log('createTransporter exists:', typeof nodemailer.createTransporter === 'function');

// 测试基本功能
if (typeof nodemailer.createTransporter === 'function') {
  console.log('createTransporter is a function');
} else {
  console.log('createTransporter is not a function');
  console.log('Nodemailer object:', nodemailer);
}