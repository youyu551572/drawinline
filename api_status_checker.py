"""
实时API状态检测工具
检查当前哪些API可用
"""
import requests
import urllib.parse
import time

def check_pollinations_status():
    """检查Pollinations API状态"""
    test_prompt = "simple cat"
    encoded_prompt = urllib.parse.quote(test_prompt)
    
    apis = [
        {
            'name': 'Pollinations V1',
            'url': f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true",
            'method': 'GET'
        },
        {
            'name': 'Pollinations V2', 
            'url': f"https://image.pollinations.ai/prompt/{encoded_prompt}",
            'method': 'GET',
            'params': {'width': '512', 'height': '512', 'nologo': 'true'}
        },
        {
            'name': 'Pollinations V3',
            'url': f"https://pollinations.ai/prompt/{encoded_prompt}",
            'method': 'GET'
        }
    ]
    
    print("🔍 检查API状态...")
    print("=" * 50)
    
    for api in apis:
        try:
            print(f"测试 {api['name']}...")
            
            if api['method'] == 'GET':
                if 'params' in api:
                    response = requests.get(
                        api['url'], 
                        params=api['params'],
                        timeout=10, 
                        verify=False,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
                else:
                    response = requests.get(
                        api['url'], 
                        timeout=10, 
                        verify=False,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
            
            print(f"  状态码: {response.status_code}")
            print(f"  响应大小: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print(f"  ✅ {api['name']}: 可用")
            else:
                print(f"  ❌ {api['name']}: 不可用 (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"  💥 {api['name']}: 异常 - {str(e)}")
        
        print()
        time.sleep(1)  # 避免请求过快

def check_alternative_apis():
    """检查其他免费API"""
    print("🔍 检查其他免费API...")
    print("=" * 50)
    
    # 检查一些其他的免费API
    other_apis = [
        {
            'name': 'Hugging Face (新端点)',
            'url': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1',
            'method': 'POST',
            'data': {'inputs': 'simple cat drawing'}
        },
        {
            'name': 'Replicate (公开)',
            'url': 'https://replicate.com/stability-ai/stable-diffusion',
            'method': 'GET'
        }
    ]
    
    for api in other_apis:
        try:
            print(f"测试 {api['name']}...")
            
            if api['method'] == 'POST':
                response = requests.post(
                    api['url'],
                    json=api['data'],
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                response = requests.get(api['url'], timeout=10)
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ {api['name']}: 可能可用")
            elif response.status_code == 401:
                print(f"  🔑 {api['name']}: 需要API Key")
            else:
                print(f"  ❌ {api['name']}: 不可用 (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"  💥 {api['name']}: 异常 - {str(e)}")
        
        print()
        time.sleep(1)

def main():
    """主函数"""
    print("🌐 API状态实时检测")
    print("时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    check_pollinations_status()
    check_alternative_apis()
    
    print("📊 检测完成!")
    print("💡 建议: 如果所有API都不可用，请使用本地生成功能")

if __name__ == "__main__":
    main()
