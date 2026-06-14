#!/usr/bin/env python3
"""
更新调试脚本
用于诊断更新过程中的问题
"""
import os
import sys
import json
import subprocess
from version_info import get_version_info, get_exe_dir

def check_running_processes():
    """检查正在运行的相关进程"""
    print("=== 正在运行的进程检查 ===")
    
    target_names = ["YouYu自动绘画.exe", "modern_main.exe", "python.exe"]
    
    try:
        # 使用tasklist命令检查进程
        result = subprocess.run(
            ['tasklist', '/FO', 'CSV', '/NH'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            found = False
            
            for line in lines:
                # CSV格式: "进程名","PID","会话名","会话#","内存使用"
                parts = line.replace('"', '').split(',')
                if len(parts) >= 2:
                    proc_name = parts[0].strip()
                    pid = parts[1].strip()
                    
                    if any(name.lower() in proc_name.lower() for name in target_names):
                        print(f"  找到进程: {proc_name} (PID: {pid})")
                        found = True
            
            if not found:
                print("  未找到相关进程")
        else:
            print("  无法获取进程列表")
            
    except Exception as e:
        print(f"  检查进程时出错: {e}")

def check_version_files():
    """检查版本文件"""
    print("\n=== 版本文件检查 ===")
    
    # 检查多个可能的位置
    locations = [
        get_exe_dir(),
        os.path.dirname(os.path.abspath(__file__)),
        os.getcwd(),
        os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else None
    ]
    
    for location in filter(None, set(locations)):
        version_file = os.path.join(location, "version.json")
        print(f"\n检查: {version_file}")
        
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"  ✓ 存在，内容: {data}")
            except Exception as e:
                print(f"  ✗ 读取失败: {e}")
        else:
            print(f"  ✗ 不存在")

def check_current_version():
    """检查当前版本信息"""
    print("\n=== 当前版本信息 ===")
    version = get_version_info()
    print(f"当前版本: {version}")
    print(f"可执行文件目录: {get_exe_dir()}")
    print(f"是否打包: {getattr(sys, 'frozen', False)}")
    print(f"sys.executable: {sys.executable}")
    print(f"__file__: {__file__}")

def create_test_version_file():
    """创建测试版本文件"""
    print("\n=== 创建测试版本文件 ===")
    
    test_version = "2.0.36"
    version_data = {
        "version": test_version,
        "build_time": "2024-11-24 20:10:00"
    }
    
    version_file = os.path.join(get_exe_dir(), "version.json")
    
    try:
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, ensure_ascii=False, indent=2)
        print(f"✓ 测试版本文件已创建: {version_file}")
        print(f"  内容: {version_data}")
        
        # 验证读取
        new_version = get_version_info()
        print(f"✓ 重新读取版本: {new_version}")
        
    except Exception as e:
        print(f"✗ 创建失败: {e}")

def test_process_kill():
    """测试进程终止命令"""
    print("\n=== 进程终止测试 ===")
    
    exe_name = "YouYu自动绘画.exe"
    
    print(f"测试命令: taskkill /F /T /IM {exe_name}")
    
    # 使用tasklist检查是否有该进程
    try:
        result = subprocess.run(
            ['tasklist', '/FI', f'IMAGENAME eq {exe_name}'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        
        if result.returncode == 0 and exe_name.lower() in result.stdout.lower():
            print(f"✓ 找到进程 {exe_name}")
            
            # 模拟终止命令（不实际执行）
            cmd = f'taskkill /F /T /IM "{exe_name}"'
            print(f"建议执行: {cmd}")
        else:
            print(f"✗ 未找到进程 {exe_name}")
            print("  这是正常的，说明程序当前未运行")
            
    except Exception as e:
        print(f"  检查进程时出错: {e}")

def main():
    print("YouYu自动绘画 - 更新调试工具")
    print("=" * 50)
    
    try:
        check_current_version()
        check_version_files()
        check_running_processes()
        
        print("\n" + "=" * 50)
        response = input("是否创建测试版本文件以验证版本更新？(y/n): ")
        if response.lower() in ['y', 'yes']:
            create_test_version_file()
        
        print("\n" + "=" * 50)    
        response = input("是否测试进程终止命令？(y/n): ")
        if response.lower() in ['y', 'yes']:
            test_process_kill()
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"\n调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
