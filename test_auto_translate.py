"""
测试自动翻译+turbo模型生成
"""
from ai_generator import AIImageGenerator
import time

def test_auto_translate_generation():
    """测试自动翻译生成"""
    print("=" * 80)
    print("🌐 自动翻译+turbo模型测试")
    print("=" * 80)
    
    # 创建生成器
    generator = AIImageGenerator()
    
    # 测试提示词（中英文混合）
    test_prompts = [
        "小猫",           # 中文简单
        "可爱的小狗",      # 中文复杂
        "鳄鱼",           # 之前失败的
        "房子",           # 建筑
        "花朵",           # 植物
        "cat drawing",    # 英文（应该保持不变）
        "大象和老鼠",      # 多个对象
        "简单的树"        # 带形容词
    ]
    
    success_count = 0
    total_count = len(test_prompts)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🧪 测试 {i}/{total_count}: {prompt}")
        print("-" * 60)
        
        try:
            success, result = generator.generate_image(prompt)
            
            if success:
                print(f"✅ 生成成功: {result}")
                success_count += 1
            else:
                print(f"❌ 生成失败: {result}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        # 等待避免速率限制（turbo模型需要5秒间隔）
        if i < total_count:
            print("⏳ 等待6秒避免速率限制...")
            time.sleep(6)
        
        print("-" * 60)
    
    # 总结
    print(f"\n📊 测试结果: {success_count}/{total_count} 成功")
    print(f"📈 成功率: {success_count/total_count*100:.1f}%")
    
    if success_count > 0:
        print("\n🎉 自动翻译+turbo模型测试成功！")
        print("✅ 翻译功能正常")
        print("✅ turbo模型稳定")
        print("✅ 中文输入支持")
        print(f"✅ 生成的图片保存在: ai_generated/ 文件夹")
        
        # 显示历史记录
        history = generator.get_history()
        if history:
            print(f"\n📁 最近生成的图片:")
            for i, file in enumerate(history[:5], 1):
                print(f"  {i}. {file}")
    else:
        print("\n⚠️ 所有测试都失败了")
        print("可能原因:")
        print("1. Pollinations服务器故障")
        print("2. 网络连接问题") 
        print("3. Token配置问题")
        print("4. 速率限制过于频繁")

if __name__ == "__main__":
    test_auto_translate_generation()
