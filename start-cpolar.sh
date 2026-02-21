#!/bin/bash

# Cpolar 启动脚本

# 检查环境变量
if [ -z "$CPOLAR_AUTHTOKEN" ]; then
  echo "错误: 未设置 CPOLAR_AUTHTOKEN 环境变量"
  exit 1
fi

# 配置 Cpolar 认证
cpolar authtoken $CPOLAR_AUTHTOKEN

# 启动 Cpolar 隧道，映射本地 3000 端口
echo "启动 Cpolar 隧道，映射本地 3000 端口..."
cpolar http 3000