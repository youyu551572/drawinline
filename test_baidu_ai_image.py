"""
测试百度AI生图API
从浏览器网络请求中发现的API
"""
import requests
import time
import os
import urllib.parse

class BaiduAIImageTester:
    """百度AI生图API测试器"""
    
    def __init__(self):
        self.save_dir = "baidu_ai_test"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def test_baidu_ai_image(self, prompt="小猫简笔画"):
        """
        测试百度AI生图API
        
        从浏览器请求中发现的URL格式：
        https://gips0.baidu.com/it/u=2571829564,3418629511&fm=3086&app=3086&f=JPEG&wm=1,baiduai3,0,0,13,9&wmo=5,5&w=1024&h=1024
        
        参数分析：
        - u: 图片ID（两个数字）
        - fm: 格式代码 (3086)
        - app: 应用代码 (3086)
        - f: 文件格式 (JPEG)
        - wm: 水印参数 (1,baiduai3,0,0,13,9)
        - wmo: 水印偏移 (5,5)
        - w: 宽度 (1024)
        - h: 高度 (1024)
        """
        print("=" * 80)
        print("🔍 测试百度AI生图API")
        print(f"📝 提示词: {prompt}")
        print("=" * 80)
        
        # 方法1: 尝试直接访问已知的图片URL
        print("\n方法1: 测试已知的图片URL...")
        test_urls = [
            "https://gips0.baidu.com/it/u=2571829564,3418629511&fm=3086&app=3086&f=JPEG&wm=1,baiduai3,0,0,13,9&wmo=5,5&w=1024&h=1024",
            "https://gips3.baidu.com/it/u=2789977436,1240790593&fm=3086&app=3086&f=JPEG&wm=1,baiduai3,0,0,13,9&wmo=5,5&w=1024&h=1024",
            "https://gips0.baidu.com/it/u=127432533,1514766370&fm=3086&app=3086&f=JPEG&wm=1,baiduai3,0,0,13,9&wmo=5,5&w=1024&h=1024",
            "https://gips3.baidu.com/it/u=587945598,1174548909&fm=3086&app=3086&f=JPEG&wm=1,baiduai3,0,0,13,9&wmo=5,5&w=1024&h=1024"
        ]
        
        for i, url in enumerate(test_urls, 1):
            try:
                print(f"\n测试URL {i}...")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://chat.baidu.com/',
                    'Origin': 'https://chat.baidu.com',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    filepath = os.path.join(self.save_dir, f"baidu_test_{i}.jpg")
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ 成功! 图片大小: {len(response.content)} bytes")
                    print(f"📁 保存到: {filepath}")
                else:
                    print(f"❌ 失败: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"💥 异常: {str(e)}")
            
            time.sleep(1)
        
        # 方法2: 尝试分析API模式
        print("\n" + "=" * 80)
        print("方法2: 分析API模式...")
        print("=" * 80)
        
        print("\n📊 API特征分析:")
        print("1. 域名: gips0.baidu.com / gips3.baidu.com (可能是CDN)")
        print("2. 路径: /it/u=<ID1>,<ID2>&...")
        print("3. 参数:")
        print("   - u: 图片唯一ID（两个数字组合）")
        print("   - fm: 3086 (固定格式代码)")
        print("   - app: 3086 (固定应用代码)")
        print("   - f: JPEG (文件格式)")
        print("   - wm: 1,baiduai3,0,0,13,9 (水印参数)")
        print("   - wmo: 5,5 (水印偏移)")
        print("   - w: 1024 (宽度)")
        print("   - h: 1024 (高度)")
        
        print("\n🔍 关键发现:")
        print("❌ 这不是一个生成API，而是图片存储URL")
        print("❌ 图片ID是预先生成的，无法通过提示词直接生成")
        print("❌ 需要先调用百度AI生图接口获取图片ID")
        
        # 方法3: 尝试找到真正的生成API
        print("\n" + "=" * 80)
        print("方法3: 搜索真正的生成API...")
        print("=" * 80)
        
        print("\n💡 百度AI生图可能的API端点:")
        print("1. https://chat.baidu.com/api/... (需要登录和认证)")
        print("2. https://yiyan.baidu.com/... (文心一言API)")
        print("3. 需要Cookie和Token认证")
        
        print("\n⚠️ 限制:")
        print("- 需要百度账号登录")
        print("- 需要Cookie认证")
        print("- 可能有速率限制")
        print("- 可能需要付费或有配额限制")
        
        # 方法4: 尝试无水印版本
        print("\n" + "=" * 80)
        print("方法4: 测试无水印参数...")
        print("=" * 80)
        
        # 尝试修改水印参数
        test_url_no_watermark = "https://gips0.baidu.com/it/u=2571829564,3418629511&fm=3086&app=3086&f=JPEG&w=512&h=512"
        
        try:
            print(f"\n测试无水印URL...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://chat.baidu.com/'
            }
            
            response = requests.get(test_url_no_watermark, headers=headers, timeout=30)
            
            if response.status_code == 200:
                filepath = os.path.join(self.save_dir, "baidu_no_watermark.jpg")
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 成功! 图片大小: {len(response.content)} bytes")
                print(f"📁 保存到: {filepath}")
            else:
                print(f"❌ 失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"💥 异常: {str(e)}")
    
    def analyze_api_pattern(self):
        """分析API模式"""
        print("\n" + "=" * 80)
        print("📊 百度AI生图API完整分析")
        print("=" * 80)
        
        print("\n🔍 发现的URL模式:")
        print("```")
        print("https://gips[0-3].baidu.com/it/u=<ID1>,<ID2>&fm=3086&app=3086&f=JPEG&wm=1,baiduai3,0,0,13,9&wmo=5,5&w=1024&h=1024")
        print("```")
        
        print("\n📝 参数说明:")
        params = {
            'gips[0-3]': 'CDN节点（0-3随机）',
            'u': '图片唯一ID（两个大数字）',
            'fm': '格式代码（固定3086）',
            'app': '应用代码（固定3086）',
            'f': '文件格式（JPEG/PNG）',
            'wm': '水印参数（1,baiduai3,0,0,13,9）',
            'wmo': '水印偏移（5,5）',
            'w': '图片宽度（512/1024）',
            'h': '图片高度（512/1024）'
        }
        
        for param, desc in params.items():
            print(f"  {param:15s} - {desc}")
        
        print("\n❌ 限制和问题:")
        print("1. 这只是图片存储URL，不是生成API")
        print("2. 图片ID是预生成的，无法通过提示词获取")
        print("3. 真正的生成API需要:")
        print("   - 百度账号登录")
        print("   - Cookie和Token认证")
        print("   - 可能需要付费或有配额")
        
        print("\n💡 可能的解决方案:")
        print("1. 逆向百度AI生图的前端代码")
        print("2. 使用Selenium模拟浏览器操作")
        print("3. 申请百度AI开放平台API Key")
        print("4. 继续使用本地生成（推荐）")
        
        print("\n✅ 结论:")
        print("百度AI生图API需要认证，不适合作为免费API使用")
        print("建议继续使用当前的本地生成方案")


def main():
    """主函数"""
    tester = BaiduAIImageTester()
    
    # 测试百度AI生图
    tester.test_baidu_ai_image("小猫简笔画")
    
    # 分析API模式
    tester.analyze_api_pattern()
    
    print("\n" + "=" * 80)
    print("🎯 测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
