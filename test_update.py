"""
测试自动更新功能
用于调试更新检测问题
"""
from auto_updater import check_update_sync, AutoUpdater
import requests

def test_update_detection():
    """测试更新检测功能"""
    print("🔍 测试自动更新功能")
    print("=" * 50)
    
    # 配置信息
    REPO_OWNER = "youyu551572"
    REPO_NAME = "drawinline"
    CURRENT_VERSION = "2.0.34"
    
    print(f"仓库: {REPO_OWNER}/{REPO_NAME}")
    print(f"当前版本: {CURRENT_VERSION}")
    print()
    
    # 测试API连接 - 获取所有releases
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    print(f"API地址: {api_url}")
    
    try:
        print("📡 正在连接GitHub API...")
        response = requests.get(api_url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            releases = response.json()
            print(f"✅ API连接成功")
            print(f"📦 找到 {len(releases)} 个发布版本")
            
            # 显示前3个版本
            for i, release in enumerate(releases[:3]):
                tag = release.get('tag_name', 'N/A')
                prerelease = release.get('prerelease', False)
                published = release.get('published_at', 'N/A')
                assets_count = len(release.get('assets', []))
                
                print(f"  {i+1}. {tag} {'(预发布)' if prerelease else '(正式版)'}")
                print(f"     发布时间: {published}")
                print(f"     资源文件: {assets_count} 个")
                
                # 显示资源文件
                for asset in release.get('assets', []):
                    name = asset.get('name', 'N/A')
                    size_mb = asset.get('size', 0) / 1024 / 1024
                    print(f"       - {name} ({size_mb:.1f} MB)")
                print()
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 网络连接失败: {e}")
        return
    
    print()
    print("🔍 测试更新检测逻辑...")
    
    # 测试更新检测
    try:
        updater = AutoUpdater(REPO_OWNER, REPO_NAME, CURRENT_VERSION)
        update_info = updater.check_for_updates()
        
        if update_info:
            print("🎉 发现新版本！")
            print(f"新版本: {update_info['version']}")
            print(f"下载地址: {update_info['download_url']}")
            print(f"发布页面: {update_info['html_url']}")
            print(f"更新说明: {update_info['release_notes'][:100]}...")
        else:
            print("ℹ️ 没有发现新版本")
            print("可能原因:")
            print("1. 版本号相同")
            print("2. 版本比较逻辑错误")  
            print("3. 版本被跳过")
            
    except Exception as e:
        print(f"❌ 更新检测失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_update_detection()
