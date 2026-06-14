"""
配置文件 - Pollinations API设置
"""

# Pollinations API配置
POLLINATIONS_TOKEN = "eOuQ2QCtd3oCVVX9"  # 你的Pollinations Token

# 使用说明：
# 1. 访问 https://auth.pollinations.ai
# 2. 注册/登录账号
# 3. 获取API Token
# 4. 将Token填入上面的POLLINATIONS_TOKEN变量
# 5. 保存文件

# 示例：
# POLLINATIONS_TOKEN = "pol_1234567890abcdef"

# API设置
POLLINATIONS_BASE_URL = "https://image.pollinations.ai"
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
DEFAULT_MODEL = "flux"
REQUEST_TIMEOUT = 60

# 速率限制设置
RATE_LIMIT_ANONYMOUS = 15  # 匿名用户：15秒/次
RATE_LIMIT_REGISTERED = 5  # 注册用户：5秒/次

print("📋 配置文件已加载")
if POLLINATIONS_TOKEN:
    print(f"✅ Pollinations Token已配置: {POLLINATIONS_TOKEN[:10]}...")
else:
    print("⚠️ 请配置Pollinations Token")
