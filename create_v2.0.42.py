"""创建v2.0.42测试版本"""
import json
import time

version_data = {
    "version": "2.0.42",
    "build_time": time.strftime("%Y-%m-%d %H:%M:%S")
}

with open("version.json", "w", encoding="utf-8") as f:
    json.dump(version_data, f, ensure_ascii=False, indent=2)

print("✅ 已创建v2.0.42测试版本")
print(f"   版本号: {version_data['version']}")
print(f"   时间: {version_data['build_time']}")
print("\n📋 测试流程:")
print("1. 打包v2.0.41: python build_exe.py")
print("2. 手动安装v2.0.41到测试目录")
print("3. 运行此脚本: python create_v2.0.42.py")
print("4. 打包v2.0.42: python build_exe.py")
print("5. 发布v2.0.42到GitHub")
print("6. 用v2.0.41测试更新到v2.0.42")
print("\n✨ 这次应该能看到:")
print("   - 旧进程完全关闭（循环检查）")
print("   - version.json正确更新（PowerShell）")
print("   - 只有新版本启动")
