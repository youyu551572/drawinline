#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YouYu自动绘画 - PyQt5现代化版本
作者：YouYu
版本：v2.0.0

使用方法：
python modern_main.py

依赖安装：
pip install PyQt5

"""

import sys
from modern_app import ModernDrawingApp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 创建主窗口（窗口会通过延迟初始化自动显示）
    window = ModernDrawingApp()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
