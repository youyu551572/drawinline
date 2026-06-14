"""
从百度搜索结果中提取并下载图片
"""
import requests
import urllib.parse
import json
import re
import os

def extract_and_download_images(prompt="小猫简笔画"):
    """提取并下载百度AI生成的图片"""
    
    save_dir = "baidu_extracted_images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    print("=" * 80)
    print(f"🔍 提取百度AI生图: {prompt}")
    print("=" * 80)
    
    # 构建搜索URL
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://chat.baidu.com/search?word={encoded_prompt}&pd=csaitab&sa=b_pic_capsule"
    
    print(f"\n📝 访问URL: {url}")
    
    # 发送请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://chat.baidu.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"✅ 状态码: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # 查找所有图片URL（处理Unicode转义）
            # 模式：u=数字,数字&fm=3028或3086
            pattern = r'u=(\d+),(\d+)\\u0026fm=(\d+)\\u0026app=(\d+)'
            matches = re.findall(pattern, html)
            
            if matches:
                print(f"\n✅ 找到 {len(matches)} 个图片ID")
                
                # 构建完整URL并下载
                for i, (id1, id2, fm, app) in enumerate(matches, 1):
                    # 构建图片URL
                    img_url = f"https://gips0.baidu.com/it/u={id1},{id2}&fm={fm}&app={app}&f=JPEG&w=1024&h=1024"
                    
                    print(f"\n{i}. 下载图片...")
                    print(f"   ID: {id1},{id2}")
                    print(f"   URL: {img_url[:80]}...")
                    
                    try:
                        img_response = requests.get(img_url, headers=headers, timeout=30)
                        
                        if img_response.status_code == 200:
                            filename = f"baidu_{prompt}_{i}.jpg"
                            filepath = os.path.join(save_dir, filename)
                            
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                            
                            print(f"   ✅ 已保存: {filepath} ({len(img_response.content)} bytes)")
                        else:
                            print(f"   ❌ 下载失败: HTTP {img_response.status_code}")
                            
                    except Exception as e:
                        print(f"   💥 下载异常: {str(e)}")
                
                print(f"\n🎉 完成! 成功下载到 {save_dir} 文件夹")
                
            else:
                print("❌ 未找到图片ID")
                print("💡 可能需要登录或JavaScript渲染")
                
        else:
            print(f"❌ 请求失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"💥 异常: {str(e)}")
    
    print("\n" + "=" * 80)
    print("📊 总结")
    print("=" * 80)
    print("\n✅ 发现:")
    print("1. 搜索URL可以访问并返回HTML")
    print("2. HTML中包含图片ID（Unicode转义格式）")
    print("3. 可以构建图片URL并下载")
    
    print("\n❌ 限制:")
    print("1. 返回的是已存在的图片，不是新生成的")
    print("2. 图片ID是预设的，与提示词的关联不明确")
    print("3. 无法控制生成过程")
    
    print("\n💡 结论:")
    print("这个方法可以获取相关图片，但不是真正的生成API")
    print("仍然建议使用本地生成方案")


if __name__ == "__main__":
    # 测试不同的提示词
    prompts = ["小猫简笔画", "房子简笔画", "花朵简笔画"]
    
    for prompt in prompts:
        extract_and_download_images(prompt)
        print("\n" + "=" * 80 + "\n")
