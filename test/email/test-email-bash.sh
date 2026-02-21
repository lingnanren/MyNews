#!/bin/bash

# 直接使用bash运行，避免zsh的交互式提示
export ZSH_DISABLE_COMPFIX=true

# 加载nvm
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# 使用node 18
nvm use 18

# 运行邮件测试脚本
node test-email-noninteractive.js