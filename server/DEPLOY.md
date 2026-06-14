# YouYu 中转服务器 - 部署指南

## 🆓 方案：Render 免费部署（推荐）

### 1. 注册
- 打开 https://render.com
- 用 GitHub 账号登录（免费额度 750 小时/月）

### 2. 推送代码到 GitHub
```bash
git init
git add server/
git commit -m "添加中转服务器"
git push origin main
```

### 3. 一键部署
在 Render 控制台 → New Web Service → 选择你的 GitHub 仓库 →
填入以下环境变量（敏感信息手动填）：

| 变量 | 值 |
|------|-----|
| `API_KEY` | `49b21a17b98efad1166961a1ec4724058dede9652357f4c3f10018c7c024b2b7` |
| `ADMIN_KEY` | `678355bba4144b4446975b5ad8ed8127` |
| `SMTP_USER` | `agbzzvee51g@foxmail.com` |
| `SMTP_PASS` | `ijlhidpydirdebeb` |
| `GITHUB_TOKEN` | `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` |
| `GITEE_TOKEN` | `e5114aa8afca63e7c13a35d3dfdc701b` |
| `SECRET_KEY` | `2f8318055a2a751e983e849d2fcd8b0fc980207d28f15e5fa909f6b6d946547d` |

Render 会给你一个域名如 `https://youyu-drawinline.onrender.com`

### 4. 客户端配置
```python
# config.py
API_SERVER_URL = "https://youyu-drawinline.onrender.com"
API_KEY = "49b21a17b98efad1166961a1ec4724058dede9652357f4c3f10018c7c024b2b7"
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
