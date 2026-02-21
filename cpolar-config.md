# Cpolar 内网穿透配置

## 什么是 Cpolar

Cpolar 是一个强大的内网穿透工具，可以将本地运行的服务暴露到公网，使您可以通过公网地址访问本地服务。

## 安装 Cpolar

### macOS

```bash
# 使用 Homebrew 安装
brew install cpolar

# 或者下载安装包
# 访问 https://www.cpolar.com/download 下载对应版本
```

### Windows

访问 https://www.cpolar.com/download 下载安装包，双击安装。

### Linux

```bash
# 下载安装包
curl -L https://www.cpolar.com/static/downloads/install-release-cpolar.sh | sudo bash

# 或者使用包管理器
# 参考官方文档：https://www.cpolar.com/docs
```

## 配置 Cpolar

### 1. 注册并登录 Cpolar

1. 访问 https://www.cpolar.com/ 注册账号
2. 登录后，在后台获取认证令牌
3. 执行以下命令进行认证：

```bash
cpolar authtoken <您的认证令牌>
```

### 2. 启动 MyNews 服务

在启动 Cpolar 之前，确保 MyNews 服务已经运行：

```bash
# 启动 MyNews 服务
npm start
```

### 3. 配置 Cpolar 隧道

#### 临时隧道（每次需要手动启动）

```bash
# 映射本地 3000 端口到公网
cpolar http 3000
```

执行后，Cpolar 会生成一个公网地址，类似：
```
https://xxxxxx.cpolar.top
```

您可以使用这个地址访问 MyNews 服务。

#### 永久隧道（推荐）

1. 编辑 Cpolar 配置文件：

```bash
# macOS/Linux
vim ~/.cpolar/cpolar.yml

# Windows
# 编辑 C:\Users\<用户名>\.cpolar\cpolar.yml
```

2. 添加以下配置：

```yaml
auth_token: <您的认证令牌>

 tunnels:
   mynews:
     addr: 3000
     proto: http
     subdomain: mynews
     region: cn_vip
```

3. 启动 Cpolar 服务：

```bash
# macOS/Linux
sudo systemctl start cpolar

# Windows
# 在服务管理中启动 Cpolar 服务
```

4. 查看隧道状态：

```bash
cpolar status
```

## 访问 MyNews 服务

配置完成后，您可以通过以下方式访问 MyNews 服务：

1. **本地访问**：`http://localhost:3000`
2. **公网访问**：`https://<您的子域名>.cpolar.top`

## 注意事项

1. **免费版限制**：Cpolar 免费版有流量和连接数限制，且公网地址会定期变化
2. **安全设置**：建议在生产环境中配置防火墙和访问控制
3. **服务稳定性**：确保 MyNews 服务和 Cpolar 服务保持运行状态
4. **域名配置**：如果需要固定域名，可以考虑使用 Cpolar 专业版或配置自定义域名

## 故障排查

### 无法访问公网地址

1. 检查 MyNews 服务是否正常运行：`curl http://localhost:3000`
2. 检查 Cpolar 服务是否正常运行：`cpolar status`
3. 检查网络连接是否正常
4. 检查防火墙设置是否阻止了 Cpolar 连接

### 公网地址变化

- 免费版 Cpolar 的公网地址会定期变化，建议使用专业版获取固定地址
- 或者使用动态 DNS 服务配合 Cpolar 使用

## 更多配置

详细的 Cpolar 配置选项请参考官方文档：https://www.cpolar.com/docs