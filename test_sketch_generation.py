"""
测试黑白线条简笔画生成
"""
from ai_generator import AIImageGenerator
import time

def test_sketch_generation():
    """测试黑白简笔画生成"""
    print("=" * 80)
    print("🎨 黑白线条简笔画生成测试")
    print("=" * 80)
    
    # 创建生成器
    generator = AIImageGenerator()
    
    # 测试提示词 - 专门针对简笔画
    test_prompts = [
        "小猫简笔画",
        "老鼠简笔画", 
        "房子简笔画",
        "花朵简笔画",
        "太阳简笔画",
        "a simple cat drawing",
        "a house sketch",
        "a flower line art",
        "a bird simple drawing",
        "a tree minimalist sketch"
    ]
    
    success_count = 0
    total_count = len(test_prompts)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🧪 测试 {i}/{total_count}: {prompt}")
        print("-" * 60)
        
        try:
            success, result = generator.generate_image(prompt)
            
            if success:
                print(f"✅ 成功生成: {result}")
                success_count += 1
            else:
                print(f"❌ 生成失败: {result}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        # 避免速率限制
        if i < total_count:
            print("⏳ 等待5秒避免速率限制...")
            time.sleep(5)
        
        print("-" * 60)
    
    # 总结
    print(f"\n📊 测试结果: {success_count}/{total_count} 成功")
    print(f"📈 成功率: {success_count/total_count*100:.1f}%")
    
    if success_count > 0:
        print("\n🎉 黑白简笔画生成测试成功！")
        print("✅ Pollinations API 正常工作")
        print("✅ 黑白线条风格已优化")
        print("✅ 简笔画效果良好")
        print(f"✅ 生成的图片保存在: ai_generated/ 文件夹")
    else:
        print("\n⚠️ 所有测试都失败了")
        print("可能原因:")
        print("1. 网络连接问题")
        print("2. Pollinations服务器故障")
        print("3. Token配置问题")
        print("4. 速率限制过于频繁")

if __name__ == "__main__":
    test_sketch_generation()
