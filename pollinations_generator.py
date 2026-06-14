"""
Pollinations.AI 图片生成器
基于官方API文档实现
"""
import requests
import time
import os
from urllib.parse import quote
import hashlib

class PollinationsGenerator:
    """Pollinations.AI 生成器"""
    
    def __init__(self, token=None):
        """
        初始化生成器
        
        Args:
            token: API Token（可选，提供后可获得更高速率限制）
        """
        self.token = token
        self.base_url = "https://image.pollinations.ai"
        self.last_request_time = 0
        self.save_dir = "ai_generated"
        
        # 根据是否有token设置速率限制
        self.rate_limit = 5 if token else 15  # 秒
        
        # 创建保存目录
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        print(f"🌸 Pollinations生成器初始化完成")
        if token:
            print(f"✅ 使用注册Token，速率限制: {self.rate_limit}秒/次")
        else:
            print(f"⚠️ 匿名模式，速率限制: {self.rate_limit}秒/次")
    
    def generate(self, prompt, width=512, height=512, model="flux", enhance=False):
        """
        生成黑白线条简笔画
        
        Args:
            prompt: 图片描述
            width: 宽度（默认512）
            height: 高度（默认512）
            model: 模型（flux/turbo）
            enhance: 是否让AI优化提示词
            
        Returns:
            tuple: (success, image_path_or_error)
        """
        print(f"🎨 Pollinations生成: {prompt}")
        
        try:
            # 检查速率限制
            self._wait_for_rate_limit()
            
            # 构建URL
            encoded_prompt = quote(prompt)
            url = f"{self.base_url}/prompt/{encoded_prompt}"
            
            # 构建参数
            params = {
                'width': width,
                'height': height,
                'model': model,
                'enhance': str(enhance).lower()
            }
            
            # 如果有token，添加nologo参数
            if self.token:
                params['nologo'] = 'true'
            
            # 构建请求头
            headers = {
                'User-Agent': 'YouYu-AutoDrawing/1.0'
            }
            
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
            
            print(f"📡 发送请求: {url}")
            print(f"📋 参数: {params}")
            
            # 发送请求
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                timeout=60,
                stream=True
            )
            
            # 更新请求时间
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                # 保存图片
                timestamp = int(time.time())
                filename = f"pollinations_{timestamp}.png"
                filepath = os.path.join(self.save_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ 图片已保存: {filepath}")
                return True, filepath
                
            elif response.status_code == 429:
                error_msg = f"速率限制：请等待{self.rate_limit}秒后重试"
                print(f"⏳ {error_msg}")
                return False, error_msg
                
            elif response.status_code == 500:
                error_msg = "服务器内部错误，请稍后重试"
                print(f"❌ {error_msg}")
                return False, error_msg
                
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                print(f"❌ {error_msg}")
                return False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "请求超时，请检查网络连接"
            print(f"⏰ {error_msg}")
            return False, error_msg
            
        except requests.exceptions.ConnectionError:
            error_msg = "网络连接错误"
            print(f"🌐 {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def _wait_for_rate_limit(self):
        """等待速率限制"""
        if self.last_request_time == 0:
            return
        
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            wait_time = self.rate_limit - elapsed
            print(f"⏳ 速率限制，等待 {wait_time:.1f} 秒...")
            time.sleep(wait_time)
    
    def generate_with_cache(self, prompt, **kwargs):
        """
        带缓存的生成（避免重复生成相同内容）
        
        Args:
            prompt: 图片描述
            **kwargs: 其他参数
            
        Returns:
            tuple: (success, image_path_or_error)
        """
        # 生成缓存键
        cache_key = self._generate_cache_key(prompt, **kwargs)
        cache_file = os.path.join(self.save_dir, f"cache_{cache_key}.png")
        
        # 检查缓存
        if os.path.exists(cache_file):
            print(f"📦 使用缓存: {cache_file}")
            return True, cache_file
        
        # 生成新图片
        success, result = self.generate(prompt, **kwargs)
        
        # 如果成功，复制到缓存
        if success:
            import shutil
            shutil.copy2(result, cache_file)
            print(f"💾 已缓存: {cache_file}")
        
        return success, result
    
    def _generate_cache_key(self, prompt, **kwargs):
        """生成缓存键"""
        cache_data = f"{prompt}_{kwargs}"
        return hashlib.md5(cache_data.encode()).hexdigest()[:16]
    
    def test_connection(self):
        """测试连接"""
        print("🧪 测试Pollinations连接...")
        
        success, result = self.generate("test image", width=256, height=256)
        
        if success:
            print("✅ 连接测试成功！")
            print(f"📁 测试图片: {result}")
            return True
        else:
            print(f"❌ 连接测试失败: {result}")
            return False


# 测试代码
if __name__ == "__main__":
    # 尝试从配置文件加载token
    try:
        from config import POLLINATIONS_TOKEN
        token = POLLINATIONS_TOKEN if POLLINATIONS_TOKEN else None
    except ImportError:
        print("⚠️ 未找到config.py，使用匿名模式")
        token = None
    
    # 创建生成器
    generator = PollinationsGenerator(token=token)
    
    # 测试生成
    test_prompts = [
        "a cute cat, simple line drawing",
        "a small house, minimalist sketch",
        "a beautiful flower, black and white drawing"
    ]
    
    print("=" * 80)
    print("🌸 Pollinations生成器测试")
    print("=" * 80)
    
    for prompt in test_prompts:
        print(f"\n🎨 测试: {prompt}")
        success, result = generator.generate(prompt)
        
        if success:
            print(f"✅ 成功: {result}")
        else:
            print(f"❌ 失败: {result}")
        
        print("-" * 40)
    
    print("\n🎉 测试完成！")
