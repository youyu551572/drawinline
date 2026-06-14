"""
全面的免费AI生图API测试工具
测试所有找到的免费API及其限制
"""
import requests
import time
import json
import urllib.parse
from datetime import datetime
import os

class ComprehensiveAPITester:
    """全面的API测试器"""
    
    def __init__(self):
        self.results = []
        self.test_prompt = "simple cat drawing, black and white, minimalist"
        self.save_dir = "api_comprehensive_test"
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def test_all_apis(self):
        """测试所有API"""
        print("=" * 80)
        print("🌐 全面免费AI生图API测试")
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # API列表
        apis = [
            # 1. Pollinations.AI
            {
                'name': 'Pollinations.AI',
                'category': '免费开源',
                'test_func': self.test_pollinations,
                'rate_limit': '匿名: 15秒/次, 注册: 5秒/次',
                'docs': 'https://pollinations.ai'
            },
            
            # 2. Puter.js (多模型)
            {
                'name': 'Puter.js (FLUX.1-schnell)',
                'category': '免费无限制',
                'test_func': self.test_puter_flux,
                'rate_limit': '无限制',
                'docs': 'https://developer.puter.com'
            },
            
            # 3. Hugging Face Inference
            {
                'name': 'Hugging Face Inference',
                'category': '免费有限制',
                'test_func': self.test_huggingface,
                'rate_limit': '需要Token, 有速率限制',
                'docs': 'https://huggingface.co/docs/api-inference'
            },
            
            # 4. Replicate
            {
                'name': 'Replicate',
                'category': '需要API Key',
                'test_func': self.test_replicate,
                'rate_limit': '需要付费',
                'docs': 'https://replicate.com'
            },
            
            # 5. Stability AI
            {
                'name': 'Stability AI',
                'category': '需要API Key',
                'test_func': self.test_stability,
                'rate_limit': '需要付费',
                'docs': 'https://stability.ai'
            },
            
            # 6. DeepAI
            {
                'name': 'DeepAI',
                'category': '免费有限制',
                'test_func': self.test_deepai,
                'rate_limit': '免费层有限制',
                'docs': 'https://deepai.org'
            },
            
            # 7. Craiyon (DALL-E mini)
            {
                'name': 'Craiyon (DALL-E mini)',
                'category': '免费',
                'test_func': self.test_craiyon,
                'rate_limit': '有速率限制',
                'docs': 'https://craiyon.com'
            },
            
            # 8. Segmind
            {
                'name': 'Segmind',
                'category': '免费有限制',
                'test_func': self.test_segmind,
                'rate_limit': '免费层有限制',
                'docs': 'https://segmind.com'
            }
        ]
        
        # 测试每个API
        for i, api in enumerate(apis, 1):
            print(f"\n{'='*80}")
            print(f"📊 测试 {i}/{len(apis)}: {api['name']}")
            print(f"📁 分类: {api['category']}")
            print(f"⏱️  速率限制: {api['rate_limit']}")
            print(f"📖 文档: {api['docs']}")
            print(f"{'='*80}")
            
            try:
                start_time = time.time()
                success, result, details = api['test_func']()
                elapsed = time.time() - start_time
                
                self.results.append({
                    'name': api['name'],
                    'category': api['category'],
                    'rate_limit': api['rate_limit'],
                    'success': success,
                    'result': result,
                    'details': details,
                    'elapsed_time': elapsed,
                    'timestamp': datetime.now().isoformat()
                })
                
                if success:
                    print(f"✅ 成功! 耗时: {elapsed:.2f}秒")
                    print(f"📄 详情: {details}")
                else:
                    print(f"❌ 失败: {result}")
                    
            except Exception as e:
                print(f"💥 异常: {str(e)}")
                self.results.append({
                    'name': api['name'],
                    'category': api['category'],
                    'rate_limit': api['rate_limit'],
                    'success': False,
                    'result': f"异常: {str(e)}",
                    'details': None,
                    'elapsed_time': 0,
                    'timestamp': datetime.now().isoformat()
                })
            
            # 等待避免速率限制
            time.sleep(2)
        
        # 生成报告
        self.generate_report()
    
    def test_pollinations(self):
        """测试Pollinations.AI"""
        try:
            encoded_prompt = urllib.parse.quote(self.test_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
            
            response = requests.get(url, timeout=30, verify=False)
            
            if response.status_code == 200 and len(response.content) > 1000:
                filepath = os.path.join(self.save_dir, "pollinations_test.png")
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True, filepath, f"图片大小: {len(response.content)} bytes"
            else:
                return False, f"HTTP {response.status_code}", f"响应大小: {len(response.content)} bytes"
                
        except Exception as e:
            return False, str(e), None
    
    def test_puter_flux(self):
        """测试Puter.js (需要浏览器环境)"""
        # Puter.js是JavaScript库，需要浏览器环境
        return False, "需要浏览器环境 (JavaScript)", "Puter.js是前端库，无法在Python中直接测试"
    
    def test_huggingface(self):
        """测试Hugging Face Inference API"""
        try:
            # 使用免费的Stable Diffusion模型
            url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": self.test_prompt
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                filepath = os.path.join(self.save_dir, "huggingface_test.png")
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True, filepath, f"图片大小: {len(response.content)} bytes"
            elif response.status_code == 503:
                return False, "模型正在加载中", "需要等待模型加载"
            else:
                return False, f"HTTP {response.status_code}", response.text[:200]
                
        except Exception as e:
            return False, str(e), None
    
    def test_replicate(self):
        """测试Replicate"""
        return False, "需要API Key", "Replicate需要注册并获取API Key"
    
    def test_stability(self):
        """测试Stability AI"""
        return False, "需要API Key", "Stability AI需要付费API Key"
    
    def test_deepai(self):
        """测试DeepAI"""
        try:
            url = "https://api.deepai.org/api/text2img"
            
            data = {
                'text': self.test_prompt
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'output_url' in result:
                    # 下载图片
                    img_response = requests.get(result['output_url'], timeout=30)
                    if img_response.status_code == 200:
                        filepath = os.path.join(self.save_dir, "deepai_test.png")
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        return True, filepath, f"图片URL: {result['output_url']}"
                return False, "无图片URL", str(result)
            else:
                return False, f"HTTP {response.status_code}", response.text[:200]
                
        except Exception as e:
            return False, str(e), None
    
    def test_craiyon(self):
        """测试Craiyon (DALL-E mini)"""
        try:
            url = "https://backend.craiyon.com/generate"
            
            data = {
                "prompt": self.test_prompt
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'images' in result and len(result['images']) > 0:
                    import base64
                    image_data = result['images'][0]
                    image_bytes = base64.b64decode(image_data)
                    
                    filepath = os.path.join(self.save_dir, "craiyon_test.png")
                    with open(filepath, 'wb') as f:
                        f.write(image_bytes)
                    return True, filepath, f"生成了 {len(result['images'])} 张图片"
                return False, "无图片数据", str(result)
            else:
                return False, f"HTTP {response.status_code}", response.text[:200]
                
        except Exception as e:
            return False, str(e), None
    
    def test_segmind(self):
        """测试Segmind"""
        try:
            # Segmind需要API Key
            return False, "需要API Key", "Segmind需要注册并获取API Key"
        except Exception as e:
            return False, str(e), None
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("📊 测试报告汇总")
        print("=" * 80)
        
        # 按类别分组
        categories = {}
        for result in self.results:
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # 打印每个类别
        for category, apis in categories.items():
            print(f"\n📁 {category}")
            print("-" * 80)
            
            for api in apis:
                status = "✅ 可用" if api['success'] else "❌ 不可用"
                print(f"{status} | {api['name']}")
                print(f"   速率限制: {api['rate_limit']}")
                if api['success']:
                    print(f"   耗时: {api['elapsed_time']:.2f}秒")
                    print(f"   详情: {api['details']}")
                else:
                    print(f"   原因: {api['result']}")
                print()
        
        # 统计
        total = len(self.results)
        success = sum(1 for r in self.results if r['success'])
        
        print("=" * 80)
        print(f"📈 统计信息")
        print(f"   总测试数: {total}")
        print(f"   成功: {success} ({success/total*100:.1f}%)")
        print(f"   失败: {total-success} ({(total-success)/total*100:.1f}%)")
        print("=" * 80)
        
        # 保存JSON报告
        report_file = os.path.join(self.save_dir, "test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        # 生成推荐
        print("\n" + "=" * 80)
        print("💡 推荐使用的API")
        print("=" * 80)
        
        successful_apis = [r for r in self.results if r['success']]
        if successful_apis:
            for api in successful_apis:
                print(f"✅ {api['name']}")
                print(f"   - 速率限制: {api['rate_limit']}")
                print(f"   - 响应时间: {api['elapsed_time']:.2f}秒")
                print()
        else:
            print("❌ 当前没有可用的免费API")
            print("💡 建议使用本地生成功能")


def main():
    """主函数"""
    tester = ComprehensiveAPITester()
    tester.test_all_apis()


if __name__ == "__main__":
    main()
