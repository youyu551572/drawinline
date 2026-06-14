"""
增强的Pollinations生成器 - 处理服务器不稳定问题
"""
import time
import random
from pollinations_generator import PollinationsGenerator
from config import POLLINATIONS_TOKEN

class RobustPollinationsGenerator:
    """增强的Pollinations生成器，处理服务器不稳定"""
    
    def __init__(self):
        self.token = POLLINATIONS_TOKEN if POLLINATIONS_TOKEN else None
        self.max_retries = 5
        self.base_wait_time = 10
        
    def generate_with_robust_retry(self, prompt, **kwargs):
        """
        带强化重试的生成
        
        Args:
            prompt: 提示词
            **kwargs: 其他参数
            
        Returns:
            tuple: (success, result)
        """
        print(f"🌸 增强重试生成: {prompt}")
        
        # 尝试不同的策略
        strategies = [
            {"prompt": f"{prompt}, sketch", "model": "flux"},
            {"prompt": f"{prompt}, drawing", "model": "turbo"}, 
            {"prompt": prompt, "model": "flux"},
            {"prompt": f"simple {prompt}", "model": "turbo"},
            {"prompt": f"{prompt} art", "model": "flux"}
        ]
        
        for strategy_idx, strategy in enumerate(strategies):
            print(f"📋 尝试策略 {strategy_idx + 1}/{len(strategies)}: {strategy}")
            
            for retry in range(self.max_retries):
                try:
                    generator = PollinationsGenerator(token=self.token)
                    
                    # 使用策略参数
                    test_kwargs = kwargs.copy()
                    test_kwargs.update(strategy)
                    
                    success, result = generator.generate(**test_kwargs)
                    
                    if success:
                        print(f"✅ 策略 {strategy_idx + 1} 第 {retry + 1} 次尝试成功!")
                        return True, result
                    
                    # 分析错误类型
                    if "500" in str(result) or "502" in str(result):
                        wait_time = self.base_wait_time + retry * 5 + random.randint(1, 5)
                        print(f"⏳ 服务器错误，等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    elif "429" in str(result):
                        wait_time = 20 + retry * 10
                        print(f"⏳ 速率限制，等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ 其他错误: {result}")
                        break  # 非服务器错误，尝试下一个策略
                        
                except Exception as e:
                    print(f"❌ 异常: {e}")
                    if retry < self.max_retries - 1:
                        time.sleep(5)
            
            print(f"⚠️ 策略 {strategy_idx + 1} 失败，尝试下一个策略...")
        
        return False, "所有策略都失败了，Pollinations服务器可能暂时不可用"
    
    def test_connection(self):
        """测试连接状态"""
        print("🧪 测试Pollinations连接状态...")
        
        test_prompts = ["cat", "dog", "sun"]
        
        for prompt in test_prompts:
            print(f"\n🔍 测试提示词: {prompt}")
            success, result = self.generate_with_robust_retry(
                prompt, 
                width=256, 
                height=256
            )
            
            if success:
                print(f"✅ 连接正常: {result}")
                return True
            else:
                print(f"❌ 连接失败: {result}")
        
        print("⚠️ 所有测试都失败，服务器可能不可用")
        return False


# 测试代码
if __name__ == "__main__":
    generator = RobustPollinationsGenerator()
    
    # 测试连接
    if generator.test_connection():
        print("\n🎉 Pollinations服务可用!")
        
        # 测试实际生成
        success, result = generator.generate_with_robust_retry(
            "鳄鱼", 
            width=512, 
            height=512
        )
        
        if success:
            print(f"🎨 生成成功: {result}")
        else:
            print(f"❌ 生成失败: {result}")
    else:
        print("\n⚠️ Pollinations服务暂时不可用")
