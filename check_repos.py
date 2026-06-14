"""
检查GitHub仓库列表
"""
import requests
import json

def check_user_repos():
    """检查用户的所有仓库"""
    try:
        # 获取用户仓库列表
        url = "https://api.github.com/users/youyu551572/repos"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ 找到 {len(repos)} 个仓库:")
            
            for repo in repos:
                name = repo.get('name', '')
                private = repo.get('private', False)
                print(f"  - {name} {'(私有)' if private else '(公开)'}")
                
                # 检查是否是drawinline相关
                if 'draw' in name.lower() or 'line' in name.lower():
                    print(f"    ⭐ 可能的目标仓库！")
                    
        else:
            print(f"❌ 获取仓库列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 网络请求失败: {e}")

def check_drawinline_repo():
    """检查drawinline仓库是否存在"""
    repo_names = ["drawinline", "drawinline-main", "YouYu自动绘画", "drawing", "auto-drawing"]
    
    for repo_name in repo_names:
        try:
            url = f"https://api.github.com/repos/youyu551572/{repo_name}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ 找到仓库: {repo_name}")
                
                # 检查releases
                releases_url = f"https://api.github.com/repos/youyu551572/{repo_name}/releases/latest"
                releases_response = requests.get(releases_url, timeout=5)
                
                if releases_response.status_code == 200:
                    release_data = releases_response.json()
                    print(f"  最新Release: {release_data.get('tag_name', 'N/A')}")
                else:
                    print(f"  无法获取Release信息: {releases_response.status_code}")
                    
            else:
                print(f"❌ 仓库不存在: {repo_name}")
                
        except Exception as e:
            print(f"❌ 检查 {repo_name} 时出错: {e}")

if __name__ == "__main__":
    print("🔍 检查GitHub仓库...")
    print("=" * 40)
    
    check_user_repos()
    
    print("\n" + "=" * 40)
    print("🔍 检查可能的仓库名...")
    
    check_drawinline_repo()
