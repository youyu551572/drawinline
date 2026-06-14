"""创建v2.0.41测试版本"""
import json
import time

version_data = {
    "version": "2.0.41",
    "build_time": time.strftime("%Y-%m-%d %H:%M:%S")
}

with open("version.json", "w", encoding="utf-8") as f:
    json.dump(version_data, f, ensure_ascii=False, indent=2)

print("✅ 已创建v2.0.41测试版本")
print(f"   版本号: {version_data['version']}")
print(f"   时间: {version_data['build_time']}")
print("\n下一步:")
print("1. python build_exe.py")
print("2. 发布到GitHub作为v2.0.41")
print("3. 用v2.0.40测试更新到v2.0.41")
