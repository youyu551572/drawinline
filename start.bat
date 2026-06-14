@echo off
chcp 65001 > nul
echo ========================================
echo   图片线条自动绘画工具
echo ========================================
echo.

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo [√] 检测到虚拟环境
    call .venv\Scripts\activate.bat
) else (
    echo [!] 未检测到虚拟环境
    echo [*] 正在创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo [X] 创建虚拟环境失败
        echo [*] 请确保已安装 Python 3.7+
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
    echo [√] 虚拟环境创建成功
)

echo.
echo [*] 检查依赖包...
python -c "import cv2, numpy, pyautogui, PIL" 2>nul
if errorlevel 1 (
    echo [!] 缺少依赖包
    echo [*] 正在安装依赖包...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [X] 安装依赖包失败
        pause
        exit /b 1
    )
    echo [√] 依赖包安装完成
) else (
    echo [√] 依赖包已安装
)

echo.
echo [*] 启动程序...
echo ========================================
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [X] 程序运行出错
    pause
)
