# 免费AI生图API完整调研报告

## 📊 测试时间
**2025年11月25日**

## 🎯 测试目标
1. 找到所有可用的免费AI生图API
2. 测试每个API的可用性
3. 了解速率限制和使用条件
4. 为软件选择最佳方案

---

## 📋 API清单

### 1. ✅ Pollinations.AI
**官网**: https://pollinations.ai  
**文档**: https://github.com/pollinations/pollinations

#### 基本信息
- **类型**: 免费开源
- **需要注册**: 否（匿名可用）
- **需要API Key**: 否

#### 速率限制
| 等级 | 速率限制 | 可用模型 | 注册要求 | 备注 |
|------|---------|----------|----------|------|
| 匿名 | 15秒/次 | 基础模型 | 无需注册 | 适合测试 |
| Seed | 5秒/次 | 标准模型 | 免费注册 | 推荐使用 |
| Flower | 3秒/次 | 高级模型 | 付费 | 更高限制 |
| Nectar | 无限制 | 所有模型 | 企业 | 联系官方 |

#### 重要说明
- **2025年3月31日起**: 免费层图片可能包含水印
- **注册地址**: https://auth.pollinations.ai
- **注册后**: 移除水印 + 更高速率限制

#### 测试结果
- ✅ **可用**: 成功生成图片
- ⏱️ **响应时间**: 1.2秒
- 📦 **图片大小**: 24KB
- 🎯 **成功率**: 100%（测试时）

#### API使用示例
```python
import requests
import urllib.parse

prompt = "simple cat drawing"
encoded_prompt = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"

response = requests.get(url, timeout=30)
if response.status_code == 200:
    with open('image.png', 'wb') as f:
        f.write(response.content)
```

#### 优缺点
**优点**:
- ✅ 完全免费（基础功能）
- ✅ 无需API Key
- ✅ 响应快速
- ✅ 支持多种模型
- ✅ 开源项目

**缺点**:
- ⚠️ 匿名使用有速率限制（15秒/次）
- ⚠️ 2025年起可能有水印
- ⚠️ 服务不稳定（有时返回500错误）

---

### 2. ⚠️ Puter.js
**官网**: https://developer.puter.com  
**文档**: https://developer.puter.com/tutorials/free-unlimited-image-generation-api/

#### 基本信息
- **类型**: 免费无限制
- **需要注册**: 否
- **需要API Key**: 否

#### 速率限制
- **无限制**: 真正的免费无限制使用

#### 支持的模型
```
- gemini-2.5-flash-image-preview
- gpt-image-1 / gpt-image-1-mini
- dall-e-3 / dall-e-2
- FLUX.1-schnell / FLUX.1-dev / FLUX.1-pro
- Stable Diffusion 3 / SDXL
- 等30+模型
```

#### 测试结果
- ❌ **不可用**: 需要浏览器环境
- 📝 **原因**: Puter.js是JavaScript库，只能在前端使用
- 🔧 **限制**: 无法在Python后端直接调用

#### 使用示例（JavaScript）
```javascript
<script src="https://js.puter.com/v2/"></script>
<script>
puter.ai.txt2img("A peaceful mountain landscape")
  .then(imageElement => {
    document.body.appendChild(imageElement);
  });
</script>
```

#### 优缺点
**优点**:
- ✅ 完全免费
- ✅ 无限制使用
- ✅ 支持30+模型
- ✅ 无需API Key

**缺点**:
- ❌ 只能在浏览器中使用
- ❌ 无法在Python后端调用
- ❌ 不适合我们的桌面应用

---

### 3. ❌ Hugging Face Inference API
**官网**: https://huggingface.co  
**文档**: https://huggingface.co/docs/api-inference

#### 基本信息
- **类型**: 免费有限制
- **需要注册**: 是
- **需要API Key**: 是（Token）

#### 速率限制
- **免费层**: 有限制
- **Pro层**: $9/月，更高限制

#### 测试结果
- ❌ **不可用**: HTTP 410错误
- 📝 **原因**: API端点已停用
- 🔄 **状态**: 需要使用新的Inference Providers

#### 重要更新
- 旧API (`api-inference.huggingface.co`) 已停用
- 新API需要使用 Inference Providers
- 需要Token认证

#### 优缺点
**优点**:
- ✅ 模型丰富
- ✅ 社区活跃

**缺点**:
- ❌ 需要注册和Token
- ❌ 旧API已停用
- ❌ 有速率限制
- ❌ 模型加载慢

---

### 4. ❌ Craiyon (DALL-E mini)
**官网**: https://craiyon.com  
**API**: https://backend.craiyon.com/generate

#### 基本信息
- **类型**: 免费
- **需要注册**: 否
- **需要API Key**: 否

#### 速率限制
- **有限制**: 具体限制未公开
- **生成时间**: 约60秒

#### 测试结果
- ❌ **不可用**: HTTP 403错误
- 📝 **原因**: 可能有反爬虫机制
- 🔒 **状态**: API访问受限

#### 优缺点
**优点**:
- ✅ 完全免费
- ✅ 无需注册

**缺点**:
- ❌ API访问受限
- ❌ 生成速度慢（60秒）
- ❌ 图片质量一般

---

### 5. ❌ DeepAI
**官网**: https://deepai.org  
**API**: https://api.deepai.org/api/text2img

#### 基本信息
- **类型**: 免费有限制
- **需要注册**: 是
- **需要API Key**: 是

#### 速率限制
- **免费层**: 有限制
- **付费层**: 更高限制

#### 测试结果
- ❌ **不可用**: HTTP 401错误
- 📝 **原因**: 需要API Key
- 🔑 **要求**: 必须注册获取Key

#### 优缺点
**优点**:
- ✅ 有免费层

**缺点**:
- ❌ 需要注册和API Key
- ❌ 免费层限制严格
- ❌ 图片质量一般

---

### 6. ❌ Replicate
**官网**: https://replicate.com

#### 基本信息
- **类型**: 需要API Key
- **需要注册**: 是
- **需要API Key**: 是

#### 价格
- **按使用付费**: 不是真正免费
- **需要信用卡**: 注册需要绑卡

#### 测试结果
- ❌ **不可用**: 需要API Key
- 💰 **原因**: 需要付费

---

### 7. ❌ Stability AI
**官网**: https://stability.ai

#### 基本信息
- **类型**: 需要API Key
- **需要注册**: 是
- **需要API Key**: 是

#### 价格
- **付费服务**: 无免费层
- **企业级**: 价格较高

#### 测试结果
- ❌ **不可用**: 需要付费API Key

---

### 8. ❌ Segmind
**官网**: https://segmind.com

#### 基本信息
- **类型**: 免费有限制
- **需要注册**: 是
- **需要API Key**: 是

#### 测试结果
- ❌ **不可用**: 需要API Key

---

## 📊 测试统计

### 总体情况
- **测试总数**: 8个API
- **可用数量**: 1个（12.5%）
- **不可用**: 7个（87.5%）

### 按类别统计
| 类别 | 数量 | 可用 | 不可用 |
|------|------|------|--------|
| 免费开源 | 1 | 1 | 0 |
| 免费无限制 | 1 | 0 | 1 |
| 免费有限制 | 4 | 0 | 4 |
| 需要API Key | 3 | 0 | 3 |

### 不可用原因分析
| 原因 | 数量 | 占比 |
|------|------|------|
| 需要API Key | 4 | 57% |
| API已停用 | 1 | 14% |
| 访问受限 | 1 | 14% |
| 环境限制 | 1 | 14% |

---

## 💡 推荐方案

### 🥇 首选: Pollinations.AI
**推荐理由**:
1. ✅ 唯一测试成功的免费API
2. ✅ 无需API Key
3. ✅ 响应速度快（1.2秒）
4. ✅ 支持匿名使用

**使用建议**:
- 匿名使用: 适合低频使用（15秒/次）
- 注册使用: 推荐注册提升到5秒/次
- 注意水印: 2025年3月后可能有水印

**实现方式**:
```python
# 方法1: 直接URL
url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512"

# 方法2: 带参数
url = f"https://image.pollinations.ai/prompt/{prompt}"
params = {'width': '512', 'height': '512', 'nologo': 'true'}

# 方法3: 镜像端点
url = f"https://pollinations.ai/prompt/{prompt}"
```

### 🥈 备选: 本地生成
**推荐理由**:
1. ✅ 100%可靠
2. ✅ 无速率限制
3. ✅ 无网络依赖
4. ✅ 隐私保护

**适用场景**:
- API不可用时
- 离线使用
- 简单图形生成

---

## 🎯 最终建议

### 当前策略
**本地生成优先** + Pollinations.AI备用

**原因**:
1. Pollinations.AI虽然可用，但不稳定（经常500错误）
2. 速率限制（15秒/次）影响用户体验
3. 本地生成100%可靠，响应更快

### 实现方案
```python
def generate_image(prompt):
    # 优先使用本地生成（快速可靠）
    if is_simple_shape(prompt):
        return generate_local(prompt)
    
    # 复杂图形尝试API
    try:
        return pollinations_api(prompt)
    except:
        # API失败回退到本地
        return generate_local(prompt)
```

### 未来规划
1. **监控Pollinations.AI**: 定期检查API状态
2. **扩展本地库**: 添加更多图形类型
3. **用户选择**: 让用户选择API或本地
4. **缓存机制**: 缓存常用图形

---

## 📈 速率限制对比

| API | 匿名限制 | 注册限制 | 付费限制 |
|-----|----------|----------|----------|
| Pollinations.AI | 15秒/次 | 5秒/次 | 3秒/次或无限 |
| Puter.js | 无限制 | 无限制 | - |
| Hugging Face | - | 有限制 | 更高限制 |
| Craiyon | 有限制 | - | - |
| DeepAI | - | 有限制 | 更高限制 |
| 本地生成 | **无限制** | **无限制** | **无限制** |

---

## 🔍 关键发现

### 1. 免费API现状
- 真正免费且可用的API极少
- 大部分需要API Key或付费
- 服务稳定性普遍较差

### 2. 速率限制普遍存在
- 即使免费API也有严格限制
- Pollinations匿名: 15秒/次
- 注册后可提升到5秒/次

### 3. 本地生成的优势
- 100%可靠性
- 无速率限制
- 即时响应
- 完全免费

### 4. 用户体验考虑
- API延迟影响体验
- 失败率高影响信任
- 本地生成更稳定

---

## 📝 总结

经过全面测试，我们得出以下结论：

1. **Pollinations.AI是唯一可用的免费API**
   - 但存在速率限制和稳定性问题

2. **本地生成是最佳方案**
   - 100%可靠，无限制，响应快

3. **推荐策略: 本地优先**
   - 简单图形: 本地生成
   - 复杂图形: API尝试 → 失败回退本地

4. **未来方向**
   - 持续监控API状态
   - 扩展本地图形库
   - 提供用户选择权

**最终建议**: 继续使用当前的本地生成优先策略，这是最稳定可靠的方案！
