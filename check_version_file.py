"""检查version.json文件"""
import os
import json

# 检查当前目录的version.json
current_dir = os.getcwd()
version_file = os.path.join(current_dir, "version.json")

print("=" * 60)
print("Version.json 诊断工具")
print("=" * 60)

print(f"\n当前目录: {current_dir}")
print(f"Version文件: {version_file}")

if os.path.exists(version_file):
    print("\n✅ version.json存在")
    
    # 读取文件大小
    size = os.path.getsize(version_file)
    print(f"   文件大小: {size} bytes")
    
    # 读取并显示内容
    print("\n📄 文件内容:")
    print("-" * 60)
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    print("-" * 60)
    
    # 解析JSON
    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("\n✅ JSON格式正确")
        print(f"   版本号: {data.get('version', 'N/A')}")
        print(f"   编译时间: {data.get('build_time', 'N/A')}")
    except Exception as e:
        print(f"\n❌ JSON解析失败: {e}")
        
else:
    print("\n❌ version.json不存在")
    
    # 检查是否有备份
    backup_file = version_file + ".backup"
    if os.path.exists(backup_file):
        print(f"   但发现备份文件: {backup_file}")

print("\n" + "=" * 60)

# 测试PowerShell脚本
print("\n🧪 测试PowerShell更新:")
print("-" * 60)

ps_script = f"""$ErrorActionPreference = "Stop"
try {{
    $versionData = @{{
        version = "TEST.VERSION"
        build_time = "2024-11-24 TEST"
    }}
    $json = $versionData | ConvertTo-Json
    Write-Host "生成的JSON:"
    Write-Host $json
    Write-Host ""
    Write-Host "目标文件: {version_file}"
}} catch {{
    Write-Host "错误: $_"
}}
"""

import tempfile
test_ps1 = os.path.join(tempfile.gettempdir(), "test_version.ps1")
with open(test_ps1, 'w', encoding='utf-8') as f:
    f.write(ps_script)

print(f"PowerShell脚本: {test_ps1}")
print("\n执行: powershell -ExecutionPolicy Bypass -File " + test_ps1)
print("")

os.system(f'powershell -ExecutionPolicy Bypass -File "{test_ps1}"')

print("\n" + "=" * 60)
