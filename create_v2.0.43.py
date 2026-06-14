"""创建v2.0.43测试版本"""
import json
import time

version_data = {
    "version": "2.0.43",
    "build_time": time.strftime("%Y-%m-%d %H:%M:%S")
}

with open("version.json", "w", encoding="utf-8") as f:
    json.dump(version_data, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("✅ 已创建v2.0.43测试版本")
print("=" * 60)
print(f"   版本号: {version_data['version']}")
print(f"   时间: {version_data['build_time']}")
print()
print("📋 下一步:")
print("   1. python build_exe.py")
print("   2. 发布v2.0.43到GitHub")
print("   3. 用v2.0.42测试更新到v2.0.43")
print()
print("🎯 这次应该会看到:")
print("   ✅ 安装完成后显示 'Press any key to start'")
print("   ✅ 按键后等待2秒")
print("   ✅ 新版本启动，左下角显示 v2.0.43")
print("   ✅ 不会再有版本号错误的问题")
print("=" * 60)
