"""
AI图片生成器 - 自动翻译+turbo模型
专门生成黑白线条简笔画
"""
import os
import time

class AIImageGenerator:
    """AI图片生成器 - 只使用Pollinations API"""
    
    def __init__(self):
        """初始化生成器"""
        self.timeout = 60  # 请求超时时间
        self.save_dir = os.path.join(os.path.dirname(__file__), 'ai_generated')
        
        # 创建保存目录
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        print("🌸 AI图片生成器初始化完成（纯Pollinations API）")
    
    def generate_image(self, prompt, style="simple line drawing"):
        """
        生成AI图片 - 自动翻译+turbo模型+黑白简笔画
        
        Args:
            prompt: 用户输入的描述（中文或英文）
            style: 风格描述，默认为简笔画
            
        Returns:
            tuple: (success, image_path_or_error_message)
        """
        # 自动翻译中文到英文
        from translator import SimpleTranslator
        translator = SimpleTranslator()
        
        # 翻译提示词
        english_prompt = translator.translate_to_english(prompt)
        
        # 添加简笔画风格
        final_prompt = translator.add_drawing_style(english_prompt)
        
        print(f"🌸 使用Pollinations生成简笔画: {prompt}")
        print(f"🌐 翻译后: {final_prompt}")
        
        # 使用turbo模型生成
        success, result = self._try_pollinations_turbo(final_prompt)
        
        if success:
            return success, result
        else:
            # 如果失败，尝试更简化的提示词
            print("⚠️ 首次生成失败，尝试最简化提示词...")
            simple_prompt = english_prompt if english_prompt else prompt
            return self._try_pollinations_turbo(simple_prompt)
    
    def _try_pollinations(self, prompt):
        """尝试使用Pollinations生成 - 增强重试版本"""
        try:
            # 使用增强的重试生成器
            from robust_pollinations import RobustPollinationsGenerator
            generator = RobustPollinationsGenerator()
            
            # 使用强化重试机制生成图片
            return generator.generate_with_robust_retry(
                prompt, 
                width=512, 
                height=512
            )
            
        except Exception as e:
            print(f"增强Pollinations生成失败: {e}")
            # 回退到原始方法
            try:
                from config import POLLINATIONS_TOKEN
                token = POLLINATIONS_TOKEN if POLLINATIONS_TOKEN else None
                
                from pollinations_generator import PollinationsGenerator
                generator = PollinationsGenerator(token=token)
                return generator.generate(prompt, width=512, height=512)
            except Exception as e2:
                return False, f"所有方法都失败: {str(e2)}"
    
    def _try_pollinations_turbo(self, prompt):
        """专门使用turbo模型生成"""
        try:
            from config import POLLINATIONS_TOKEN
            token = POLLINATIONS_TOKEN if POLLINATIONS_TOKEN else None
            
            from pollinations_generator import PollinationsGenerator
            generator = PollinationsGenerator(token=token)
            
            print(f"🚀 使用turbo模型生成: {prompt}")
            
            # 固定使用turbo模型，多次重试
            for attempt in range(3):
                try:
                    success, result = generator.generate(
                        prompt, 
                        width=512, 
                        height=512, 
                        model="turbo"  # 固定使用turbo
                    )
                    
                    if success:
                        print(f"✅ turbo模型第{attempt+1}次尝试成功!")
                        return True, result
                    else:
                        print(f"⚠️ turbo模型第{attempt+1}次失败: {result}")
                        if attempt < 2:  # 不是最后一次
                            wait_time = (attempt + 1) * 8  # 8, 16秒
                            print(f"⏳ 等待{wait_time}秒后重试...")
                            time.sleep(wait_time)
                
                except Exception as e:
                    print(f"❌ turbo模型第{attempt+1}次异常: {e}")
                    if attempt < 2:
                        time.sleep(5)
            
            return False, "turbo模型3次尝试都失败了"
            
        except Exception as e:
            return False, f"turbo模型调用失败: {str(e)}"
    
    def get_history(self):
        """获取生成历史记录"""
        try:
            import glob
            import os
            from datetime import datetime
            
            # 获取所有生成的图片
            pattern = os.path.join(self.save_dir, "*.png")
            files = glob.glob(pattern)
            
            # 按修改时间排序（最新的在前）
            files.sort(key=os.path.getmtime, reverse=True)
            
            # 转换为字典格式，匹配modern_app.py的期望
            history_list = []
            for file_path in files[:10]:
                try:
                    # 获取文件信息
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    mod_time = os.path.getmtime(file_path)
                    
                    # 格式化时间
                    time_str = datetime.fromtimestamp(mod_time).strftime("%H:%M")
                    
                    # 创建历史记录项
                    history_item = {
                        'name': file_name.replace('.png', '').replace('pollinations_', ''),
                        'path': file_path,
                        'size': f"{file_size//1024}KB",
                        'time': time_str,
                        'type': 'AI生成'
                    }
                    history_list.append(history_item)
                except Exception as e:
                    print(f"处理文件 {file_path} 失败: {e}")
                    continue
            
            return history_list
        except Exception as e:
            print(f"获取历史记录失败: {e}")
            return []
    
    def clear_history(self):
        """清空历史记录"""
        try:
            import glob
            import os
            
            pattern = os.path.join(self.save_dir, "*.png")
            files = glob.glob(pattern)
            
            for file in files:
                os.remove(file)
            
            print(f"已清空 {len(files)} 个历史文件")
            return True
        except Exception as e:
            print(f"清空历史记录失败: {e}")
            return False


# 测试代码
if __name__ == "__main__":
    generator = AIImageGenerator()
    
    # 测试生成
    test_prompts = [
        "小猫简笔画",
        "房子简笔画", 
        "花朵简笔画"
    ]
    
    print("=" * 80)
    print("🎨 黑白简笔画生成测试")
    print("=" * 80)
    
    for prompt in test_prompts:
        print(f"\n🧪 测试: {prompt}")
        success, result = generator.generate_image(prompt)
        
        if success:
            print(f"✅ 成功: {result}")
        else:
            print(f"❌ 失败: {result}")
        
        # 等待避免速率限制
        time.sleep(6)
    
    print("\n🎉 测试完成！")
