"""
版本号管理模块
统一管理软件版本号
"""
import os
import json
import sys
from pathlib import Path

def get_exe_dir():
    """获取可执行文件所在目录"""
    if getattr(sys, 'frozen', False):
        # 打包后的exe
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

def get_version_info():
    """获取版本信息"""
    # 尝试多个位置查找版本文件
    version_paths = [
        os.path.join(get_exe_dir(), "version.json"),  # exe同目录
        os.path.join(os.path.dirname(__file__), "version.json"),  # 脚本同目录
        "version.json"  # 当前目录
    ]
    
    for version_file in version_paths:
        try:
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = data.get('version', '2.0.34')
                    print(f"[版本信息] 从 {version_file} 读取版本: {version}")
                    return version
        except Exception as e:
            print(f"[版本信息] 读取 {version_file} 失败: {e}")
            continue
    
    print("[版本信息] 未找到版本文件，使用默认版本: 2.0.34")
    return "2.0.34"

def set_version_info(version: str):
    """设置版本信息"""
    try:
        data = {
            'version': version,
            'build_time': __import__('time').time()
        }
        
        # 优先写入exe同目录
        version_file = os.path.join(get_exe_dir(), "version.json")
        
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"[版本信息] 版本已更新为 {version}，写入 {version_file}")
        return True
    except Exception as e:
        print(f"设置版本信息失败: {e}")
        return False

def update_version_after_install(new_version: str):
    """安装后更新版本号"""
    return set_version_info(new_version)

# 当前版本号（动态获取）
CURRENT_VERSION = get_version_info()

if __name__ == "__main__":
    print(f"当前版本: {get_version_info()}")
    
    # 测试更新版本
    if set_version_info("2.0.35"):
        print(f"更新后版本: {get_version_info()}")
    else:
        print("版本更新失败")
