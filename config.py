"""
配置文件 - API 密钥设置
⚠️ 此文件打包进 exe，不要放真实敏感密钥
"""

import os

# ==============================
# Hugging Face API配置 (主要使用)
# ==============================

# 请替换为你的Hugging Face Token
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# 获取Token的步骤：
# 1. 访问 https://huggingface.co/join 注册账号
# 2. 登录后访问 https://huggingface.co/settings/tokens
# 3. 点击 "New token" 创建新Token
# 4. 复制Token并粘贴到上面的HUGGINGFACE_TOKEN变量中
# 5. 保存文件

# 示例（请替换为你自己的Token）：
# HUGGINGFACE_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ==============================
# 硅基流动 SiliconFlow API配置 (国内最佳，强烈推荐！)
# ==============================

# 硅基流动 API Key (注册送14元，FLUX.1-schnell永久免费)
SILICONFLOW_API_KEY = os.environ.get("SILICONFLOW_API_KEY", "")

# 获取API Key步骤：
# 1. 访问 https://cloud.siliconflow.cn 注册账号
# 2. 点击左侧 "API密钥" -> "新建密钥"
# 3. 复制 sk-开头的密钥
# 4. 粘贴到上面的SILICONFLOW_API_KEY变量中

# 优势：
# ✅ 国内服务器，速度极快（秒级响应）
# ✅ 不需要代理/VPN
# ✅ 免费使用FLUX.1-schnell模型（永久免费）
# ✅ 注册送14元余额
# ✅ 支持中文提示词
# ✅ 多种模型可选（FLUX, Kolors, Qwen等）

# 可用模型列表（全部免费）：
# - black-forest-labs/FLUX.1-schnell (推荐，永久免费)
# - Kwai-Kolors/Kolors (快手可图，免费！支持中英文，中文效果优秀)

# ==============================
# Replicate API配置 (高质量备用)
# ==============================

# Replicate API Token (有免费额度)
REPLICATE_TOKEN = "YOUR_REPLICATE_TOKEN"

# 获取Token步骤：
# 1. 访问 https://replicate.com/account/api-tokens
# 2. 注册账号并创建API Token
# 3. 复制Token到上面的变量中

# ==============================
# Google API配置 (备用，权限受限)
# ==============================

# Google AI Studio API Key（目前无Imagen权限）
GOOGLE_API_KEY = ""

# ==============================
# Auth (SMTP + GitHub) — 全部改为环境变量，默认空
# ==============================
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "youyu551572/drawinline")
GITEE_TOKEN = os.environ.get("GITEE_TOKEN", "")
GITEE_REPO = os.environ.get("GITEE_REPO", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

# ==============================
# 中转服务器配置（推荐）
# 配置后自动将敏感操作（SMTP/数据存储）交给服务器处理
# 客户端不再暴露 GitHub/SMTP 密钥
# ==============================

# 服务器地址（部署后填写）
# 本地测试: http://127.0.0.1:5000
# 生产环境: https://your-server.com
API_SERVER_URL = "http://127.0.0.1:5000"

# 客户端-服务器共享密钥（必须与服务器端的 API_KEY 一致）
# 生成方式: python -c "import secrets; print(secrets.token_hex(32))"
API_KEY = "49b21a17b98efad1166961a1ec4724058dede9652357f4c3f10018c7c024b2b7"

# ==============================
# Network config
# ==============================

# ⚠️ 国内用户必读：
# Hugging Face在国内需要代理访问，系统已自动配置代理 127.0.0.1:7890
# 如果你的代理端口不是7890，请确认你的VPN/代理软件设置：
# - Clash: 通常是7890
# - V2ray: 可能是1080或其他
# - 请确保代理软件开启并允许本地连接

# ==============================
# 使用说明
# ==============================

# 1. 安装依赖库:
#    pip install requests pillow

# 2. 配置API Key（见上方）

# 3. 运行测试:
#    python google_imagen_generator.py

# 4. 运行主程序:
#    python modern_main.py

# 5. 直接输入中文提示词，无需翻译！
#    例如: "小猫", "可爱的小狗", "打篮球"

# ==============================
# 技术支持
# ==============================

# Google AI Studio: https://aistudio.google.com
# API文档: https://ai.google.dev/docs
# 问题反馈: 查看 docs/Google_Imagen配置指南.md
