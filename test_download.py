"""
测试软件内下载功能
"""
import sys
from PyQt5.QtWidgets import QApplication
from update_downloader import show_download_dialog

def test_download():
    """测试下载对话框"""
    app = QApplication(sys.argv)
    
    # 测试更新信息（使用真实的GitHub数据）
    update_info = {
        'version': '2.0.35',
        'download_url': 'https://github.com/youyu551572/drawinline/releases/download/v2.0.35/YouYu.exe',
        'html_url': 'https://github.com/youyu551572/drawinline/releases/tag/v2.0.35',
        'release_notes': '''## ✨ 新增功能
- 启动时自动检测新版本  
- 一键跳转下载页面
- 支持跳过特定版本更新
- 可禁用自动检查更新

## 🐛 Bug修复  
- 修复截图识别"未选择图片"错误
- 区分截图和文件两种处理模式'''
    }
    
    print("🧪 测试软件内下载功能")
    print("=" * 40)
    print(f"版本: {update_info['version']}")
    print(f"下载链接: {update_info['download_url']}")
    print()
    
    # 显示下载对话框
    result = show_download_dialog(None, update_info)
    
    if result:
        print("✅ 下载完成")
    else:
        print("❌ 下载取消")

if __name__ == "__main__":
    test_download()
