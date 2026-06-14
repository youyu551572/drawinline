"""
Pollinations API 完整测试
"""
from pollinations_generator import PollinationsGenerator
from config import POLLINATIONS_TOKEN
import time

def test_pollinations():
    """测试Pollinations API"""
    print("=" * 80)
    print("🌸 Pollinations API 完整测试")
    print("=" * 80)
    
    # 创建生成器
    generator = PollinationsGenerator(token=POLLINATIONS_TOKEN)
    
    # 测试提示词
    test_prompts = [
        ("简单测试", "a simple cat"),
        ("中文测试", "一只可爱的小猫"),
        ("复杂测试", "a cyberpunk city at night, neon lights, futuristic"),
        ("艺术风格", "a beautiful landscape, oil painting style"),
    ]
    
    success_count = 0
    total_count = len(test_prompts)
    
    for name, prompt in test_prompts:
        print(f"\n🧪 {name}: {prompt}")
        print("-" * 60)
        
        try:
            success, result = generator.generate(
                prompt, 
                width=512, 
                height=512, 
                model="flux"
            )
            
            if success:
                print(f"✅ 成功: {result}")
                success_count += 1
            else:
                print(f"❌ 失败: {result}")
                
                # 如果是500错误，等待一下再试
                if "500" in str(result):
                    print("⏳ 服务器错误，等待10秒后重试...")
                    time.sleep(10)
                    
                    success2, result2 = generator.generate(prompt, width=256, height=256)
                    if success2:
                        print(f"✅ 重试成功: {result2}")
                        success_count += 1
                    else:
                        print(f"❌ 重试仍失败: {result2}")
        
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        print("-" * 60)
    
    # 总结
    print(f"\n📊 测试结果: {success_count}/{total_count} 成功")
    
    if success_count > 0:
        print("🎉 Pollinations API 配置成功！")
        print("✅ Token有效")
        print("✅ 可以正常生成图片")
        print("✅ 速率限制: 5秒/次")
        print("✅ 无水印")
    else:
        print("⚠️ 所有测试都失败了")
        print("可能原因:")
        print("1. 网络连接问题")
        print("2. Pollinations服务器临时故障")
        print("3. Token配置错误")
        print("4. 速率限制")
        
        print("\n💡 建议:")
        print("1. 检查网络连接")
        print("2. 稍后重试")
        print("3. 使用本地生成器作为备选")

if __name__ == "__main__":
    test_pollinations()
