# Pollinations.AI 官方API完整指南

## 📚 项目信息

**GitHub**: https://github.com/pollinations/pollinations  
**官方文档**: https://github.com/pollinations/pollinations/blob/master/APIDOCS.md  
**认证平台**: https://auth.pollinations.ai

---

## 🎯 核心特点

### ✅ 优势

1. **完全开源**
   - MIT许可证
   - 社区驱动
   - 透明可信

2. **真正免费**
   - 匿名可用
   - 无需API Key（基础使用）
   - 无需信用卡

3. **简单易用**
   - 单个URL即可生成
   - RESTful API
   - 支持多种语言

4. **功能丰富**
   - 图片生成
   - 文本生成
   - 音频生成
   - 多模态支持

---

## 📊 速率限制详情

### 访问层级

| 层级 | 速率限制 | 可用模型 | 注册要求 | 费用 | 水印 |
|------|---------|----------|----------|------|------|
| **Anonymous** | 15秒/次 | 基础模型 | 无需注册 | 免费 | 2025.3.31后有 |
| **Seed** | 5秒/次 | 标准模型 | 免费注册 | 免费 | 无 |
| **Flower** | 3秒/次 | 高级模型 | 付费 | 付费 | 无 |
| **Nectar** | 无限制 | 所有模型 | 企业 | 联系官方 | 无 |

### 关键信息

**匿名使用**:
- ✅ 完全免费
- ⚠️ 15秒只能生成1张
- ⚠️ 2025年3月31日后会有水印

**注册使用** (推荐):
- ✅ 完全免费
- ✅ 5秒可生成1张（提升3倍）
- ✅ 无水印
- ✅ 注册地址: https://auth.pollinations.ai

---

## 🎨 图片生成API

### 基础用法

**端点**: `GET https://image.pollinations.ai/prompt/{prompt}`

**最简单的例子**:
```
https://image.pollinations.ai/prompt/a cute cat
```

### 参数说明

| 参数 | 类型 | 说明 | 默认值 | 示例 |
|------|------|------|--------|------|
| `prompt` | string | 图片描述（必需） | - | "a cute cat" |
| `model` | string | AI模型 | flux | turbo, flux |
| `width` | integer | 宽度（像素） | 1024 | 512, 1920 |
| `height` | integer | 高度（像素） | 1024 | 512, 1080 |
| `seed` | integer | 随机种子 | random | 12345 |
| `nologo` | boolean | 移除水印（需注册） | false | true |
| `enhance` | boolean | AI优化提示词 | false | true |
| `private` | boolean | 不显示在公开feed | false | true |

### Python示例

```python
import requests
from urllib.parse import quote

def generate_image(prompt, width=512, height=512):
    """使用Pollinations生成图片"""
    # URL编码提示词
    encoded_prompt = quote(prompt)
    
    # 构建URL
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    
    # 添加参数
    params = {
        'width': width,
        'height': height,
        'model': 'flux',
        'nologo': 'true'  # 需要注册才能生效
    }
    
    try:
        # 发送请求（60秒超时）
        response = requests.get(url, params=params, timeout=60)
        
        if response.status_code == 200:
            # 保存图片
            with open('generated.png', 'wb') as f:
                f.write(response.content)
            return True, 'generated.png'
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

# 使用示例
success, result = generate_image("a cute cat drawing")
if success:
    print(f"✅ 图片已保存: {result}")
else:
    print(f"❌ 生成失败: {result}")
```

---

## 🔑 认证方式

### 方式1: 匿名使用（无需认证）

**优点**:
- ✅ 无需注册
- ✅ 立即可用

**缺点**:
- ⚠️ 15秒/次（很慢）
- ⚠️ 2025年3月后有水印

**适用场景**: 测试、低频使用

### 方式2: Referrer认证（Web应用）

**用法**:
```
https://image.pollinations.ai/prompt/landscape?referrer=myapp.com
```

**优点**:
- ✅ 浏览器自动发送
- ✅ 适合前端应用

**缺点**:
- ⚠️ 仍有速率限制

### 方式3: Bearer Token（推荐）

**获取Token**:
1. 访问 https://auth.pollinations.ai
2. 注册/登录
3. 获取Token

**使用Token**:
```python
headers = {
    'Authorization': 'Bearer YOUR_TOKEN'
}
response = requests.get(url, headers=headers)
```

**优点**:
- ✅ 5秒/次（提升3倍）
- ✅ 无水印
- ✅ 完全免费

---

## 💡 实用建议

### 1. 提示词优化

**基础提示词**:
```
"a cat"
```

**优化后**:
```
"a cute cat, simple line drawing, black and white, minimalist style, sketch"
```

**技巧**:
- 添加风格描述
- 指定颜色方案
- 说明细节程度

### 2. 速率限制处理

**策略A: 缓存**
```python
import hashlib
import os

def get_cached_or_generate(prompt):
    # 生成缓存文件名
    cache_key = hashlib.md5(prompt.encode()).hexdigest()
    cache_file = f"cache/{cache_key}.png"
    
    # 检查缓存
    if os.path.exists(cache_file):
        return True, cache_file
    
    # 生成新图片
    success, result = generate_image(prompt)
    
    # 保存到缓存
    if success:
        os.rename(result, cache_file)
        return True, cache_file
    
    return False, result
```

**策略B: 队列**
```python
import time
from queue import Queue

class PollinationsQueue:
    def __init__(self, interval=15):
        self.interval = interval  # 15秒间隔
        self.last_request = 0
        self.queue = Queue()
    
    def generate(self, prompt):
        # 计算需要等待的时间
        elapsed = time.time() - self.last_request
        if elapsed < self.interval:
            wait_time = self.interval - elapsed
            print(f"⏳ 等待 {wait_time:.1f} 秒...")
            time.sleep(wait_time)
        
        # 生成图片
        result = generate_image(prompt)
        self.last_request = time.time()
        return result
```

### 3. 错误处理

```python
def robust_generate(prompt, max_retries=3):
    """带重试的生成"""
    for i in range(max_retries):
        try:
            success, result = generate_image(prompt)
            if success:
                return True, result
            
            # 如果是速率限制，等待后重试
            if "429" in str(result):
                print(f"⏳ 速率限制，等待15秒...")
                time.sleep(15)
                continue
            
            return False, result
        except Exception as e:
            if i < max_retries - 1:
                print(f"⚠️ 重试 {i+1}/{max_retries}...")
                time.sleep(5)
            else:
                return False, str(e)
```

---

## 🚀 集成到项目

### 方案1: 简单集成（匿名）

**优点**: 无需配置
**缺点**: 15秒/次

```python
# ai_generator.py
def generate_image(self, prompt):
    # 尝试Pollinations
    try:
        return self._generate_pollinations(prompt)
    except:
        # 失败回退到本地
        return self._generate_local(prompt)
```

### 方案2: 注册集成（推荐）

**优点**: 5秒/次，无水印
**缺点**: 需要一次性注册

```python
# config.py
POLLINATIONS_TOKEN = "your_token_here"  # 从 auth.pollinations.ai 获取

# ai_generator.py
def generate_image(self, prompt):
    headers = {}
    if POLLINATIONS_TOKEN:
        headers['Authorization'] = f'Bearer {POLLINATIONS_TOKEN}'
    
    response = requests.get(url, headers=headers, timeout=60)
    # ...
```

### 方案3: 混合方案（最佳）

**策略**: 常见图形用本地，复杂图形用API

```python
def generate_image(self, prompt):
    # 常见图形列表
    common_keywords = ['猫', '狗', '老鼠', '房子', '花', '树']
    
    # 判断是否为常见图形
    is_common = any(kw in prompt for kw in common_keywords)
    
    if is_common:
        # 常见图形：高质量本地生成（瞬间完成）
        return self._generate_local_advanced(prompt)
    else:
        # 复杂图形：尝试API
        try:
            return self._generate_pollinations(prompt)
        except:
            # API失败：回退到本地
            return self._generate_local_advanced(prompt)
```

---

## 📊 性能对比

### 速度对比

| 方案 | 首次生成 | 缓存命中 | 连续生成 |
|------|---------|----------|----------|
| **本地生成** | <0.1秒 | <0.1秒 | 无限制 |
| Pollinations匿名 | 2-5秒 | 2-5秒 | 15秒/次 |
| Pollinations注册 | 2-5秒 | 2-5秒 | 5秒/次 |
| 混合方案 | <0.1秒 | <0.1秒 | 智能选择 |

### 质量对比

| 方案 | 常见图形 | 复杂图形 | 自定义内容 |
|------|---------|----------|-----------|
| **本地生成** | ⭐⭐⭐⭐ | ⭐⭐ | ❌ |
| Pollinations | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 混合方案 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 推荐方案

### 当前最佳实践

**阶段1: 立即可用**
- 使用改进的高质量本地生成器
- 12种精美图形
- 瞬间生成，100%可靠

**阶段2: 提升质量（可选）**
- 注册Pollinations（免费）
- 获取Token
- 5秒/次，无水印

**阶段3: 混合方案（推荐）**
- 常见图形：本地生成（快速）
- 复杂图形：Pollinations（高质量）
- 最佳用户体验

---

## 📝 总结

### Pollinations.AI 评价

| 特性 | 评分 | 说明 |
|------|------|------|
| **免费程度** | ⭐⭐⭐⭐⭐ | 真正免费，注册也免费 |
| **易用性** | ⭐⭐⭐⭐⭐ | 单个URL即可 |
| **稳定性** | ⭐⭐⭐ | 有时会500错误 |
| **速率限制** | ⭐⭐⭐ | 匿名15秒，注册5秒 |
| **图片质量** | ⭐⭐⭐⭐⭐ | 非常高 |
| **文档质量** | ⭐⭐⭐⭐⭐ | 详细清晰 |
| **社区支持** | ⭐⭐⭐⭐ | 活跃的GitHub |

### 最终建议

1. **现在**: 使用高质量本地生成器（已集成）
2. **可选**: 注册Pollinations获取Token
3. **未来**: 实现混合方案（最佳体验）

**Pollinations是目前最好的免费AI生图API，值得集成！** 🎉
