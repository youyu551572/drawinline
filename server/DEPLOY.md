# YouYu 中转服务器 - 部署指南

## 🆓 方案：Render 免费部署（推荐）

### 1. 注册
- 打开 https://render.com
- 用 GitHub 账号登录（免费额度 750 小时/月）

### 2. 推送代码到 GitHub
把你 server/ 目录推送到 GitHub 仓库

### 3. 一键部署
在 Render 控制台 → New Web Service → 选择你的 GitHub 仓库 →
填入以下环境变量（替换为你的真实值）：

| 变量 | 说明 |
|------|------|
| `API_KEY` | 客户端-服务器共享密钥 |
| `ADMIN_KEY` | 管理接口密钥 |
| `SMTP_USER` | QQ邮箱地址 |
| `SMTP_PASS` | QQ邮箱授权码 |
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `GITEE_TOKEN` | Gitee Personal Access Token |
| `SECRET_KEY` | Flask 内部密钥 |
| `SMTP_HOST` | smtp.qq.com |
| `SMTP_PORT` | 465 |
| `GITHUB_REPO` | youyu551572/drawinline |
| `GITEE_REPO` | youyu551572/drawinline |

Render 会给你一个域名如 `https://youyu-drawinline.onrender.com`

### 4. 客户端配置
```python
# config.py
API_SERVER_URL = "https://youyu-drawinline.onrender.com"
API_KEY = "你的API_KEY"  # 必须与服务器一致
```

---

## 方案 B：AWS Serverless（$0 费用）
见 `server/serverless.yml`，需安装 Serverless Framework。

## 方案 C：VPS 自托管
```bash
cd server
pip install -r requirements.txt
gunicorn server:app -w 2 -b 0.0.0.0:5000
```
