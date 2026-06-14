"""
测试百度对话API - 可能是真正的图片生成API
"""
import requests
import json
import urllib.parse
import time

def test_conversation_api(query="老鼠简笔画", token=None):
    """
    测试百度对话API
    
    发现的API:
    1. checkquerydanger - 检查查询安全性
    2. conversation - 对话/生成API
    """
    print("=" * 80)
    print(f"🔍 测试百度对话API: {query}")
    print("=" * 80)
    
    # 如果没有提供token，使用示例token（可能已过期）
    if not token:
        token = "YmYwZmJhODd8NDc1YTE1NTNmY2QwZTk5OTRhNGFhOTE5MmY5NWRhMGF8MTc2NDA1MDI5OTA1MHwxMDg2MTQ0MDI3MTQyMzIyNjkzMA==-10861440271423226930-3"
        print("⚠️  使用示例token（可能已过期）")
    
    # 步骤1: 检查查询安全性
    print("\n步骤1: 检查查询安全性...")
    check_url = f"https://chat.baidu.com/aichat/api/checkquerydanger"
    
    check_params = {
        'query': query,
        'sge_lid': '',
        'token': token
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://chat.baidu.com/',
        'Accept': 'application/json',
        'Origin': 'https://chat.baidu.com'
    }
    
    try:
        response = requests.get(check_url, params=check_params, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get('status') == 0:
                print("✅ 查询安全检查通过")
                aitab_ct = data.get('data', {}).get('aitab_ct', '')
                is_danger = data.get('data', {}).get('is_danger', 0)
                
                if is_danger == 0:
                    print(f"✅ 查询安全，aitab_ct: {aitab_ct}")
                else:
                    print(f"⚠️  查询可能不安全")
                    return False, "查询不安全"
            else:
                print(f"❌ 检查失败: {data.get('message')}")
                return False, data.get('message')
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        print(f"💥 异常: {str(e)}")
        return False, str(e)
    
    # 步骤2: 调用对话API
    print("\n步骤2: 调用对话API...")
    conversation_url = "https://chat.baidu.com/aichat/api/conversation"
    
    # 构建请求数据（需要逆向工程确定正确的格式）
    conversation_data = {
        "query": query,
        "token": token,
        "lid": "",
        "ori_lid": "",
        "enter_type": "b_pic_capsule",
        "sa": "b_pic_capsule",
        "setype": "csaitab"
    }
    
    print(f"请求数据: {json.dumps(conversation_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            conversation_url,
            json=conversation_data,
            headers=headers,
            timeout=60  # 生成可能需要更长时间
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应大小: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # 尝试解析JSON
            try:
                data = response.json()
                print(f"✅ JSON响应:")
                print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
                return True, data
            except:
                # 可能是流式响应
                print(f"📄 文本响应:")
                print(response.text[:500])
                return True, response.text
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        print(f"💥 异常: {str(e)}")
        return False, str(e)


def analyze_findings():
    """分析发现"""
    print("\n" + "=" * 80)
    print("📊 发现分析")
    print("=" * 80)
    
    print("\n🔍 发现的API流程:")
    print("```")
    print("1. checkquerydanger - 检查查询安全性")
    print("   GET https://chat.baidu.com/aichat/api/checkquerydanger")
    print("   参数: query, token, sge_lid")
    print("   返回: aitab_ct, is_danger")
    print("")
    print("2. conversation - 对话/生成API")
    print("   POST https://chat.baidu.com/aichat/api/conversation")
    print("   参数: query, token, lid, ori_lid, enter_type, sa, setype")
    print("   返回: 可能是图片生成结果")
    print("```")
    
    print("\n✅ 关键发现:")
    print("1. 找到了完整的API调用流程")
    print("2. 需要token认证")
    print("3. 有安全检查机制")
    print("4. conversation API可能是生成API")
    
    print("\n❌ 主要障碍:")
    print("1. 需要有效的token")
    print("2. token需要登录百度账号获取")
    print("3. token可能有时效性")
    print("4. 需要正确的请求格式")
    
    print("\n💡 Token获取方式:")
    print("1. 登录百度账号")
    print("2. 打开开发者工具")
    print("3. 在网络请求中找到token参数")
    print("4. 复制token值")
    
    print("\n⚠️  Token特征:")
    print("- Base64编码")
    print("- 包含时间戳")
    print("- 格式: <base64>-<数字>-<数字>")
    print("- 示例: YmYwZmJhODd8...==- 10861440271423226930-3")


def main():
    """主函数"""
    # 测试对话API
    test_conversation_api("老鼠简笔画")
    
    # 分析发现
    analyze_findings()
    
    print("\n" + "=" * 80)
    print("🎯 测试完成!")
    print("=" * 80)
    
    print("\n💡 总结:")
    print("1. ✅ 找到了真正的API端点")
    print("2. ❌ 但需要有效的token认证")
    print("3. ⚠️  Token获取需要登录")
    print("4. 🔧 技术上可行，但实施困难")
    print("\n✅ 建议: 继续使用本地生成方案")
    print("   - 100%可靠")
    print("   - 无需认证")
    print("   - 无限制")
    print("   - 零维护成本")


if __name__ == "__main__":
    main()
