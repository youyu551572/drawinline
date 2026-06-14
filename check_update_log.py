"""检查更新安装日志"""
import os
import tempfile

# 日志文件位置
log_file = os.path.join(tempfile.gettempdir(), "update_install.log")
bat_file = os.path.join(tempfile.gettempdir(), "install_update.bat")
py_file = os.path.join(tempfile.gettempdir(), "update_version.py")

print("=" * 60)
print("更新安装诊断工具")
print("=" * 60)

print(f"\n临时文件目录: {tempfile.gettempdir()}")

# 检查批处理脚本
print(f"\n1. 批处理脚本: {bat_file}")
if os.path.exists(bat_file):
    print("   ✅ 存在")
    size = os.path.getsize(bat_file)
    print(f"   大小: {size} bytes")
    
    # 显示内容
    print("\n   内容预览:")
    try:
        with open(bat_file, 'r', encoding='gbk', errors='ignore') as f:
            lines = f.readlines()[:10]
            for i, line in enumerate(lines, 1):
                print(f"      {i}: {line.rstrip()}")
    except Exception as e:
        print(f"   ❌ 读取失败: {e}")
else:
    print("   ❌ 不存在")

# 检查Python脚本
print(f"\n2. Python脚本: {py_file}")
if os.path.exists(py_file):
    print("   ✅ 存在")
    size = os.path.getsize(py_file)
    print(f"   大小: {size} bytes")
else:
    print("   ❌ 不存在")

# 检查日志文件
print(f"\n3. 日志文件: {log_file}")
if os.path.exists(log_file):
    print("   ✅ 存在")
    size = os.path.getsize(log_file)
    print(f"   大小: {size} bytes")
    
    # 显示日志内容
    print("\n   📋 日志内容:")
    print("   " + "-" * 56)
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip():
                    print(f"   {line}")
    except Exception as e:
        print(f"   ❌ 读取失败: {e}")
    print("   " + "-" * 56)
else:
    print("   ❌ 不存在（说明脚本从未运行过）")

# 检查可能的下载文件
print(f"\n4. 检查临时下载文件:")
temp_dir = tempfile.gettempdir()
for file in os.listdir(temp_dir):
    if 'youyu' in file.lower() or 'update' in file.lower():
        full_path = os.path.join(temp_dir, file)
        if os.path.isfile(full_path):
            size = os.path.getsize(full_path) / (1024 * 1024)
            print(f"   - {file} ({size:.2f} MB)")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)

print("\n💡 下一步:")
if not os.path.exists(log_file):
    print("  ❌ 日志文件不存在 = 安装脚本从未运行")
    print("  原因可能:")
    print("     1. 批处理脚本启动失败")
    print("     2. CREATE_NEW_CONSOLE标志问题")
    print("     3. 权限不足")
    print("\n  解决方案: 手动运行批处理脚本测试")
    if os.path.exists(bat_file):
        print(f"  命令: {bat_file}")
else:
    print("  ✅ 日志文件存在，请查看上面的日志内容")
    print("     找到失败的步骤，然后告诉我")
