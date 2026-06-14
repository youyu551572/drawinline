"""
自动更新检测模块
使用 GitHub Releases API 检测新版本
"""
import requests
import webbrowser
import os
import sys
from typing import Optional, Dict
from packaging import version
import json


class AutoUpdater:
    """自动更新检测器"""
    
    def __init__(self, repo_owner: str, repo_name: str, current_version: str):
        """
        初始化更新检测器
        
        Args:
            repo_owner: GitHub仓库所有者
            repo_name: GitHub仓库名称
            current_version: 当前软件版本（如 "2.0.32"）
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        # 使用所有releases端点，包括预发布版本
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
        self.latest_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        
    def check_for_updates(self) -> Optional[Dict]:
        """
        检查是否有新版本
        
        Returns:
            dict: 包含更新信息的字典，如果没有更新则返回None
            {
                'version': '2.0.33',
                'download_url': 'https://...',
                'release_notes': '更新内容...',
                'html_url': 'https://github.com/...'
            }
        """
        try:
            # 先尝试获取最新正式版本
            response = requests.get(self.latest_api_url, timeout=5)
            latest_release = None
            
            if response.status_code == 200:
                latest_release = response.json()
            
            # 如果没有正式版本，或者我们要包括预发布版本，获取所有版本
            if latest_release is None or latest_release.get('prerelease', False):
                response = requests.get(self.api_url, timeout=5)
                
                if response.status_code != 200:
                    print(f"检查更新失败: HTTP {response.status_code}")
                    return None
                
                all_releases = response.json()
                
                # 找到最新的版本（包括预发布）
                if all_releases:
                    # 按发布时间排序，取最新的
                    latest_release = max(all_releases, 
                                       key=lambda x: x.get('published_at', ''))
            
            if not latest_release:
                print("未找到任何发布版本")
                return None
            
            # 解析版本信息
            latest_version = latest_release.get('tag_name', '').lstrip('v')
            
            # 比较版本
            if self._is_newer_version(latest_version):
                # 查找Windows可执行文件
                download_url = self._find_download_url(latest_release.get('assets', []))
                
                return {
                    'version': latest_version,
                    'download_url': download_url or latest_release.get('html_url'),
                    'release_notes': latest_release.get('body', '暂无更新说明'),
                    'html_url': latest_release.get('html_url'),
                    'published_at': latest_release.get('published_at', ''),
                    'prerelease': latest_release.get('prerelease', False)
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"网络请求失败: {e}")
            return None
        except Exception as e:
            print(f"检查更新时出错: {e}")
            return None
    
    def _is_newer_version(self, latest_version: str) -> bool:
        """
        比较版本号
        
        Args:
            latest_version: 最新版本号
            
        Returns:
            bool: 如果最新版本更新则返回True
        """
        try:
            return version.parse(latest_version) > version.parse(self.current_version)
        except Exception as e:
            print(f"版本号比较失败: {e}")
            return False
    
    def _find_download_url(self, assets: list) -> Optional[str]:
        """
        从资源列表中查找Windows可执行文件的下载链接
        
        Args:
            assets: GitHub Release资源列表
            
        Returns:
            str: 下载链接，如果没找到则返回None
        """
        for asset in assets:
            name = asset.get('name', '').lower()
            # 查找 .exe 或 .zip 文件
            if name.endswith('.exe') or name.endswith('.zip'):
                return asset.get('browser_download_url')
        return None
    
    def open_download_page(self, html_url: str):
        """
        在浏览器中打开下载页面
        
        Args:
            html_url: GitHub Release页面URL
        """
        webbrowser.open(html_url)


class UpdateConfig:
    """更新配置管理"""
    
    CONFIG_FILE = "update_config.json"
    
    @staticmethod
    def should_check_update() -> bool:
        """
        判断是否应该检查更新
        
        Returns:
            bool: 如果应该检查则返回True
        """
        try:
            if not os.path.exists(UpdateConfig.CONFIG_FILE):
                return True
            
            with open(UpdateConfig.CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查用户是否禁用了自动检查
            return config.get('auto_check', True)
            
        except Exception:
            return True
    
    @staticmethod
    def set_auto_check(enabled: bool):
        """
        设置是否自动检查更新
        
        Args:
            enabled: True为启用，False为禁用
        """
        try:
            config = {}
            if os.path.exists(UpdateConfig.CONFIG_FILE):
                with open(UpdateConfig.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['auto_check'] = enabled
            
            with open(UpdateConfig.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    @staticmethod
    def set_skip_version(version: str):
        """
        设置跳过的版本
        
        Args:
            version: 要跳过的版本号
        """
        try:
            config = {}
            if os.path.exists(UpdateConfig.CONFIG_FILE):
                with open(UpdateConfig.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['skip_version'] = version
            
            with open(UpdateConfig.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    @staticmethod
    def get_skip_version() -> Optional[str]:
        """
        获取跳过的版本
        
        Returns:
            str: 跳过的版本号，如果没有则返回None
        """
        try:
            if not os.path.exists(UpdateConfig.CONFIG_FILE):
                return None
            
            with open(UpdateConfig.CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config.get('skip_version')
            
        except Exception:
            return None


def check_update_sync(repo_owner: str, repo_name: str, current_version: str) -> Optional[Dict]:
    """
    同步检查更新（便捷函数）
    
    Args:
        repo_owner: GitHub仓库所有者
        repo_name: GitHub仓库名称
        current_version: 当前版本号
        
    Returns:
        dict: 更新信息，没有更新则返回None
    """
    if not UpdateConfig.should_check_update():
        return None
    
    updater = AutoUpdater(repo_owner, repo_name, current_version)
    update_info = updater.check_for_updates()
    
    # 检查是否是用户选择跳过的版本
    if update_info:
        skip_version = UpdateConfig.get_skip_version()
        if skip_version == update_info['version']:
            return None
    
    return update_info


# 示例使用
if __name__ == "__main__":
    # 测试更新检测
    updater = AutoUpdater(
        repo_owner="your-username",
        repo_name="drawinline",
        current_version="2.0.32"
    )
    
    update_info = updater.check_for_updates()
    
    if update_info:
        print(f"发现新版本: {update_info['version']}")
        print(f"下载地址: {update_info['download_url']}")
        print(f"更新说明: {update_info['release_notes']}")
    else:
        print("当前已是最新版本")
