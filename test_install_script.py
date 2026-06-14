"""手动测试安装脚本"""
import os
import sys
import tempfile
import subprocess

print("=" * 60)
print("手动测试安装脚本")
print("=" * 60)

# 查找批处理脚本
bat_file = os.path.join(tempfile.gettempdir(), "install_update.bat")

print(f"\n批处理脚本位置: {bat_file}")

if os.path.exists(bat_file):
    print("✅ 脚本存在")
    
    print("\n选择测试方式:")
    print("1. 直接运行批处理（推荐）")
    print("2. 使用cmd /c start运行")
    print("3. 使用subprocess.Popen运行")
    print("4. 查看脚本内容")
    print("5. 退出")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == "1":
        print("\n正在运行批处理脚本...")
        print("⚠️ 注意观察弹出的黑色窗口内容")
        print("-" * 60)
        os.system(f'"{bat_file}"')
        
    elif choice == "2":
        print("\n使用 cmd /c start 运行...")
        subprocess.Popen(f'cmd /c start "测试安装" "{bat_file}"', shell=True)
        print("✅ 已启动，请观察弹出的窗口")
        
    elif choice == "3":
        print("\n使用 subprocess.Popen 运行...")
        subprocess.Popen([bat_file], shell=True)
        print("✅ 已启动")
        
    elif choice == "4":
        print("\n批处理脚本内容:")
        print("=" * 60)
        try:
            with open(bat_file, 'r', encoding='gbk', errors='ignore') as f:
                print(f.read())
        except Exception as e:
            print(f"读取失败: {e}")
        print("=" * 60)
        
    else:
        print("退出")
        
else:
    print("❌ 脚本不存在")
    print("\n可能原因:")
    print("  1. 还没有下载过更新")
    print("  2. 脚本已被清理")
    print("\n请先运行软件并下载更新，然后再运行此测试脚本")

print("\n" + "=" * 60)
