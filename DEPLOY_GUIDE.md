# 🚀 Render.com 部署指南

## 📋 部署前检查

✅ 所有文件已准备就绪：

- `app.py` - 应用入口文件
- `paper_db_manager.py` - 数据库管理
- `paper_web_ui.py` - Web 界面
- `requirements.txt` - Python 依赖
- `render.yaml` - Render 配置
- `index.csv` - 示例数据 (292KB, 958 篇论文)

## 第一步：创建 GitHub 仓库

### 1.1 初始化 Git 仓库

```bash
git init
git add .
git commit -m "Initial commit: Paper Database Web App"
```

### 1.2 创建 GitHub 仓库

1. 访问 https://github.com
2. 点击右上角 "+" → "New repository"
3. 仓库名称：`paper-database` (或您喜欢的名称)
4. 设置为 Public
5. 不要初始化 README (我们已经有了)
6. 点击 "Create repository"

### 1.3 推送代码到 GitHub

```bash
git remote add origin https://github.com/您的用户名/paper-database.git
git branch -M main
git push -u origin main
```

## 第二步：注册 Render.com

### 2.1 注册账号

1. 访问 https://render.com
2. 点击 "Get Started for Free"
3. 使用 GitHub 账号登录 (推荐)
4. 授权 Render 访问您的 GitHub

### 2.2 连接 GitHub 仓库

1. 在 Render 控制台点击 "New +"
2. 选择 "Web Service"
3. 选择您刚创建的 GitHub 仓库
4. 点击 "Connect"

## 第三步：配置部署设置

### 3.1 基本设置

- **Name**: `paper-database` (或自定义名称)
- **Environment**: `Python 3`
- **Region**: `Ohio (US East)` (推荐，速度快)
- **Branch**: `main`

### 3.2 构建设置

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:application`

### 3.3 计划选择

- 选择 **Free** 计划
- 注意：免费计划有以下限制
  - 15 分钟无访问会自动休眠
  - 每月 750 小时免费使用
  - 512MB RAM
  - 0.1 CPU

### 3.4 环境变量 (可选)

如需设置环境变量，在 "Environment Variables" 部分添加：

- `PYTHON_VERSION`: `3.11.0`

## 第四步：部署和测试

### 4.1 开始部署

1. 点击 "Create Web Service"
2. 等待部署完成 (通常需要 2-5 分钟)
3. 查看构建日志确认无错误

### 4.2 测试部署

部署完成后，您会得到一个 URL，类似：
`https://paper-database-xxxx.onrender.com`

访问此 URL 测试功能：

- ✅ 首页加载
- ✅ 论文统计显示
- ✅ 搜索功能工作
- ✅ 数据导入成功

## 第五步：自定义域名 (可选)

### 5.1 购买域名

推荐域名商：

- Namecheap (便宜)
- Cloudflare (快速)
- GoDaddy (知名)

### 5.2 配置自定义域名

1. 在 Render 控制台，进入您的服务
2. 点击 "Settings" 标签
3. 滚动到 "Custom Domains"
4. 点击 "Add Custom Domain"
5. 输入您的域名
6. 按照指示配置 DNS 记录

### 5.3 DNS 配置

在您的域名商控制台添加：

- **Type**: CNAME
- **Name**: @ (或 www)
- **Value**: `paper-database-xxxx.onrender.com`
- **TTL**: 3600

## 🔧 故障排除

### 常见问题

**Q: 部署失败**
A: 检查构建日志，通常是依赖问题：

```bash
# 如果pandas安装失败，可以尝试更新requirements.txt
Flask==3.0.3
pandas==2.0.3
gunicorn==21.2.0
```

**Q: 应用启动失败**
A: 检查 Start Command 是否正确：
`gunicorn --bind 0.0.0.0:$PORT app:application`

**Q: 数据库为空**
A: 确认 index.csv 文件已上传且格式正确

**Q: 15 分钟后无法访问**
A: 这是免费计划的限制，重新访问会自动唤醒

### 查看日志

在 Render 控制台的 "Logs" 标签可以查看：

- 构建日志
- 运行日志
- 错误信息

## 🎯 部署后的优化

### 性能优化

1. 启用 Gzip 压缩
2. 静态文件缓存
3. 数据库索引优化

### 安全优化

1. 设置访问限制
2. 添加 HTTPS 重定向
3. 配置安全头

### 监控

1. 设置健康检查
2. 配置告警通知
3. 监控资源使用

## 📞 获取帮助

如果遇到问题：

1. 查看 Render 官方文档
2. 检查构建和运行日志
3. 在 GitHub 仓库创建 Issue
4. 联系技术支持

部署完成后，您就有了一个可以在全球访问的论文数据库管理系统！
