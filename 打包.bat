@echo off
chcp 65001 >nul
echo ========================================
echo    YouYu自动绘画 - 打包工具
echo ========================================
echo.

echo [1/3] 检查依赖...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller未安装，正在安装...
    pip install pyinstaller
)

echo.
echo [2/3] 开始打包...
python build_exe.py

echo.
echo [3/3] 打包完成！
echo.
echo 📁 文件位置：dist\YouYu自动绘画.exe
echo.
pause
