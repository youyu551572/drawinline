"""
软件内更新下载器
实现软件内直接下载更新，显示进度条
"""
import os
import sys
import time
import shutil
import tempfile
import subprocess
import requests
import json
from typing import Callable, Optional
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox
import requests


class DownloadThread(QThread):
    """下载线程"""
    progress = pyqtSignal(int, int, int)  # 当前字节，总字节，百分比
    finished = pyqtSignal(str)  # 下载完成，返回文件路径
    error = pyqtSignal(str)     # 下载失败，返回错误信息
    speed = pyqtSignal(str)     # 下载速度
    
    def __init__(self, download_url: str, save_path: str):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
        self.should_stop = False
        
    def run(self):
        """执行下载"""
        try:
            # 创建保存目录
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            
            # 开始下载
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            start_time = time.time()
            
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.should_stop:
                        return
                        
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 计算进度
                        if total_size > 0:
                            progress = int(downloaded_size * 100 / total_size)
                            self.progress.emit(downloaded_size, total_size, progress)
                            
                            # 计算下载速度
                            elapsed_time = time.time() - start_time
                            if elapsed_time > 0:
                                speed_bps = downloaded_size / elapsed_time
                                speed_text = self._format_speed(speed_bps)
                                self.speed.emit(speed_text)
            
            # 下载完成
            if not self.should_stop:
                self.finished.emit(self.save_path)
                
        except Exception as e:
            self.error.emit(str(e))
    
    def stop(self):
        """停止下载"""
        self.should_stop = True
        
    def _format_speed(self, speed_bps: float) -> str:
        """格式化下载速度"""
        if speed_bps < 1024:
            return f"{speed_bps:.1f} B/s"
        elif speed_bps < 1024 * 1024:
            return f"{speed_bps / 1024:.1f} KB/s"
        else:
            return f"{speed_bps / 1024 / 1024:.1f} MB/s"


class UpdateDownloadDialog(QDialog):
    """更新下载对话框"""
    
    def __init__(self, parent, update_info: dict):
        super().__init__(parent)
        self.update_info = update_info
        self.download_thread = None
        self.downloaded_file = None
        
        self.setWindowTitle("🎉 正在更新")
        self.setFixedSize(450, 200)
        self.setModal(True)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 标题信息
        title_label = QLabel(f"正在下载 v{self.update_info['version']}")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2196F3; margin: 10px;")
        layout.addWidget(title_label)
        
        # 文件信息
        download_url = self.update_info['download_url']
        filename = download_url.split('/')[-1] if download_url else "YouYu自动绘画.exe"
        
        file_label = QLabel(f"📦 文件: {filename}")
        file_label.setStyleSheet("margin: 5px;")
        layout.addWidget(file_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 下载信息
        info_layout = QHBoxLayout()
        
        self.size_label = QLabel("大小: 准备中...")
        self.speed_label = QLabel("速度: --")
        
        info_layout.addWidget(self.size_label)
        info_layout.addStretch()
        info_layout.addWidget(self.speed_label)
        
        layout.addLayout(info_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.clicked.connect(self.cancel_download)
        
        self.install_btn = QPushButton("✅ 安装并重启")
        self.install_btn.clicked.connect(self.install_update)
        self.install_btn.setEnabled(False)
        self.install_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QPushButton:hover:enabled {
                background-color: #45a049;
            }
        """)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.install_btn)
        
        layout.addLayout(button_layout)
        
    def start_download(self):
        """开始下载"""
        download_url = self.update_info['download_url']
        
        if not download_url or 'github.com' not in download_url:
            QMessageBox.warning(self, "错误", "无效的下载链接")
            self.reject()
            return
        
        # 创建临时文件路径
        temp_dir = tempfile.gettempdir()
        filename = download_url.split('/')[-1]
        if not filename.endswith('.exe'):
            filename = "YouYu自动绘画.exe"
        
        save_path = os.path.join(temp_dir, f"update_{filename}")
        
        # 开始下载
        self.download_thread = DownloadThread(download_url, save_path)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.error.connect(self.download_error)
        self.download_thread.speed.connect(self.update_speed)
        self.download_thread.start()
        
    def update_progress(self, downloaded: int, total: int, percentage: int):
        """更新下载进度"""
        self.progress_bar.setValue(percentage)
        
        # 格式化大小
        downloaded_mb = downloaded / 1024 / 1024
        total_mb = total / 1024 / 1024
        
        self.size_label.setText(f"大小: {downloaded_mb:.1f} / {total_mb:.1f} MB ({percentage}%)")
        
    def update_speed(self, speed: str):
        """更新下载速度"""
        self.speed_label.setText(f"速度: {speed}")
        
    def download_finished(self, file_path: str):
        """下载完成"""
        self.downloaded_file = file_path
        self.size_label.setText("✅ 下载完成！")
        self.speed_label.setText("")
        
        self.cancel_btn.setText("稍后安装")
        self.install_btn.setEnabled(True)
        
        # 自动提示安装
        QTimer.singleShot(1000, self.prompt_install)
        
    def download_error(self, error_msg: str):
        """下载失败"""
        QMessageBox.critical(self, "下载失败", f"下载更新失败:\n{error_msg}")
        self.reject()
        
    def prompt_install(self):
        """提示安装"""
        reply = QMessageBox.question(
            self, "安装更新", 
            f"v{self.update_info['version']} 下载完成！\n\n是否立即安装并重启软件？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.install_update()
            
    def cancel_download(self):
        """取消下载"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait(2000)
            
        self.reject()
        
    def install_update(self):
        """安装更新"""
        if not self.downloaded_file or not os.path.exists(self.downloaded_file):
            QMessageBox.warning(self, "错误", "未找到下载的文件")
            return
            
        try:
            # 获取当前exe路径
            current_exe = sys.executable
            if current_exe.endswith('python.exe'):
                # 开发环境，提示用户
                QMessageBox.information(
                    self, "安装更新", 
                    f"更新文件已下载到:\n{self.downloaded_file}\n\n"
                    "请手动安装新版本。"
                )
                self.accept()
                return
            
            # 检查文件权限
            if not os.access(os.path.dirname(current_exe), os.W_OK):
                QMessageBox.critical(
                    self, "权限不足", 
                    "无法写入程序目录，请以管理员身份运行软件进行更新。"
                )
                return
                
            # 显示安装确认
            reply = QMessageBox.question(
                self, "确认安装", 
                f"即将安装 v{self.update_info['version']}\n\n"
                "⚠️ 安装过程中软件会自动重启\n"
                "⚠️ 请确保已保存当前工作\n\n"
                "确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
                
            # 创建安装脚本
            install_script = self._create_install_script(current_exe, self.downloaded_file)
            
            # 创建VBScript来隐藏窗口启动批处理
            vbs_script = os.path.join(tempfile.gettempdir(), "run_update.vbs")
            vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{install_script}""", 0, False
'''
            with open(vbs_script, 'w', encoding='utf-8') as f:
                f.write(vbs_content)
            
            # 使用VBScript启动（隐藏窗口）
            import platform
            if platform.system() == 'Windows':
                subprocess.Popen(
                    f'wscript.exe "{vbs_script}"',
                    shell=True
                )
            else:
                subprocess.Popen([install_script], shell=True)
            
            # 延迟关闭，给脚本时间启动
            QTimer.singleShot(2000, self.accept)
            
            # 强制退出，确保旧程序完全关闭
            QTimer.singleShot(2500, self._force_exit)
            
        except Exception as e:
            QMessageBox.critical(self, "安装失败", f"安装更新失败:\n{e}")
    
    def _force_exit(self):
        """强制退出程序"""
        import os
        os._exit(0)  # 强制退出，不执行清理代码
            
    def _create_install_script(self, current_exe: str, new_exe: str) -> str:
        """创建安装脚本"""
        exe_name = os.path.basename(current_exe)
        exe_dir = os.path.dirname(current_exe)
        version_file = os.path.join(exe_dir, "version.json")
        new_version = self.update_info['version']
        
        # 创建日志文件路径
        log_file = os.path.join(tempfile.gettempdir(), "update_install.log")
        
        # 创建PowerShell脚本用于更新版本文件（更可靠）
        update_version_ps1 = os.path.join(tempfile.gettempdir(), "update_version.ps1")
        import time
        build_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # 转义PowerShell中的反斜杠
        version_file_ps = version_file.replace('\\', '\\\\')
        ps_script_content = f'''$ErrorActionPreference = "Stop"
try {{
    # 手动构建JSON字符串，确保格式正确
    $json = @"
{{
  "version": "{new_version}",
  "build_time": "{build_time}"
}}
"@
    [System.IO.File]::WriteAllText("{version_file_ps}", $json, [System.Text.Encoding]::UTF8)
    Write-Host "[OK] Version updated to {new_version}"
    Write-Host "File: {version_file_ps}"
    exit 0
}} catch {{
    Write-Host "[ERROR] Failed to update version: $_"
    Write-Host "Target file: {version_file_ps}"
    exit 1
}}
'''
        
        with open(update_version_ps1, 'w', encoding='utf-8') as f:
            f.write(ps_script_content)
        
        # 转义路径中的反斜杠
        current_exe_escaped = current_exe.replace('\\', '\\\\')
        
        # 创建批处理脚本（使用UTF-8编码with BOM，支持中文）
        script_content = f'''@echo off
chcp 65001 > nul
set LOG_FILE="{log_file}"

echo ================================================ > %LOG_FILE%
echo Update Installation Log >> %LOG_FILE%
echo Time: %date% %time% >> %LOG_FILE%
echo Version: {new_version} >> %LOG_FILE%
echo ================================================ >> %LOG_FILE%
echo. >> %LOG_FILE%

echo Installing update to v{new_version}...
echo [INFO] Installing update to v{new_version} >> %LOG_FILE%

echo Step 1: Waiting for old program to close...
echo [STEP 1] Waiting 3 seconds... >> %LOG_FILE%
timeout /t 3 /nobreak > nul

echo Step 2: Force terminate all processes...
echo [STEP 2] Terminating process at: {current_exe} >> %LOG_FILE%

REM 方法1: 使用wmic终止（通过路径）
wmic process where "ExecutablePath='{current_exe_escaped}'" delete >> %LOG_FILE% 2>&1
timeout /t 2 /nobreak > nul

REM 方法2: 使用taskkill终止（通过进程名，终止所有相关进程）
taskkill /F /T /IM "{exe_name}" >> %LOG_FILE% 2>&1
timeout /t 2 /nobreak > nul

REM 方法3: 再次使用wmic确保
wmic process where "ExecutablePath='{current_exe_escaped}'" delete > nul 2>&1
timeout /t 1 /nobreak > nul

echo Step 3: Verify process closed...
echo [STEP 3] Verifying and waiting... >> %LOG_FILE%

REM 循环检查，最多等待10秒
set RETRY=0
:CHECK_PROCESS
wmic process where "ExecutablePath='{current_exe_escaped}'" get ProcessId 2>NUL | findstr /r "[0-9]" > nul
if "%ERRORLEVEL%"=="0" (
    set /a RETRY+=1
    if %RETRY% LSS 5 (
        echo [WARN] Process still running, retry %RETRY%/5... >> %LOG_FILE%
        timeout /t 2 /nobreak > nul
        taskkill /F /T /IM "{exe_name}" > nul 2>&1
        wmic process where "ExecutablePath='{current_exe_escaped}'" delete > nul 2>&1
        goto CHECK_PROCESS
    ) else (
        echo [ERROR] Failed to terminate after 5 retries >> %LOG_FILE%
    )
) else (
    echo [OK] All processes closed >> %LOG_FILE%
)

echo Step 4: Backup current version...
echo [STEP 4] Backing up... >> %LOG_FILE%
if exist "{current_exe}" (
    copy "{current_exe}" "{current_exe}.backup" >> %LOG_FILE% 2>&1
)

echo Step 5: Installing new version...
echo [STEP 5] Copying files... >> %LOG_FILE%
echo   From: {new_exe} >> %LOG_FILE%
echo   To: {current_exe} >> %LOG_FILE%
copy /Y "{new_exe}" "{current_exe}" >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [ERROR] File copy failed! >> %LOG_FILE%
    echo [RETRY] Trying again... >> %LOG_FILE%
    timeout /t 3 /nobreak > nul
    copy /Y "{new_exe}" "{current_exe}" >> %LOG_FILE% 2>&1
    if errorlevel 1 (
        echo [FATAL] Installation failed! >> %LOG_FILE%
        echo Installation failed! Check log: %LOG_FILE%
        pause
        exit /b 1
    )
)
echo [OK] File copied >> %LOG_FILE%

echo Step 6: Updating version info...
echo [STEP 6] Running PowerShell script... >> %LOG_FILE%
echo   Script: "{update_version_ps1}" >> %LOG_FILE%
powershell -ExecutionPolicy Bypass -File "{update_version_ps1}" >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [WARN] PowerShell script failed >> %LOG_FILE%
) else (
    echo [OK] Version info updated >> %LOG_FILE%
)

echo Step 7: Verify installation...
echo [STEP 7] Verifying files... >> %LOG_FILE%
if exist "{current_exe}" (
    echo [OK] EXE exists >> %LOG_FILE%
) else (
    echo [ERROR] EXE missing! >> %LOG_FILE%
    pause
    exit /b 1
)

if exist "{version_file}" (
    echo [OK] Version file exists >> %LOG_FILE%
) else (
    echo [WARN] Version file missing >> %LOG_FILE%
)

echo Step 8: Cleanup temp files...
echo [STEP 8] Cleaning up... >> %LOG_FILE%
del "{new_exe}" >> %LOG_FILE% 2>&1
del "{update_version_ps1}" >> %LOG_FILE% 2>&1

echo ================================================ >> %LOG_FILE%
echo [SUCCESS] Update completed! >> %LOG_FILE%
echo ================================================ >> %LOG_FILE%

echo.
echo ================================================
echo           Update Installation Complete!
echo ================================================
echo.
echo New version v{new_version} has been installed successfully.
echo.
echo [Press any key to start the new version...]
pause > nul

echo.
echo [STEP 9] User confirmed, starting new version... >> %LOG_FILE%
REM 用户确认后，等待2秒让文件系统完全同步
timeout /t 2 /nobreak > nul
start "" "{current_exe}"
echo [STEP 9] New version started >> %LOG_FILE%

echo.
echo New version is starting...
timeout /t 1 /nobreak > nul

del "%~f0" > nul 2>&1
'''
        
        script_path = os.path.join(tempfile.gettempdir(), "install_update.bat")
        
        # 使用GBK编码，Windows批处理默认编码（但脚本中已用chcp 65001切换到UTF-8）
        # 先测试用UTF-8编码（不带BOM）
        try:
            with open(script_path, 'w', encoding='utf-8', newline='\r\n') as f:
                f.write(script_content)
        except Exception as e:
            print(f"[错误] 写入批处理脚本失败: {e}")
            # 降级到GBK
            with open(script_path, 'w', encoding='gbk', newline='\r\n', errors='ignore') as f:
                f.write(script_content)
        
        print(f"[安装脚本] 已创建: {script_path}")
        print(f"[日志文件] 位置: {log_file}")
        print(f"[PS脚本] {update_version_ps1}")
            
        return script_path
        

def show_download_dialog(parent, update_info: dict) -> bool:
    """显示下载对话框"""
    dialog = UpdateDownloadDialog(parent, update_info)
    dialog.start_download()
    
    result = dialog.exec_()
    return result == QDialog.Accepted


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 测试数据
    test_update_info = {
        'version': '2.0.35',
        'download_url': 'https://github.com/youyu551572/drawinline/releases/download/v2.0.35/YouYu.exe',
        'html_url': 'https://github.com/youyu551572/drawinline/releases/tag/v2.0.35',
        'release_notes': '测试更新'
    }
    
    show_download_dialog(None, test_update_info)
    
    app.exec_()
