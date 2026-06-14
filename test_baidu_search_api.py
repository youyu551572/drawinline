"""
测试百度AI生图搜索API
通过搜索页面获取生成的图片
"""
import requests
import urllib.parse
import json
import re
import os

class BaiduSearchAPITester:
    """百度搜索API测试器"""
    
    def __init__(self):
        self.save_dir = "baidu_search_test"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://chat.baidu.com/'
        })
    
    def test_search_api(self, prompt="小猫简笔画"):
        """
        测试百度AI生图搜索API
        
        URL格式分析：
        https://chat.baidu.com/search?
            extParamsJson=...
            &isShowHello=
            &pd=csaitab
            &sa=b_pic_capsule
            &word=小猫简笔画  # 这是关键参数
            &applid=
            &fr=capsule_b
        """
        print("=" * 80)
        print("🔍 测试百度AI生图搜索API")
        print(f"📝 提示词: {prompt}")
        print("=" * 80)
        
        # 方法1: 尝试直接访问搜索页面
        print("\n方法1: 访问搜索页面...")
        try:
            # URL编码提示词
            encoded_prompt = urllib.parse.quote(prompt)
            
            # 构建完整URL
            ext_params = {
                "enter_type": "b_pic_capsule",
                "inputPanelExt": {
                    "showPanel": False,
                    "showPrompt": False
                },
                "openInputMode": 8
            }
            ext_params_json = urllib.parse.quote(json.dumps(ext_params))
            
            url = f"https://chat.baidu.com/search?extParamsJson={ext_params_json}&isShowHello=&pd=csaitab&sa=b_pic_capsule&word={encoded_prompt}&applid=&fr=capsule_b"
            
            print(f"URL: {url[:100]}...")
            
            response = self.session.get(url, timeout=30)
            
            print(f"状态码: {response.status_code}")
            print(f"响应大小: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # 保存HTML以供分析
                html_file = os.path.join(self.save_dir, "search_page.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"✅ HTML已保存: {html_file}")
                
                # 分析HTML，查找图片URL
                self.analyze_html(response.text)
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"💥 异常: {str(e)}")
        
        # 方法2: 尝试简化的URL
        print("\n" + "=" * 80)
        print("方法2: 测试简化URL...")
        print("=" * 80)
        
        try:
            encoded_prompt = urllib.parse.quote(prompt)
            simple_url = f"https://chat.baidu.com/search?word={encoded_prompt}&pd=csaitab&sa=b_pic_capsule"
            
            print(f"URL: {simple_url}")
            
            response = self.session.get(simple_url, timeout=30)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                html_file = os.path.join(self.save_dir, "search_simple.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"✅ HTML已保存: {html_file}")
                
                self.analyze_html(response.text)
            
        except Exception as e:
            print(f"💥 异常: {str(e)}")
        
        # 方法3: 尝试查找API端点
        print("\n" + "=" * 80)
        print("方法3: 分析可能的API端点...")
        print("=" * 80)
        
        possible_apis = [
            "https://chat.baidu.com/api/image/generate",
            "https://chat.baidu.com/api/v1/image",
            "https://yiyan.baidu.com/api/image/generate",
            "https://chat.baidu.com/csaitab/knowledge/list"
        ]
        
        for api_url in possible_apis:
            try:
                print(f"\n测试: {api_url}")
                
                data = {
                    "prompt": prompt,
                    "width": 512,
                    "height": 512
                }
                
                response = self.session.post(
                    api_url,
                    json=data,
                    timeout=10
                )
                
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"✅ 可能找到API!")
                    print(f"响应: {response.text[:200]}")
                elif response.status_code == 401:
                    print(f"🔑 需要认证")
                elif response.status_code == 403:
                    print(f"🚫 访问被拒绝")
                elif response.status_code == 404:
                    print(f"❌ 端点不存在")
                else:
                    print(f"⚠️ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"💥 异常: {str(e)}")
    
    def analyze_html(self, html_content):
        """分析HTML内容，查找图片URL"""
        print("\n📊 分析HTML内容...")
        
        # 查找图片URL模式
        patterns = [
            r'https://gips\d+\.baidu\.com/it/u=\d+,\d+[^"\']*',
            r'https://[^"\']*\.baidu\.com[^"\']*\.(jpg|jpeg|png|webp)',
            r'"url":\s*"([^"]+)"',
            r'"imageUrl":\s*"([^"]+)"',
            r'data-src="([^"]+)"',
            r'src="(https://[^"]+\.(jpg|jpeg|png))"'
        ]
        
        found_urls = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                if isinstance(match, tuple):
                    url = match[0]
                else:
                    url = match
                
                if 'baidu.com' in url and any(ext in url for ext in ['.jpg', '.jpeg', '.png', 'u=']):
                    found_urls.add(url)
        
        if found_urls:
            print(f"✅ 找到 {len(found_urls)} 个图片URL:")
            for i, url in enumerate(found_urls, 1):
                print(f"  {i}. {url[:80]}...")
                
                # 尝试下载
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        filename = f"found_image_{i}.jpg"
                        filepath = os.path.join(self.save_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        print(f"     ✅ 已下载: {filepath}")
                except:
                    pass
        else:
            print("❌ 未找到图片URL")
            print("💡 可能需要JavaScript渲染或需要登录")
    
    def generate_summary(self):
        """生成测试总结"""
        print("\n" + "=" * 80)
        print("📊 测试总结")
        print("=" * 80)
        
        print("\n🔍 发现的URL格式:")
        print("```")
        print("https://chat.baidu.com/search?")
        print("  word=<提示词>          # 关键参数")
        print("  &pd=csaitab")
        print("  &sa=b_pic_capsule")
        print("  &extParamsJson=...")
        print("```")
        
        print("\n📝 关键参数:")
        print("  word - 提示词（URL编码）")
        print("  pd - 产品标识（csaitab）")
        print("  sa - 来源标识（b_pic_capsule）")
        
        print("\n❌ 主要问题:")
        print("1. 这是一个网页搜索URL，不是API")
        print("2. 返回的是HTML页面，不是JSON数据")
        print("3. 图片可能通过JavaScript动态加载")
        print("4. 需要Cookie认证才能生成新图片")
        
        print("\n💡 可能的解决方案:")
        print("1. 使用Selenium模拟浏览器访问")
        print("2. 逆向JavaScript代码找到真正的API")
        print("3. 使用百度AI开放平台的官方API")
        print("4. 继续使用本地生成（推荐✅）")
        
        print("\n✅ 结论:")
        print("搜索URL虽然包含提示词，但仍需要浏览器环境和认证")
        print("不适合作为后端API直接调用")


def main():
    """主函数"""
    tester = BaiduSearchAPITester()
    
    # 测试搜索API
    tester.test_search_api("小猫简笔画")
    
    # 生成总结
    tester.generate_summary()
    
    print("\n" + "=" * 80)
    print("🎯 测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
