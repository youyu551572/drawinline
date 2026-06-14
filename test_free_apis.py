"""
测试所有免费AI图片生成API
找出真正可用的API服务
"""
import requests
import io
import time
import base64
import json
import urllib.parse
from PIL import Image
import os

class FreeAPITester:
    """免费API测试器"""
    
    def __init__(self):
        self.test_prompt = "simple cat drawing, black and white, minimalist"
        self.results = []
        self.save_dir = "api_test_results"
        
        # 创建测试结果目录
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def test_all_apis(self):
        """测试所有API"""
        print("🔍 开始测试所有免费AI图片生成API...")
        print(f"📝 测试提示词: {self.test_prompt}")
        print("=" * 60)
        
        # 测试所有API
        apis = [
            ("Pollinations.ai (方法1)", self.test_pollinations_v1),
            ("Pollinations.ai (方法2)", self.test_pollinations_v2),
            ("Pollinations.ai (方法3)", self.test_pollinations_v3),
            ("Craiyon (DALL-E Mini)", self.test_craiyon),
            ("Hugging Face Inference", self.test_huggingface),
            ("Replicate Free", self.test_replicate),
            ("Stability AI Free", self.test_stability),
            ("OpenAI DALL-E (需要Key)", self.test_openai),
            ("DeepAI", self.test_deepai),
            ("ArtBot", self.test_artbot),
            ("NightCafe", self.test_nightcafe),
            ("Lexica", self.test_lexica)
        ]
        
        for name, test_func in apis:
            print(f"\n🧪 测试 {name}...")
            try:
                success, result = test_func()
                self.results.append({
                    'name': name,
                    'success': success,
                    'result': result,
                    'timestamp': time.time()
                })
                
                if success:
                    print(f"✅ {name}: 成功! 图片保存到 {result}")
                else:
                    print(f"❌ {name}: 失败 - {result}")
                    
            except Exception as e:
                print(f"💥 {name}: 异常 - {str(e)}")
                self.results.append({
                    'name': name,
                    'success': False,
                    'result': f"异常: {str(e)}",
                    'timestamp': time.time()
                })
            
            # 等待1秒避免请求过快
            time.sleep(1)
        
        # 生成测试报告
        self.generate_report()
    
    def test_pollinations_v1(self):
        """测试Pollinations.ai 方法1"""
        try:
            encoded_prompt = urllib.parse.quote(self.test_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
            
            response = requests.get(url, timeout=30, verify=False, allow_redirects=True)
            
            if response.status_code == 200:
                filepath = self.save_image(response.content, "pollinations_v1")
                return True, filepath
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def test_pollinations_v2(self):
        """测试Pollinations.ai 方法2"""
        try:
            encoded_prompt = urllib.parse.quote(self.test_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            
            params = {
                'width': '512',
                'height': '512',
                'nologo': 'true'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                filepath = self.save_image(response.content, "pollinations_v2")
                return True, filepath
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def test_pollinations_v3(self):
        """测试Pollinations.ai 方法3"""
        try:
            encoded_prompt = urllib.parse.quote(self.test_prompt)
            url = f"https://pollinations.ai/prompt/{encoded_prompt}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30, verify=False, allow_redirects=True)
            
            if response.status_code == 200:
                filepath = self.save_image(response.content, "pollinations_v3")
                return True, filepath
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def test_craiyon(self):
        """测试Craiyon (DALL-E Mini)"""
        try:
            url = "https://backend.craiyon.com/generate"
            
            data = {
                "prompt": self.test_prompt
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if 'images' in result and len(result['images']) > 0:
                    # 解码base64图片
                    image_data = result['images'][0]
                    image_bytes = base64.b64decode(image_data)
                    filepath = self.save_image(image_bytes, "craiyon")
                    return True, filepath
                else:
                    return False, "无图片数据"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def test_huggingface(self):
        """测试Hugging Face Inference API"""
        try:
            # 使用免费的模型
            url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "inputs": self.test_prompt,
                "parameters": {
                    "num_inference_steps": 20,
                    "guidance_scale": 7.5
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                filepath = self.save_image(response.content, "huggingface")
                return True, filepath
            else:
                return False, f"HTTP {response.status_code}: {response.text[:100]}"
                
        except Exception as e:
            return False, str(e)
    
    def test_replicate(self):
        """测试Replicate免费API"""
        try:
            # Replicate通常需要API key，这里测试公开端点
            url = "https://replicate.com/api/predictions"
            
            data = {
                "version": "stability-ai/stable-diffusion",
                "input": {
                    "prompt": self.test_prompt,
                    "width": 512,
                    "height": 512
                }
            }
            
            response = requests.post(url, json=data, timeout=30)
            return False, f"需要API Key - HTTP {response.status_code}"
            
        except Exception as e:
            return False, str(e)
    
    def test_stability(self):
        """测试Stability AI免费端点"""
        try:
            # Stability AI通常需要API key
            url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
            
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "text_prompts": [{"text": self.test_prompt}],
                "cfg_scale": 7,
                "height": 512,
                "width": 512,
                "samples": 1,
                "steps": 20,
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            return False, f"需要API Key - HTTP {response.status_code}"
            
        except Exception as e:
            return False, str(e)
    
    def test_openai(self):
        """测试OpenAI DALL-E"""
        try:
            # OpenAI需要API key
            return False, "需要API Key"
        except Exception as e:
            return False, str(e)
    
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
                        filepath = self.save_image(img_response.content, "deepai")
                        return True, filepath
                return False, "无图片URL"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def test_artbot(self):
        """测试ArtBot"""
        try:
            # ArtBot通常是网页界面，没有直接API
            return False, "无公开API"
        except Exception as e:
            return False, str(e)
    
    def test_nightcafe(self):
        """测试NightCafe"""
        try:
            # NightCafe通常需要登录
            return False, "需要登录"
        except Exception as e:
            return False, str(e)
    
    def test_lexica(self):
        """测试Lexica"""
        try:
            # Lexica主要是搜索引擎，不是生成API
            return False, "主要是搜索功能"
        except Exception as e:
            return False, str(e)
    
    def save_image(self, image_data, api_name):
        """保存图片"""
        timestamp = int(time.time())
        filename = f"{api_name}_{timestamp}.png"
        filepath = os.path.join(self.save_dir, filename)
        
        if isinstance(image_data, bytes):
            # 直接保存字节数据
            with open(filepath, 'wb') as f:
                f.write(image_data)
        else:
            # 使用PIL保存
            image = Image.open(io.BytesIO(image_data))
            image.save(filepath)
        
        return filepath
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 API测试报告")
        print("=" * 60)
        
        successful_apis = []
        failed_apis = []
        
        for result in self.results:
            if result['success']:
                successful_apis.append(result)
            else:
                failed_apis.append(result)
        
        print(f"\n✅ 成功的API ({len(successful_apis)}):")
        for api in successful_apis:
            print(f"  - {api['name']}: {api['result']}")
        
        print(f"\n❌ 失败的API ({len(failed_apis)}):")
        for api in failed_apis:
            print(f"  - {api['name']}: {api['result']}")
        
        # 保存报告到文件
        report_file = os.path.join(self.save_dir, "test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        # 生成可用API代码
        if successful_apis:
            print(f"\n🔧 可用API集成代码:")
            self.generate_integration_code(successful_apis)
    
    def generate_integration_code(self, successful_apis):
        """生成集成代码"""
        code_file = os.path.join(self.save_dir, "working_apis.py")
        
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write('"""\n')
            f.write('可用的免费AI图片生成API\n')
            f.write('测试时间: ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n')
            f.write('"""\n\n')
            
            for i, api in enumerate(successful_apis, 1):
                api_name = api['name'].replace(' ', '_').replace('(', '').replace(')', '').lower()
                f.write(f'def generate_with_{api_name}(prompt):\n')
                f.write(f'    """{api["name"]} - 测试成功"""\n')
                f.write(f'    # 实现代码...\n')
                f.write(f'    pass\n\n')
        
        print(f"  📝 集成代码已保存到: {code_file}")


def main():
    """主函数"""
    tester = FreeAPITester()
    tester.test_all_apis()


if __name__ == "__main__":
    main()
