#!/usr/bin/env python3
"""
版本更新测试脚本
用于手动测试版本号更新功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from version_info import get_version_info, set_version_info, get_exe_dir

def test_version_update():
    print("版本更新测试")
    print("=" * 40)
    
    # 显示当前版本
    current = get_version_info()
    print(f"当前版本: {current}")
    
    # 显示exe目录
    exe_dir = get_exe_dir()
    print(f"EXE目录: {exe_dir}")
    
    # 测试更新版本
    test_version = "2.0.36"
    print(f"\n尝试更新版本到: {test_version}")
    
    if set_version_info(test_version):
        print("✓ 版本更新成功")
        
        # 重新读取验证
        new_version = get_version_info()
        print(f"验证读取: {new_version}")
        
        if new_version == test_version:
            print("✓ 版本更新验证成功")
        else:
            print(f"✗ 版本更新验证失败，期望 {test_version}，实际 {new_version}")
    else:
        print("✗ 版本更新失败")
    
    # 恢复原始版本
    print(f"\n恢复原始版本: {current}")
    if set_version_info(current):
        print("✓ 版本恢复成功")
    else:
        print("✗ 版本恢复失败")

if __name__ == "__main__":
    test_version_update()
