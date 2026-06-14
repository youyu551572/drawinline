# 更新安装调试指南

## 🔍 发现的问题

### 问题1：批处理脚本字符丢失
**现象**：`wmic process` 变成 `cess`  
**原因**：UTF-8-sig编码的BOM导致  
**修复**：改用UTF-8无BOM编码，添加`newline='\r\n'`

### 问题2：PowerShell JSON格式
**现象**：版本号没有更新  
**原因**：`ConvertTo-Json`生成的格式可能与预期不符  
**修复**：手动构建JSON字符串

---

## 🧪 调试步骤

### 步骤1：查看实际的version.json
```powershell
# 在exe目录
cd C:\Users\YouYu\Desktop\nihauwoc
type version.json
```

**预期输出**：
```json
{
  "version": "2.0.42",
  "build_time": "2024-11-24 22:xx:xx"
}
```

**如果版本号不对**：PowerShell脚本失败了

### 步骤2：查看安装日志
```powershell
type C:\Users\YouYu\AppData\Local\Temp\update_install.log
```

**关键检查点**：
- `[OK] All processes closed` → 进程终止成功
- `[OK] File copied` → 文件复制成功
- `[OK] Version info updated` → 版本更新成功（PowerShell）
- `[OK] Version file exists` → 文件存在验证

### 步骤3：手动测试PowerShell脚本
```powershell
# 查看PowerShell脚本
type C:\Users\YouYu\AppData\Local\Temp\update_version.ps1

# 手动运行
powershell -ExecutionPolicy Bypass -File C:\Users\YouYu\AppData\Local\Temp\update_version.ps1

# 再次查看version.json
type C:\Users\YouYu\Desktop\nihauwoc\version.json
```

### 步骤4：使用诊断工具
```bash
cd D:\PYxiangmu\drawinline-main

# 检查version.json
python check_version_file.py

# 查看更新日志
python check_update_log.py

# 测试安装脚本
python test_install_script.py
```

---

## 🛠️ v2.0.42修复内容

1. **PowerShell JSON**：手动构建JSON字符串，确保格式正确
2. **批处理编码**：改用UTF-8无BOM + `\r\n`行尾
3. **路径转义**：PowerShell中的反斜杠转义
4. **调试输出**：PowerShell脚本输出文件路径

---

## 📋 重新测试流程

### 1. 改回v2.0.42
```bash
# 确认version.json是2.0.42
type version.json

# 打包
python build_exe.py
```

### 2. 制作v2.0.43
```bash
# 改version.json为2.0.43
python create_v2.0.43.py
python build_exe.py
# 发布到GitHub
```

### 3. 测试更新
1. 手动安装v2.0.42到测试目录
2. 运行v2.0.42，检测到v2.0.43
3. 下载并安装
4. **关键检查**：
   - 安装窗口显示完整（不要有`cess`）
   - PowerShell显示文件路径
   - 查看日志确认所有步骤成功
   - 手动打开exe，左下角显示v2.0.43

### 4. 验证version.json
```powershell
cd C:\Users\YouYu\Desktop\nihauwoc
type version.json
# 应该显示 "version": "2.0.43"
```

---

## 💡 如果还是失败

### Plan A：改用批处理写入version.json
不依赖PowerShell，直接用批处理的echo写入

### Plan B：在Python脚本中更新
在`_force_exit`之前调用`set_version_info()`

### Plan C：移除version.json更新
接受每次启动都会检测到更新（因为exe内的version.json不会改变）
