"""
测试百度AI生图建议API
这个API返回搜索建议，可能包含生成相关的信息
"""
import requests
import urllib.parse
import json
import os

def test_suggestion_api(query="老鼠简笔画"):
    """
    测试百度建议API
    
    URL格式：
    https://chat.baidu.com/aichat/api/aitabserver?
        ctl=sug
        &action=common
        &tk=<token>
        &query=<查询词>
        &lid=<lid>
        &ori_lid=<ori_lid>
    """
    print("=" * 80)
    print(f"🔍 测试百度建议API: {query}")
    print("=" * 80)
    
    # 构建URL
    encoded_query = urllib.parse.quote(query)
    
    # 简化的URL（不需要token可能也能工作）
    url = f"https://chat.baidu.com/aichat/api/aitabserver?ctl=sug&action=common&query={encoded_query}"
    
    print(f"\n📝 URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://chat.baidu.com/',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://chat.baidu.com'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"✅ 状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 解析JSON
            data = response.json()
            
            print(f"\n📊 响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 分析响应
            if data.get('status') == 0:
                print(f"\n✅ API调用成功!")
                
                common_sugs = data.get('data', {}).get('common_sugs', [])
                print(f"\n📝 找到 {len(common_sugs)} 个建议:")
                
                for i, sug in enumerate(common_sugs, 1):
                    print(f"  {i}. {sug.get('word', '')}")
                
                # 保存结果
                save_dir = "baidu_api_test"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                
                result_file = os.path.join(save_dir, f"suggestion_{query}.json")
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 结果已保存: {result_file}")
                
                return True, data
            else:
                print(f"❌ API返回错误: {data.get('message')}")
                return False, data
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"💥 异常: {str(e)}")
        return False, None


def analyze_api():
    """分析API特征"""
    print("\n" + "=" * 80)
    print("📊 API分析")
    print("=" * 80)
    
    print("\n🔍 发现的API端点:")
    print("```")
    print("https://chat.baidu.com/aichat/api/aitabserver")
    print("```")
    
    print("\n📝 参数说明:")
    params = {
        'ctl': 'sug (控制器类型)',
        'action': 'common (操作类型)',
        'tk': 'token (可选，认证令牌)',
        'query': '查询词 (URL编码)',
        'lid': 'log id (可选)',
        'ori_lid': 'original log id (可选)'
    }
    
    for param, desc in params.items():
        print(f"  {param:10s} - {desc}")
    
    print("\n✅ 关键发现:")
    print("1. 这是一个建议API，返回搜索建议")
    print("2. 返回JSON格式数据")
    print("3. 不需要token也可能工作")
    print("4. 但这不是图片生成API")
    
    print("\n❌ 限制:")
    print("1. 只返回文本建议，不返回图片")
    print("2. 无法用于生成图片")
    print("3. 可能需要进一步探索其他API端点")


def search_for_image_api():
    """搜索可能的图片生成API"""
    print("\n" + "=" * 80)
    print("🔍 搜索图片生成API")
    print("=" * 80)
    
    # 可能的API端点
    possible_endpoints = [
        "https://chat.baidu.com/aichat/api/aitabserver?ctl=image&action=generate",
        "https://chat.baidu.com/aichat/api/aitabserver?ctl=pic&action=generate",
        "https://chat.baidu.com/aichat/api/image/generate",
        "https://chat.baidu.com/aichat/api/pic/generate",
        "https://chat.baidu.com/api/image/text2img",
        "https://chat.baidu.com/api/v1/image/generate"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://chat.baidu.com/',
        'Content-Type': 'application/json'
    }
    
    data = {
        "query": "老鼠简笔画",
        "prompt": "老鼠简笔画"
    }
    
    for endpoint in possible_endpoints:
        print(f"\n测试: {endpoint}")
        
        try:
            # 尝试GET
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  GET: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 可能找到! 响应: {response.text[:100]}")
            
        except Exception as e:
            print(f"  GET 失败: {str(e)[:50]}")
        
        try:
            # 尝试POST
            response = requests.post(endpoint, json=data, headers=headers, timeout=10)
            print(f"  POST: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 可能找到! 响应: {response.text[:100]}")
            
        except Exception as e:
            print(f"  POST 失败: {str(e)[:50]}")


def main():
    """主函数"""
    # 测试建议API
    test_queries = ["老鼠简笔画", "小猫简笔画", "房子简笔画"]
    
    for query in test_queries:
        success, data = test_suggestion_api(query)
        print("\n" + "-" * 80)
    
    # 分析API
    analyze_api()
    
    # 搜索图片生成API
    search_for_image_api()
    
    print("\n" + "=" * 80)
    print("🎯 测试完成!")
    print("=" * 80)
    
    print("\n💡 结论:")
    print("1. 建议API可以工作，但只返回文本建议")
    print("2. 没有找到直接的图片生成API")
    print("3. 真正的生成API可能需要:")
    print("   - 特殊的token认证")
    print("   - WebSocket连接")
    print("   - 或者通过其他隐藏的端点")
    print("\n✅ 建议: 继续使用本地生成方案")


if __name__ == "__main__":
    main()
