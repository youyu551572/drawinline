"""
优化的AI图片生成模块
基于API测试结果，只使用真正可用的免费API
"""
import requests
import io
import time
from PIL import Image
import os
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OptimizedAIImageGenerator:
    """优化的AI图片生成器 - 只使用测试通过的API"""
    
    def __init__(self):
        """初始化生成器"""
        self.timeout = 45  # 请求超时时间
        self.save_dir = os.path.join(os.path.dirname(__file__), 'ai_generated')
        
        # 创建保存目录
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def generate_image(self, prompt, style='simple line drawing'):
        """
        生成图片 - 使用测试通过的API
        
        Args:
            prompt: 用户输入的描述
            style: 风格描述，默认为简笔画
            
        Returns:
            tuple: (success, image_path_or_error_message)
        """
        # 优化提示词，强调简笔画风格
        full_prompt = f"{prompt}, {style}, black and white, minimalist, sketch"
        
        # 方法1: Pollinations.ai 直接URL (测试成功)
        try:
            result = self._generate_pollinations_v1(full_prompt)
            if result[0]:
                return result
            else:
                print(f"方法1失败: {result[1]}")
        except Exception as e:
            print(f"方法1异常: {e}")
            
        # 方法2: Pollinations.ai 带参数 (测试成功)
        try:
            result = self._generate_pollinations_v2(full_prompt)
            if result[0]:
                return result
            else:
                print(f"方法2失败: {result[1]}")
        except Exception as e:
            print(f"方法2异常: {e}")
            
        # 方法3: Pollinations.ai 镜像 (测试成功)
        try:
            result = self._generate_pollinations_v3(full_prompt)
            if result[0]:
                return result
            else:
                print(f"方法3失败: {result[1]}")
        except Exception as e:
            print(f"方法3异常: {e}")
            
        # 方法4: 本地生成 (100%可靠)
        try:
            return self._generate_simple_local(prompt)
        except Exception as e:
            print(f"本地生成失败: {e}")
            
        # 所有方法都失败
        return False, f"生成失败: 所有方法都不可用"
    
    def _generate_pollinations_v1(self, prompt):
        """
        Pollinations.ai 方法1 - 直接URL (测试成功 ✅)
        """
        try:
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
            
            print(f"正在生成图片（方法1-测试通过）: {prompt}")
            
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=False,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                timestamp = int(time.time())
                filename = f"ai_generated_{timestamp}.png"
                filepath = os.path.join(self.save_dir, filename)
                
                image = Image.open(io.BytesIO(response.content))
                image.save(filepath)
                print(f"方法1图片已保存: {filepath}")
                
                return True, filepath
            else:
                return False, f"API返回错误: {response.status_code}"
                
        except Exception as e:
            return False, f"方法1失败: {str(e)}"
    
    def _generate_pollinations_v2(self, prompt):
        """
        Pollinations.ai 方法2 - 带参数 (测试成功 ✅)
        """
        try:
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            
            params = {
                'width': '512',
                'height': '512',
                'nologo': 'true'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"正在生成图片（方法2-测试通过）: {prompt}")
            
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
                verify=False
            )
            
            if response.status_code == 200:
                timestamp = int(time.time())
                filename = f"ai_generated_{timestamp}.png"
                filepath = os.path.join(self.save_dir, filename)
                
                image = Image.open(io.BytesIO(response.content))
                image.save(filepath)
                print(f"方法2图片已保存: {filepath}")
                
                return True, filepath
            else:
                return False, f"API返回错误: {response.status_code}"
                
        except Exception as e:
            return False, f"方法2失败: {str(e)}"
    
    def _generate_pollinations_v3(self, prompt):
        """
        Pollinations.ai 方法3 - 镜像端点 (测试成功 ✅)
        """
        try:
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://pollinations.ai/prompt/{encoded_prompt}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"正在生成图片（方法3-测试通过）: {prompt}")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                verify=False,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                timestamp = int(time.time())
                filename = f"ai_generated_{timestamp}.png"
                filepath = os.path.join(self.save_dir, filename)
                
                image = Image.open(io.BytesIO(response.content))
                image.save(filepath)
                print(f"方法3图片已保存: {filepath}")
                
                return True, filepath
            else:
                return False, f"API返回错误: {response.status_code}"
                
        except Exception as e:
            return False, f"方法3失败: {str(e)}"
    
    def _generate_simple_local(self, prompt):
        """
        本地生成简单图形（100%可靠备用方案）
        """
        try:
            from PIL import Image, ImageDraw
            
            # 创建512x512的白色画布
            image = Image.new('RGB', (512, 512), 'white')
            draw = ImageDraw.Draw(image)
            
            # 根据关键词绘制简单图形
            prompt_lower = prompt.lower()
            
            if '猫' in prompt or 'cat' in prompt_lower:
                # 绘制简单的猫
                draw.ellipse([200, 150, 312, 262], outline='black', width=3)  # 头部
                draw.polygon([(210, 160), (230, 120), (250, 160)], outline='black', width=2)  # 左耳
                draw.polygon([(262, 160), (282, 120), (302, 160)], outline='black', width=2)  # 右耳
                draw.ellipse([220, 180, 235, 195], fill='black')  # 左眼
                draw.ellipse([277, 180, 292, 195], fill='black')  # 右眼
                draw.polygon([(250, 200), (260, 210), (240, 210)], fill='black')  # 鼻子
                draw.arc([235, 210, 277, 230], 0, 180, fill='black', width=2)  # 嘴巴
                
            elif '房子' in prompt or 'house' in prompt_lower:
                # 绘制简单的房子
                draw.rectangle([180, 250, 332, 380], outline='black', width=3)  # 房子主体
                draw.polygon([(160, 250), (256, 150), (352, 250)], outline='black', width=3)  # 屋顶
                draw.rectangle([230, 320, 282, 380], outline='black', width=2)  # 门
                draw.rectangle([190, 270, 220, 300], outline='black', width=2)  # 左窗
                draw.rectangle([292, 270, 322, 300], outline='black', width=2)  # 右窗
                
            elif '花' in prompt or 'flower' in prompt_lower:
                # 绘制简单的花
                draw.ellipse([240, 240, 272, 272], outline='black', width=2, fill='white')  # 花心
                # 花瓣
                for angle in range(0, 360, 45):
                    import math
                    x = 256 + 30 * math.cos(math.radians(angle))
                    y = 256 + 30 * math.sin(math.radians(angle))
                    draw.ellipse([x-10, y-10, x+10, y+10], outline='black', width=2)
                draw.line([(256, 272), (256, 400)], fill='black', width=3)  # 茎
                draw.ellipse([230, 320, 256, 350], outline='black', width=2)  # 叶子
                
            elif '笑脸' in prompt or 'smile' in prompt_lower or 'face' in prompt_lower:
                # 绘制简单的笑脸
                draw.ellipse([180, 180, 332, 332], outline='black', width=3)  # 脸部
                draw.ellipse([210, 220, 230, 240], fill='black')  # 左眼
                draw.ellipse([282, 220, 302, 240], fill='black')  # 右眼
                draw.arc([220, 250, 292, 300], 0, 180, fill='black', width=3)  # 笑脸
                
            else:
                # 默认绘制一个简单的圆形
                draw.ellipse([200, 200, 312, 312], outline='black', width=3)
                draw.text((220, 250), "Simple\nDrawing", fill='black')
            
            # 保存图片
            timestamp = int(time.time())
            filename = f"ai_generated_local_{timestamp}.png"
            filepath = os.path.join(self.save_dir, filename)
            
            image.save(filepath)
            print(f"本地生成图片已保存: {filepath}")
            
            return True, filepath
            
        except Exception as e:
            return False, f"本地生成失败: {str(e)}"
    
    def get_history(self):
        """
        获取生成历史
        
        Returns:
            list: 历史图片路径列表
        """
        if not os.path.exists(self.save_dir):
            return []
        
        files = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(self.save_dir, filename)
                files.append({
                    'path': filepath,
                    'name': filename,
                    'time': os.path.getmtime(filepath)
                })
        
        # 按时间倒序排列
        files.sort(key=lambda x: x['time'], reverse=True)
        return files
    
    def delete_image(self, filepath):
        """
        删除生成的图片
        
        Args:
            filepath: 图片路径
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"删除图片失败: {e}")
        return False


# 测试代码
if __name__ == "__main__":
    generator = OptimizedAIImageGenerator()
    
    # 测试生成
    print("测试优化的AI图片生成...")
    success, result = generator.generate_image("一只可爱的小猫")
    
    if success:
        print(f"✓ 生成成功: {result}")
    else:
        print(f"✗ 生成失败: {result}")
