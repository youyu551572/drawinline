"""创建v2.0.44测试版本"""
import json
import time

version_data = {
    "version": "2.0.44",
    "build_time": time.strftime("%Y-%m-%d %H:%M:%S")
}

with open("version.json", "w", encoding="utf-8") as f:
    json.dump(version_data, f, ensure_ascii=False, indent=2)

print("=" * 60)
print("✅ 已创建v2.0.44测试版本")
print("=" * 60)
print(f"   版本号: {version_data['version']}")
print(f"   时间: {version_data['build_time']}")
print()
print("📋 完整测试流程:")
print()
print("【步骤1】打包v2.0.44")
print("   python build_exe.py")
print()
print("【步骤2】发布到GitHub")
print("   - 上传 dist/YouYu自动绘画.exe")
print("   - Release版本：v2.0.44")
print("   - 说明：测试VBScript隐藏窗口功能")
print()
print("【步骤3】用v2.0.43测试更新")
print("   1. 运行v2.0.43 exe")
print("   2. 检测到v2.0.44更新")
print("   3. 点击'立即更新'")
print("   4. 下载完成，点击'Yes'")
print("   5. 【关键】观察是否有黑色窗口")
print("   6. 程序自动启动")
print("   7. 左下角显示v2.0.44")
print()
print("🎯 预期效果:")
print("   ✅ 无黑色命令框（VBScript隐藏）")
print("   ✅ 后台静默安装")
print("   ✅ 几秒后自动启动")
print("   ✅ 版本号正确显示v2.0.44")
print()
print("📝 如果看到黑色窗口:")
print("   - 检查VBScript是否正确创建")
print("   - 查看日志：%TEMP%\\update_install.log")
print("   - 运行诊断：python check_update_log.py")
print("=" * 60)
