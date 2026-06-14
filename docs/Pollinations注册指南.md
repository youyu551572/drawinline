# Pollinations.AI 注册指南

## 🎯 注册步骤

### 第1步：访问注册页面
**网址**: https://auth.pollinations.ai

### 第2步：选择注册方式

**推荐方式**:
1. **GitHub账号** (最简单)
   - 点击 "Continue with GitHub"
   - 授权Pollinations访问你的GitHub
   - 自动完成注册

2. **Google账号**
   - 点击 "Continue with Google"
   - 选择Google账号
   - 授权后完成注册

3. **邮箱注册**
   - 输入邮箱地址
   - 设置密码
   - 验证邮箱

### 第3步：获取API Token

**注册成功后**:
1. 进入Dashboard页面
2. 找到 "API Keys" 或 "Tokens" 部分
3. 点击 "Generate New Token" 或 "Create Token"
4. 复制生成的Token（格式类似：`pol_xxxxxxxxxx`）

### 第4步：配置Token

**在项目中配置**:
1. 打开 `config.py` 文件
2. 找到这一行：
   ```python
   POLLINATIONS_TOKEN = ""
   ```
3. 将Token填入引号中：
   ```python
   POLLINATIONS_TOKEN = "pol_你的token"
   ```
4. 保存文件

---

## ✅ 注册后的优势

### 速率限制对比

| 状态 | 速率限制 | 水印 | 费用 |
|------|---------|------|------|
| **匿名** | 15秒/次 | 2025.3.31后有 | 免费 |
| **注册** | 5秒/次 | 无 | 免费 |

### 提升效果
- ✅ **速度提升3倍**: 15秒 → 5秒
- ✅ **无水印**: 图片更干净
- ✅ **完全免费**: 注册不收费
- ✅ **更稳定**: 注册用户优先级更高

---

## 🧪 测试配置

### 方法1：运行测试脚本
```bash
python pollinations_generator.py
```

### 方法2：在主程序中测试
```bash
python modern_main.py
```
然后在AI生图功能中输入复杂提示词，如：
- "一只在太空中飞行的独角兽"
- "赛博朋克风格的城市夜景"

---

## 🔧 配置文件说明

### config.py 完整配置
```python
# Pollinations API配置
POLLINATIONS_TOKEN = "pol_你的token"  # 在这里填入Token

# API设置
POLLINATIONS_BASE_URL = "https://image.pollinations.ai"
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
DEFAULT_MODEL = "flux"
REQUEST_TIMEOUT = 60

# 速率限制设置
RATE_LIMIT_ANONYMOUS = 15  # 匿名用户：15秒/次
RATE_LIMIT_REGISTERED = 5  # 注册用户：5秒/次
```

---

## 🚀 使用效果

### 混合生成策略

**常见图形** (猫、狗、房子等):
- ✅ 使用本地生成器
- ✅ 瞬间完成
- ✅ 无限制

**复杂图形** (任意描述):
- ✅ 使用Pollinations API
- ✅ 高质量生成
- ✅ 5秒完成（注册后）

### 示例对比

| 提示词 | 生成方式 | 速度 | 质量 |
|--------|---------|------|------|
| "小猫简笔画" | 本地生成 | <0.1秒 | ⭐⭐⭐⭐ |
| "赛博朋克城市" | Pollinations | 5秒 | ⭐⭐⭐⭐⭐ |
| "独角兽在太空" | Pollinations | 5秒 | ⭐⭐⭐⭐⭐ |

---

## ❓ 常见问题

### Q: 注册是否收费？
**A**: 完全免费！Seed层级（注册用户）永久免费。

### Q: Token会过期吗？
**A**: 正常情况下不会过期，除非你主动删除。

### Q: 如果不注册会怎样？
**A**: 仍可使用，但速度慢（15秒/次），且2025年3月后有水印。

### Q: 注册失败怎么办？
**A**: 
1. 检查网络连接
2. 尝试不同的注册方式
3. 清除浏览器缓存
4. 使用匿名模式（仍可正常使用）

### Q: Token配置错误怎么办？
**A**: 
1. 检查Token格式（应以`pol_`开头）
2. 确保没有多余的空格
3. 重新生成Token
4. 如果还是不行，留空使用匿名模式

---

## 🎉 完成！

**注册完成后，你将获得**:
- ✅ 3倍速度提升（5秒/次）
- ✅ 无水印高质量图片
- ✅ 混合生成的最佳体验
- ✅ 常见图形瞬间生成
- ✅ 复杂图形高质量生成

**现在就去注册吧！** 🚀
