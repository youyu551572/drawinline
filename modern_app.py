#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyQt5现代化应用主类
"""

import sys
import os
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSlider, QFileDialog,
                             QCheckBox, QSpinBox, QProgressBar, QFrame, QGroupBox, QMessageBox,
                             QTabWidget, QScrollArea, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QRect, QEasingCurve, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QPen, QFont, QIcon, QKeyEvent
import webbrowser
import time

from imgprocess import ImageProcessor
from mctl import MouseController
from area_selector import select_drawing_area
from screenshot_selector import select_and_screenshot
from auto_updater import check_update_sync, UpdateConfig
from ai_generator import AIImageGenerator
from update_downloader import show_download_dialog
from version_info import get_version_info
import tkinter as tk
import json
from pathlib import Path

# 尝试导入全局热键库
try:
    from pynput import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("提示：未安装pynput库，全局热键不可用")

# 已移除selenium依赖，改为简单的提醒机制


class ImageProcessThread(QThread):
    """图像处理线程"""
    finished = pyqtSignal(list, object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, image_path, params):
        super().__init__()
        self.image_path = image_path
        self.params = params
    
    def run(self):
        try:
            self.progress.emit(10)
            processor = ImageProcessor(self.image_path)
            
            self.progress.emit(30)
            # 先预处理图像
            processor.preprocess(
                blur_kernel=self.params['blur_kernel'],
                threshold1=self.params['threshold1'],
                threshold2=self.params['threshold2'],
                use_skeleton=False,       # 关闭骨架化（会丢失细节和形变）
                skeleton_method='gentle'
            )
            
            self.progress.emit(50)
            # 再提取轮廓
            processor.extract_contours(
                min_length=self.params['min_length'],
                remove_duplicates=False,   # 关闭轮廓去重（性能优化：避免O(n²)复杂度）
                duplicate_threshold=5.0
            )
            
            self.progress.emit(70)
            strokes = processor.get_drawing_points(
                simplify=self.params['simplify'],
                epsilon=self.params['epsilon'],
                smooth=True  # 启用平滑，去除线条抖动
            )
            
            self.progress.emit(100)
            self.finished.emit(strokes, processor)
            
        except Exception as e:
            self.error.emit(str(e))


class AIGenerateThread(QThread):
    """AI生图线程"""
    finished = pyqtSignal(bool, str)  # (成功, 图片路径或错误信息)
    progress = pyqtSignal(str)  # 进度信息
    
    def __init__(self, generator, prompt):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
    
    def run(self):
        try:
            self.progress.emit("正在连接AI服务...")
            success, result = self.generator.generate_image(self.prompt)
            self.finished.emit(success, result)
        except Exception as e:
            self.finished.emit(False, f"生成失败: {str(e)}")


class DrawingThread(QThread):
    """绘画执行线程"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)  # 添加error信号
    
    def __init__(self, strokes, params):
        super().__init__()
        self.strokes = strokes
        self.params = params
        self.is_paused = False
        self.should_stop = False
    
    def run(self):
        try:
            # 输出调试信息
            print("=" * 60)
            print("绘画线程启动")
            print(f"参数: {self.params}")
            print(f"线条数量: {len(self.strokes)}")
            print("=" * 60)
            
            countdown = self.params['countdown']
            for i in range(countdown, 0, -1):
                if self.should_stop:
                    return
                self.status.emit(f"倒计时: {i}秒")
                time.sleep(1)
            
            self.status.emit("开始绘画...")
            
            img_width = self.params['img_width']
            img_height = self.params['img_height']
            draw_width = self.params['draw_width']
            draw_height = self.params['draw_height']
            offset_x = self.params['offset_x']
            offset_y = self.params['offset_y']
            
            print(f"图片尺寸: {img_width} × {img_height}")
            print(f"绘画区域: {draw_width} × {draw_height}")
            print(f"偏移量: ({offset_x}, {offset_y})")
            
            scale_x = draw_width / img_width
            scale_y = draw_height / img_height
            
            print(f"缩放比例: scale_x={scale_x:.4f}, scale_y={scale_y:.4f}")
            
            # 测试第一个点的坐标
            if self.strokes and len(self.strokes[0]) > 0:
                test_x, test_y = self.strokes[0][0]
                test_scaled_x = offset_x + int(round(test_x * scale_x))
                test_scaled_y = offset_y + int(round(test_y * scale_y))
                print(f"第一个点: 原始({test_x}, {test_y}) → 缩放后({test_scaled_x}, {test_scaled_y})")
            
            scaled_strokes = []
            for stroke in self.strokes:
                scaled_stroke = [(offset_x + int(round(x * scale_x)), 
                                offset_y + int(round(y * scale_y))) 
                               for x, y in stroke]
                scaled_strokes.append(scaled_stroke)
            
            # 创建鼠标控制器（不传speed参数）
            controller = MouseController()
            # 注意：不调用set_offset，因为offset已经在scaled_strokes中计算了
            # controller.set_offset(offset_x, offset_y)  # ❌ 不要调用，否则会double offset
            speed = self.params['speed']
            
            print(f"开始绘画，速度: {speed}")
            
            total_strokes = len(scaled_strokes)
            for idx, stroke in enumerate(scaled_strokes):
                if self.should_stop:
                    self.status.emit("已停止")
                    return
                
                while self.is_paused:
                    time.sleep(0.1)
                    if self.should_stop:
                        return
                
                # 绘制时传入speed参数
                controller.draw_stroke(stroke, speed=speed)
                
                progress = int((idx + 1) / total_strokes * 100)
                self.progress.emit(progress)
                self.status.emit(f"绘画中... {idx + 1}/{total_strokes}")
            
            self.status.emit("绘画完成！")
            self.finished.emit()
            
        except Exception as e:
            import traceback
            error_msg = f"绘画错误: {str(e)}\n{traceback.format_exc()}"
            print("=" * 60)
            print("绘画线程错误:")
            print(error_msg)
            print("=" * 60)
            self.status.emit(f"错误: {str(e)}")
            self.error.emit(error_msg)  # 发送error信号
    
    def pause(self):
        self.is_paused = True
    
    def resume(self):
        self.is_paused = False
    
    def stop(self):
        self.should_stop = True


class PreviewCanvas(QLabel):
    """预览画布组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 500)
        self.setMaximumSize(500, 500)
        self.setStyleSheet("""
            background-color: white;
            border: 2px solid #3498db;
            border-radius: 6px;
        """)
        self.setAlignment(Qt.AlignCenter)
        
        self.strokes = []
        self.img_size = (0, 0)
    
        
    def set_strokes(self, strokes, img_size):
        """设置要显示的线条"""
        self.strokes = strokes
        self.img_size = img_size
        self.update_preview()
    
    def update_preview(self, strokes=None):
        """更新预览（与main.py保持一致）"""
        # 如果传入了新的strokes，则更新
        if strokes is not None:
            self.strokes = strokes
            
        if not self.strokes or self.img_size[0] == 0:
            return
        
        canvas_size = 500
        pixmap = QPixmap(canvas_size, canvas_size)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        img_width, img_height = self.img_size
        scale = min(canvas_size / img_width, canvas_size / img_height)
        
        pen = QPen(Qt.blue, 1)
        painter.setPen(pen)
        
        # 性能优化：限制显示的线条数
        total_strokes = len(self.strokes)
        max_display_strokes = 1000
        stroke_step = max(1, total_strokes // max_display_strokes) if total_strokes > max_display_strokes else 1
        
        for idx, stroke in enumerate(self.strokes):
            # 采样显示
            if idx % stroke_step != 0 and total_strokes > max_display_strokes:
                continue
                
            if len(stroke) < 2:
                continue
            
            # 不做任何采样，直接缩放所有点（与area_selector和实际绘画完全一致）
            for i in range(len(stroke) - 1):
                x1, y1 = stroke[i]
                x2, y2 = stroke[i + 1]
                
                # 使用round进行缩放（与area_selector和实际绘画完全一致）
                x1_scaled = int(round(x1 * scale))
                y1_scaled = int(round(y1 * scale))
                x2_scaled = int(round(x2 * scale))
                y2_scaled = int(round(y2 * scale))
                
                painter.drawLine(x1_scaled, y1_scaled, x2_scaled, y2_scaled)
        
        painter.end()
        self.setPixmap(pixmap)


class ModernDrawingApp(QMainWindow):
    """现代化绘画应用主界面"""
    
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.mouse_controller = MouseController()
        self.ai_generator = AIImageGenerator()  # AI生图器
        self.drawing_thread = None
        self.processing_thread = None
        
        # 启用键盘事件
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 全局热键监听
        self.keyboard_listener = None
        self.minus_key_pressed = False
        
        # tk根窗口（延迟创建，仅在需要时创建）
        self.tk_root = None
        
        self.offset_x = 0
        self.offset_y = 0
        self.draw_width = 0
        self.draw_height = 0
        
        # B站视频链接
        self.bilibili_url = "https://www.bilibili.com/video/BV1mJUkBJEuF/?share_source=copy_web&vd_source=a7371052883da345eff9c7f52427819b"
        
        # 延迟初始化UI，避免在__init__中做太多操作
        QTimer.singleShot(0, self._delayed_init)
    
    def _delayed_init(self):
        """延迟初始化（在事件循环启动后执行）"""
        try:
            self.init_ui()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(None, "初始化失败", f"UI初始化失败:\n{e}")
            return
        
        try:
            self.apply_stylesheet()
        except Exception as e:
            import traceback
            traceback.print_exc()
        
        # 显示窗口
        self.show()
        
        # 延迟检查更新（确保窗口先显示）
        QTimer.singleShot(500, self._check_for_updates)
        
        # 延迟显示支持提醒（确保窗口先显示）
        QTimer.singleShot(800, self._show_support_reminder)
        
        # 延迟加载AI生图历史记录（确保UI完全初始化后）
        QTimer.singleShot(1500, self.refresh_ai_history)
    
    def _ensure_tk_root(self):
        """确保tk根窗口存在（延迟创建）"""
        if self.tk_root is None:
            try:
                self.tk_root = tk.Tk()
                self.tk_root.withdraw()  # 隐藏根窗口
            except Exception as e:
                print(f"创建tk根窗口失败: {e}")
                self.tk_root = None
    
    def init_ui(self):
        """初始化界面"""
        # 设置窗口属性
        self.setWindowTitle("YouYu自动绘画")
        self.setFixedSize(745, 606)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(__file__), "066fb186-3172-4c45-9c26-48873ea6665d.tmp.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建中央widget和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(6, 6, 6, 6)
        
        # 创建左右面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
    def create_left_panel(self):
        """创建左侧控制面板（标签页版）"""
        panel = QWidget()
        panel.setMaximumWidth(290)
        panel.setMinimumWidth(227)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("YouYu自动绘画")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 6px; background: #ecf0f1; border-radius: 6px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setMinimumHeight(50)  # 确保有足够高度显示AI生图内容
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #d5dbdb);
                color: #2c3e50;
                padding: 6px 8px;
                margin: 0px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
                font-size: 8pt;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d5dbdb, stop:1 #bdc3c7);
            }
        """)
        layout.addWidget(tab_widget)
        
        # === 标签页1: 图片处理 ===
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.setSpacing(6)
        tab1_layout.setContentsMargins(8, 8, 8, 8)
        
        # 系统信息
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            screen_label = QLabel(f"🖥️ 屏幕: {width}×{height}")
        except:
            screen_label = QLabel("🖥️ 屏幕: 无法获取")
        screen_label.setStyleSheet("padding: 3px; color: #666; font-size: 8pt;")
        tab1_layout.addWidget(screen_label)
        
        # 图片选择
        self.image_path_label = QLabel("未选择图片")
        self.image_path_label.setWordWrap(True)
        self.image_path_label.setStyleSheet("padding: 4px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; font-size: 8pt; color: #495057;")
        tab1_layout.addWidget(self.image_path_label)
        
        select_btn = QPushButton("📂 选择图片")
        select_btn.clicked.connect(self.select_image)
        tab1_layout.addWidget(select_btn)
        
        # 截图识别按钮
        self.screenshot_btn = QPushButton("📸 截图识别")
        self.screenshot_btn.setToolTip("框选桌面区域进行截图识别")
        self.screenshot_btn.clicked.connect(self.screenshot_recognize)
        tab1_layout.addWidget(self.screenshot_btn)
        
        # 处理参数（与main.py保持一致）
        self.blur_slider = self.create_slider("模糊", 1, 15, 7)  # 默认7（与main.py一致）
        tab1_layout.addWidget(self.blur_slider['widget'])
        
        self.threshold1_slider = self.create_slider("阈值1", 10, 200, 50)
        tab1_layout.addWidget(self.threshold1_slider['widget'])
        
        self.threshold2_slider = self.create_slider("阈值2", 50, 300, 150)
        tab1_layout.addWidget(self.threshold2_slider['widget'])
        
        
        self.min_length_slider = self.create_slider("最小长", 10, 200, 10)  # 默认10（与main.py一致）
        tab1_layout.addWidget(self.min_length_slider['widget'])
        
        self.simplify_check = QCheckBox("简化线条")
        self.simplify_check.setChecked(False)  # 默认False（与main.py一致）
        tab1_layout.addWidget(self.simplify_check)
        
        self.epsilon_slider = self.create_slider("简化度", 0.5, 10, 1.0, 0.5)  # 默认1.0（与main.py一致）
        tab1_layout.addWidget(self.epsilon_slider['widget'])
        
        process_btn = QPushButton("⚡ 处理图片")
        process_btn.clicked.connect(self.process_image)
        tab1_layout.addWidget(process_btn)
        
        tab1_layout.addStretch()
        tab_widget.addTab(tab1, "🎨 处理")
        
        # === 标签页2: 绘画控制 ===
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.setSpacing(6)
        tab2_layout.setContentsMargins(8, 8, 8, 8)
        
        self.area_label = QLabel("绘画区域：未设置")
        self.area_label.setStyleSheet("padding: 4px; background: #e3f2fd; border: 1px solid #90caf9; border-radius: 4px; font-size: 8pt; color: #1976d2;")
        tab2_layout.addWidget(self.area_label)
        
        select_area_btn = QPushButton("📍 框选绘画区域")
        select_area_btn.clicked.connect(self.select_position)
        tab2_layout.addWidget(select_area_btn)
        
        self.speed_slider = self.create_slider("速度", 0.001, 0.02, 0.001, 0.001)  # 默认0.001（与main.py一致）
        tab2_layout.addWidget(self.speed_slider['widget'])
        
        countdown_widget = QWidget()
        countdown_layout = QHBoxLayout(countdown_widget)
        countdown_layout.setContentsMargins(0, 0, 0, 0)
        countdown_layout.addWidget(QLabel("倒计时:"))
        self.countdown_spin = QSpinBox()
        self.countdown_spin.setRange(0, 60)
        self.countdown_spin.setValue(3)
        self.countdown_spin.setSuffix(" 秒")
        countdown_layout.addWidget(self.countdown_spin)
        tab2_layout.addWidget(countdown_widget)
        
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(4)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.start_btn = QPushButton("▶️")
        self.start_btn.setEnabled(False)
        self.start_btn.setToolTip("开始绘画")
        self.start_btn.clicked.connect(self.start_drawing)
        button_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸️")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setToolTip("暂停")
        self.pause_btn.clicked.connect(self.pause_drawing)
        button_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setToolTip("停止")
        self.stop_btn.clicked.connect(self.stop_drawing)
        button_layout.addWidget(self.stop_btn)
        
        tab2_layout.addWidget(button_widget)
        
        # 快捷键提示
        shortcut_label = QLabel("⌨️ 小键盘：-键停止 | +键开始")
        shortcut_label.setAlignment(Qt.AlignCenter)
        shortcut_label.setStyleSheet("""
            padding: 4px;
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            font-size: 7pt;
            font-weight: bold;
        """)
        tab2_layout.addWidget(shortcut_label)
        
        tab2_layout.addStretch()
        tab_widget.addTab(tab2, "🗌️ 绘画")
        
        # 进度和状态
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 添加弹性空间，将下方内容推到底部
        layout.addStretch()
        
        # 版本号显示（动态获取）
        current_version = get_version_info()
        version_label = QLabel(f"v{current_version}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("""
            padding: 4px;
            color: #7f8c8d;
            font-size: 8pt;
            font-weight: bold;
        """)
        layout.addWidget(version_label)
        
        # 作者信息和加群按钮（横向布局）
        author_container = QWidget()
        author_layout = QHBoxLayout(author_container)
        author_layout.setSpacing(4)
        author_layout.setContentsMargins(0, 0, 0, 0)
        
        # 加群按钮
        join_group_btn = QPushButton("🎮 加群")
        join_group_btn.clicked.connect(self.open_qq_group)
        join_group_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 4px 8px;
                font-size: 8pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        author_layout.addWidget(join_group_btn)
        
        # 作者信息
        author_info_label = QLabel("💼 YouYu")
        author_info_label.setAlignment(Qt.AlignCenter)
        author_info_label.setStyleSheet("""
            padding: 4px;
            color: #2c3e50;
            font-size: 9pt;
            font-weight: bold;
        """)
        author_layout.addWidget(author_info_label)
        
        layout.addWidget(author_container)
        
        bilibili_bottom_btn = QPushButton("🎬 B站一键三连")
        bilibili_bottom_btn.clicked.connect(self.open_bilibili)
        bilibili_bottom_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b9d;
                color: white;
                padding: 6px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #ff4d88;
            }
        """)
        layout.addWidget(bilibili_bottom_btn)
        
        # === 标签页3: 作者支持 ===
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.setSpacing(0)
        tab3_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用横向滚动条
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 需要时显示纵向滚动条
        
        # 滚动区域内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(8, 8, 8, 8)
        
        # 收款码标题
        qrcode_title = QLabel("💖 感谢支持")
        qrcode_title.setAlignment(Qt.AlignCenter)
        qrcode_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        qrcode_title.setStyleSheet("color: #e74c3c; padding: 8px;")
        scroll_layout.addWidget(qrcode_title)
        
        # 收款码容器（纵向布局）
        qrcode_container = QWidget()
        qrcode_layout = QVBoxLayout(qrcode_container)
        qrcode_layout.setSpacing(8)
        qrcode_layout.setContentsMargins(4, 4, 4, 4)
        
        # 加载并显示第一张收款码
        qrcode1_label = QLabel()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        qrcode1_path = os.path.join(script_dir, "1763310716369.jpg")
        
        if os.path.exists(qrcode1_path):
            try:
                pixmap1 = QPixmap(qrcode1_path)
                if not pixmap1.isNull() and pixmap1.width() > 0 and pixmap1.height() > 0:
                    if pixmap1.width() > 2000 or pixmap1.height() > 2000:
                        pixmap1 = pixmap1.scaled(800, 800, Qt.KeepAspectRatio, Qt.FastTransformation)
                    scaled_pixmap1 = pixmap1.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    qrcode1_label.setPixmap(scaled_pixmap1)
                else:
                    qrcode1_label.setText("收款码1\n(加载失败)")
            except Exception as e:
                print(f"加载收款码1失败: {e}")
                qrcode1_label.setText("收款码1\n(加载失败)")
        else:
            qrcode1_label.setText("收款码1\n(文件不存在)")
        
        qrcode1_label.setAlignment(Qt.AlignCenter)
        qrcode1_label.setStyleSheet("""
            padding: 2px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            min-width: 40px; 
            min-height: 40px;
        """)
        qrcode1_label.setCursor(Qt.PointingHandCursor)  # 鼠标悬停时显示手型
        qrcode1_label.setToolTip("点击查看完整收款码")
        # 启用鼠标事件
        qrcode1_label.mousePressEvent = lambda event: self.show_qrcode_fullsize(qrcode1_path)
        qrcode_layout.addWidget(qrcode1_label)
        
        # 加载并显示第二张收款码
        qrcode2_label = QLabel()
        qrcode2_path = os.path.join(script_dir, "IMG_4639.png")
        
        if os.path.exists(qrcode2_path):
            try:
                pixmap2 = QPixmap(qrcode2_path)
                if not pixmap2.isNull() and pixmap2.width() > 0 and pixmap2.height() > 0:
                    if pixmap2.width() > 2000 or pixmap2.height() > 2000:
                        pixmap2 = pixmap2.scaled(800, 800, Qt.KeepAspectRatio, Qt.FastTransformation)
                    scaled_pixmap2 = pixmap2.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    qrcode2_label.setPixmap(scaled_pixmap2)
                else:
                    qrcode2_label.setText("收款码2\n(加载失败)")
            except Exception as e:
                print(f"加载收款码2失败: {e}")
                qrcode2_label.setText("收款码2\n(加载失败)")
        else:
            qrcode2_label.setText("收款码2\n(文件不存在)")
        
        qrcode2_label.setAlignment(Qt.AlignCenter)
        qrcode2_label.setStyleSheet("""
            padding: 2px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            min-width: 40px; 
            min-height: 40px;
        """)
        qrcode2_label.setCursor(Qt.PointingHandCursor)  # 鼠标悬停时显示手型
        qrcode2_label.setToolTip("点击查看完整收款码")
        # 启用鼠标事件
        qrcode2_label.mousePressEvent = lambda event: self.show_qrcode_fullsize(qrcode2_path)
        qrcode_layout.addWidget(qrcode2_label)
        
        scroll_layout.addWidget(qrcode_container)
        
        # 分隔线
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setStyleSheet("background-color: #e0e0e0;")
        scroll_layout.addWidget(separator1)
        
        # 支持者名单标题
        supporters_title = QLabel("🌟 感谢以下支持者")
        supporters_title.setAlignment(Qt.AlignCenter)
        supporters_title.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
        supporters_title.setStyleSheet("color: #3498db; padding: 8px;")
        scroll_layout.addWidget(supporters_title)
        
        # 支持者名单
        supporters_text = QLabel(
            "名字：S*J\n"
            "时间：2025-06-09 06:34:05\n"
            "备注：up主加油\n"
            "━━━━━━━━━━━━\n\n"
            "感谢每一位支持者！\n"
            "您的支持是我持续更新的最大动力！❤️"
        )
        supporters_text.setAlignment(Qt.AlignLeft)  # 改为左对齐，方便阅读
        supporters_text.setStyleSheet("""
            color: #666; 
            font-size: 8pt; 
            padding: 10px; 
            line-height: 1.8;
            background: #f9f9f9;
            border-radius: 4px;
        """)
        supporters_text.setWordWrap(True)
        scroll_layout.addWidget(supporters_text)
        
        scroll_layout.addStretch()
        
        # 设置滚动区域内容
        scroll_area.setWidget(scroll_content)
        tab3_layout.addWidget(scroll_area)
        
        tab_widget.addTab(tab3, "💖 支持")
        
        # === 标签页4: AI生图 ===
        tab4 = QWidget()
        tab4_layout = QVBoxLayout(tab4)
        tab4_layout.setSpacing(6)
        tab4_layout.setContentsMargins(6, 6, 6, 6)
        
        # AI生图标题
        ai_title = QLabel("AI生成简笔画")
        ai_title.setAlignment(Qt.AlignCenter)
        ai_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        ai_title.setStyleSheet("color: #9b59b6; padding: 4px;")
        tab4_layout.addWidget(ai_title)
        
        # 说明文字
        ai_desc = QLabel(
            "使用AI生成简笔画素材\n"
            "专为自动绘画优化\n"
            "完全免费使用"
        )
        ai_desc.setAlignment(Qt.AlignCenter)
        ai_desc.setStyleSheet("""
            color: #666;
            font-size: 8pt;
            padding: 6px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
        """)
        tab4_layout.addWidget(ai_desc)
        
        # 输入描述标签
        input_label = QLabel("请输入描述：")
        input_label.setFont(QFont("Microsoft YaHei", 8, QFont.Bold))
        input_label.setStyleSheet("color: #495057; margin-top: 4px;")
        tab4_layout.addWidget(input_label)
        
        # 文本输入框
        self.ai_prompt_edit = QTextEdit()
        self.ai_prompt_edit.setPlaceholderText(
            "请描述您想要生成的简笔画内容...\n\n"
            "例如：\n"
            "• 一只坐着的小猫\n"
            "• 简单的房子轮廓\n"
            "• 一朵花的线条画\n"
            "• 可爱的卡通人物"
        )
        self.ai_prompt_edit.setMaximumHeight(70)
        self.ai_prompt_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px;
                background: white;
                font-size: 8pt;
            }
            QTextEdit:focus {
                border-color: #9b59b6;
            }
        """)
        tab4_layout.addWidget(self.ai_prompt_edit)
        
        # 快速选择按钮组
        quick_layout = QHBoxLayout()
        quick_buttons = [
            ("小猫", "一只可爱的小猫，简笔画风格，黑白线条"),
            ("房子", "简单的房子，线条画，轮廓清晰"),
            ("花朵", "一朵简单的花，线条画风格"),
            ("笑脸", "简单的笑脸表情，圆形轮廓")
        ]
        
        for text, prompt in quick_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: #ecf0f1;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 7pt;
                }
                QPushButton:hover {
                    background: #d5dbdb;
                }
            """)
            btn.clicked.connect(lambda checked, p=prompt: self.ai_prompt_edit.setPlainText(p))
            quick_layout.addWidget(btn)
        
        tab4_layout.addLayout(quick_layout)
        
        # AI生图按钮
        self.ai_generate_btn = QPushButton("生成简笔画")
        self.ai_generate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9b59b6, stop:1 #8e44ad);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 8pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8e44ad, stop:1 #7d3c98);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7d3c98, stop:1 #6c3483);
            }
        """)
        self.ai_generate_btn.clicked.connect(self.generate_ai_image_direct)
        tab4_layout.addWidget(self.ai_generate_btn)
        
        # 生成历史
        history_label = QLabel("生成历史")
        history_label.setFont(QFont("Microsoft YaHei", 8, QFont.Bold))
        history_label.setStyleSheet("color: #495057; margin-top: 8px;")
        tab4_layout.addWidget(history_label)
        
        # 历史列表（滚动区域）
        self.ai_history_scroll = QScrollArea()
        self.ai_history_scroll.setWidgetResizable(True)
        self.ai_history_scroll.setMaximumHeight(120)
        self.ai_history_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background: white;
            }
        """)
        
        self.ai_history_widget = QWidget()
        self.ai_history_layout = QVBoxLayout(self.ai_history_widget)
        self.ai_history_layout.setContentsMargins(8, 8, 8, 8)
        
        # 默认提示
        no_history_label = QLabel("暂无生成历史")
        no_history_label.setAlignment(Qt.AlignCenter)
        no_history_label.setStyleSheet("color: #999; padding: 20px;")
        self.ai_history_layout.addWidget(no_history_label)
        
        self.ai_history_scroll.setWidget(self.ai_history_widget)
        tab4_layout.addWidget(self.ai_history_scroll)
        
        tab4_layout.addStretch()
        tab_widget.addTab(tab4, "AI生图")
        
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self):
        """创建右侧预览区域"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("📺 预览")
        title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 4px; background: #ecf0f1; border-radius: 6px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.preview_canvas = PreviewCanvas()
        layout.addWidget(self.preview_canvas, 0, Qt.AlignCenter)
        
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        layout.addStretch()
        
        return panel
    
    def create_slider(self, label_text, min_val, max_val, default_val, step=1):
        """创建滑块组件"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(label_text + ":")
        label.setMinimumWidth(50)
        label.setStyleSheet("font-size: 8pt;")
        layout.addWidget(label)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(int(min_val / step))
        slider.setMaximum(int(max_val / step))
        slider.setValue(int(default_val / step))
        layout.addWidget(slider)
        
        value_label = QLabel(str(default_val))
        value_label.setMinimumWidth(45)
        value_label.setAlignment(Qt.AlignRight)
        layout.addWidget(value_label)
        
        def update_label(value):
            actual_value = value * step
            value_label.setText(f"{actual_value:.3f}" if step < 1 else str(int(actual_value)))
        
        slider.valueChanged.connect(update_label)
        
        return {'widget': widget, 'slider': slider, 'label': value_label, 'step': step}
    
    def select_image(self):
        """选择图片"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)")
        
        if file_path:
            self.image_path_label.setText(file_path)
            self.image_processor = ImageProcessor(file_path)
            
            img_width, img_height = self.image_processor.get_image_size()
            self.update_status(f"图片已加载: {img_width}×{img_height}", "success")
    
    def screenshot_recognize(self):
        """截图识别"""
        self.update_status("准备截图识别，请框选要识别的区域...", "info")
        
        # 最小化主窗口（避免影响截图）
        self.showMinimized()
        QApplication.processEvents()
        time.sleep(0.2)  # 短暂延迟确保窗口最小化
        
        # 确保tk根窗口存在
        self._ensure_tk_root()
        
        try:
            # 调用截图选择器
            screenshot_array = select_and_screenshot()
            
            # 恢复主窗口
            self.showNormal()
            self.activateWindow()
            
            if screenshot_array is None:
                self.update_status("截图已取消", "info")
                return
            
            # 创建ImageProcessor并加载截图
            self.image_processor = ImageProcessor()
            
            # 将numpy数组设置为原始图片
            self.image_processor.original_image = screenshot_array
            height, width = screenshot_array.shape[:2]
            
            # 更新图片路径标签（显示截图信息）
            self.image_path_label.setText(f"📸 截图识别 ({width}×{height})")
            
            self.update_status(f"截图成功: {width}×{height}，开始处理...", "success")
            
            # 自动处理图片
            self.process_image()
            
        except Exception as e:
            self.showNormal()
            self.activateWindow()
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"截图识别失败：\n\n{str(e)}")
            self.update_status("截图识别失败", "error")
    
    def process_image(self):
        """处理图片"""
        if not self.image_processor:
            QMessageBox.warning(self, "警告", "请先选择图片！")
            return
        
        self.update_status("处理中...", "info")
        
        # 获取参数
        blur = int(self.blur_slider['slider'].value() * self.blur_slider['step'])
        # 确保blur_kernel是奇数（OpenCV要求）
        if blur % 2 == 0:
            blur += 1
        
        params = {
            'blur_kernel': blur,
            'threshold1': int(self.threshold1_slider['slider'].value() * self.threshold1_slider['step']),
            'threshold2': int(self.threshold2_slider['slider'].value() * self.threshold2_slider['step']),
            'min_length': int(self.min_length_slider['slider'].value() * self.min_length_slider['step']),
            'simplify': self.simplify_check.isChecked(),
            'epsilon': self.epsilon_slider['slider'].value() * self.epsilon_slider['step']
        }
        
        # 如果是截图识别（image_processor已存在且有original_image），直接处理
        if self.image_processor and self.image_processor.original_image is not None and not self.image_path_label.text().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            try:
                self.progress_bar.setValue(10)
                
                # 预处理图像
                self.image_processor.preprocess(
                    blur_kernel=params['blur_kernel'],
                    threshold1=params['threshold1'],
                    threshold2=params['threshold2'],
                    use_skeleton=False,       # 关闭骨架化（会丢失细节和形变）
                    skeleton_method='gentle'
                )
                self.progress_bar.setValue(50)
                
                # 提取轮廓
                self.image_processor.extract_contours(
                    min_length=params['min_length'],
                    remove_duplicates=False,   # 关闭轮廓去重（性能优化：避免O(n²)复杂度）
                    duplicate_threshold=5.0
                )
                self.progress_bar.setValue(70)
                
                # 获取绘画点
                strokes = self.image_processor.get_drawing_points(
                    simplify=params['simplify'],
                    epsilon=params['epsilon'],
                    smooth=True  # 启用平滑，去除线条抖动
                )
                self.progress_bar.setValue(100)
                
                # 直接调用完成处理
                self.on_process_finished(strokes, self.image_processor)
                
            except Exception as e:
                self.on_process_error(str(e))
        else:
            # 文件路径模式，使用线程处理
            self.process_thread = ImageProcessThread(self.image_path_label.text(), params)
            self.process_thread.finished.connect(self.on_process_finished)
            self.process_thread.error.connect(self.on_process_error)
            self.process_thread.progress.connect(self.progress_bar.setValue)
            self.process_thread.start()
    
    def on_process_finished(self, strokes, processor):
        """处理完成"""
        self.strokes = strokes
        self.image_processor = processor
        self.start_btn.setEnabled(True)
        
        img_width, img_height = self.image_processor.get_image_size()
        total_points = sum(len(stroke) for stroke in strokes)
        
        self.update_status(f"处理完成！线条: {len(strokes)}, 点数: {total_points}", "success")
        
        self.info_label.setText(
            f"✅ 识别完成 | 📏 {img_width}×{img_height} | 📝 {len(strokes)}条线 | 📍 {total_points}点"
        )
        
        self.preview_canvas.set_strokes(strokes, (img_width, img_height))
        self.progress_bar.setValue(0)
    
    def on_process_error(self, error_msg):
        """处理错误"""
        self.update_status(f"错误: {error_msg}", "error")
        QMessageBox.critical(self, "错误", error_msg)
        self.progress_bar.setValue(0)
    
    def select_position(self):
        """框选绘画区域（修复PyQt5与tkinter冲突）"""
        if not self.strokes:
            QMessageBox.warning(self, "警告", "请先处理图片！")
            return
        
        self.update_status("正在打开区域选择器...", "info")
        
        try:
            # 最小化主窗口
            self.showMinimized()
            
            # 处理所有挂起的事件，确保窗口已最小化
            QApplication.processEvents()
            time.sleep(0.1)  # 短暂延迟确保窗口状态更新
            
            # 准备线条数据和图片尺寸用于预览
            strokes = self.strokes
            image_size = self.image_processor.get_image_size()
            
            # 确保tk根窗口存在（延迟创建）
            self._ensure_tk_root()
            
            # tkinter必须在主线程运行，直接调用
            # PyQt5窗口已最小化，不会干扰tkinter
            result = select_drawing_area(strokes=strokes, image_size=image_size)
            
            # 确保tk根窗口保持隐藏
            if self.tk_root:
                self.tk_root.withdraw()
                self.tk_root.update()  # 更新状态
            
            # 恢复主窗口显示
            self.showNormal()
            self.activateWindow()
            if result:
                self.offset_x, self.offset_y, self.draw_width, self.draw_height = result
                self.area_label.setText(
                    f"位置: ({self.offset_x}, {self.offset_y})\n"
                    f"尺寸: {self.draw_width} × {self.draw_height}"
                )
                self.start_btn.setEnabled(True)
                self.update_status(f"已选择区域: 位置({self.offset_x}, {self.offset_y}), 尺寸({self.draw_width} × {self.draw_height})", "success")
            else:
                self.update_status("未选择区域", "info")
                
        except Exception as e:
            self.showNormal()
            self.activateWindow()
            QMessageBox.critical(self, "错误", f"选择区域时出错：{str(e)}")
            self.update_status("区域选择失败", "error")
    
    def start_drawing(self):
        """开始绘画（与main.py一致）"""
        if not self.strokes:
            QMessageBox.warning(self, "警告", "请先处理图片！")
            return
        
        if self.draw_width == 0 or self.draw_height == 0:
            QMessageBox.warning(self, "警告", "请先框选绘画区域！")
            return
        
        # 取消确认对话框，直接开始
        countdown = self.countdown_spin.value()
        
        # 启动全局热键监听
        if KEYBOARD_AVAILABLE:
            self._start_keyboard_listener()
        
        # 最小化主窗口，避免遮挡绘画区域
        self.showMinimized()
        
        img_width, img_height = self.image_processor.get_image_size()
        
        # 计算速度参数
        speed_value = self.speed_slider['slider'].value() * self.speed_slider['step']
        print(f"速度滑块值: {self.speed_slider['slider'].value()}")
        print(f"速度步长: {self.speed_slider['step']}")
        print(f"计算后速度: {speed_value}")
        
        params = {
            'countdown': countdown,
            'speed': speed_value,
            'img_width': img_width,
            'img_height': img_height,
            'draw_width': self.draw_width,
            'draw_height': self.draw_height,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y
        }
        
        self.drawing_thread = DrawingThread(self.strokes, params)
        self.drawing_thread.progress.connect(self.progress_bar.setValue)
        self.drawing_thread.status.connect(lambda text: self.update_status(text, "info"))
        self.drawing_thread.finished.connect(self.on_drawing_finished)
        self.drawing_thread.error.connect(self.on_drawing_error)  # 连接错误信号
        self.drawing_thread.start()
        
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
    
    def pause_drawing(self):
        """暂停/继续绘画"""
        if self.drawing_thread:
            if self.drawing_thread.is_paused:
                self.drawing_thread.resume()
                self.pause_btn.setText("⏸️ 暂停")
            else:
                self.drawing_thread.pause()
                self.pause_btn.setText("▶️ 继续")
    
    def stop_drawing(self):
        """停止绘画（与main.py一致）"""
        if self.drawing_thread:
            self.drawing_thread.stop()
            
            # 停止全局热键监听
            if KEYBOARD_AVAILABLE and self.keyboard_listener:
                self._stop_keyboard_listener()
            
            # 恢复主窗口显示
            self.showNormal()
            self.activateWindow()
            
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.update_status("已停止", "info")
    
    def on_drawing_finished(self):
        """绘画完成（与main.py一致）"""
        # 停止全局热键监听
        if KEYBOARD_AVAILABLE and self.keyboard_listener:
            self._stop_keyboard_listener()
        
        # 恢复主窗口显示
        self.showNormal()
        self.activateWindow()
        
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # 显示完成消息
        QMessageBox.information(self, "完成", "绘画完成！")
    
    def on_drawing_error(self, error_msg):
        """绘画错误处理"""
        print("=" * 60)
        print("绘画错误回调:")
        print(error_msg)
        print("=" * 60)
        
        # 恢复主窗口显示
        self.showNormal()
        self.activateWindow()
        
        # 恢复按钮状态
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # 显示详细错误信息
        self.update_status("绘画失败", "error")
        QMessageBox.critical(self, "绘画错误", f"绘画过程中发生错误：\n\n{error_msg}")
    
    def update_status(self, text, status_type="info"):
        """更新状态"""
        self.status_label.setText(text)
        
        if status_type == "success":
            self.status_label.setStyleSheet("padding: 8px; background-color: #d4edda; color: #155724; border-radius: 4px; font-weight: bold; border: 1px solid #c3e6cb;")
        elif status_type == "error":
            self.status_label.setStyleSheet("padding: 8px; background-color: #f8d7da; color: #721c24; border-radius: 4px; font-weight: bold; border: 1px solid #f5c6cb;")
        else:
            self.status_label.setStyleSheet("padding: 8px; background-color: #e3f2fd; color: #1976d2; border-radius: 4px; font-weight: bold; border: 1px solid #90caf9;")
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def show_qrcode_fullsize(self, image_path):
        """显示完整尺寸的收款码"""
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "提示", "收款码文件不存在")
            return
        
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("💖 收款码")
        dialog.setModal(True)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 加载完整尺寸图片
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "提示", "无法加载收款码图片")
            return
        
        # 限制最大显示尺寸（避免太大）
        max_size = 600
        if pixmap.width() > max_size or pixmap.height() > max_size:
            pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # 创建标签显示图片
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        
        # 提示文字
        tip_label = QLabel("💳 请使用微信或支付宝扫描二维码")
        tip_label.setAlignment(Qt.AlignCenter)
        tip_label.setStyleSheet("""
            color: #666;
            font-size: 10pt;
            padding: 10px;
        """)
        layout.addWidget(tip_label)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        # 设置对话框大小并显示
        dialog.adjustSize()
        dialog.exec_()
    
    def open_bilibili(self):
        """打开B站视频"""
        webbrowser.open(self.bilibili_url)
        self.update_status("已打开B站视频，请完成三连！", "info")
    
    def open_qq_group(self):
        """打开QQ群链接"""
        qq_group_url = "https://qm.qq.com/q/ybikpom94Q"
        webbrowser.open(qq_group_url)
        self.update_status("已打开QQ群链接，欢迎加入交流！", "info")
    
    def _check_for_updates(self):
        """检查更新（后台异步）"""
        try:
            # 使用GitHub信息（需要修改为你的实际仓库）
            REPO_OWNER = "youyu551572"  # TODO: 修改为你的GitHub用户名
            REPO_NAME = "drawinline"      # TODO: 修改为你的仓库名
            CURRENT_VERSION = get_version_info()
            
            print(f"[更新检测] 开始检查更新: {REPO_OWNER}/{REPO_NAME}, 当前版本: {CURRENT_VERSION}")
            
            # 后台检查更新
            update_info = check_update_sync(REPO_OWNER, REPO_NAME, CURRENT_VERSION)
            
            if update_info:
                print(f"[更新检测] 发现新版本: {update_info['version']}")
                self._show_update_dialog(update_info)
            else:
                print(f"[更新检测] 没有发现新版本")
                
        except Exception as e:
            print(f"[更新检测] 检查更新失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_update_dialog(self, update_info: dict):
        """显示更新对话框"""
        msg = QMessageBox(self)
        msg.setWindowTitle("🎉 发现新版本")
        msg.setIcon(QMessageBox.Information)
        
        # 构建更新信息
        release_notes = update_info['release_notes']
        if len(release_notes) > 300:
            release_notes = release_notes[:300] + "..."
        
        msg.setText(
            f"<b>发现新版本: v{update_info['version']}</b><br><br>"
            f"当前版本: v{get_version_info()}<br><br>"
            f"<b>更新内容：</b><br>"
            f"{release_notes.replace(chr(10), '<br>')}"
        )
        
        # 添加按钮（移除"跳过版本"，避免误点）
        download_btn = msg.addButton("⬇️ 立即更新", QMessageBox.AcceptRole)
        later_btn = msg.addButton("⏰ 稍后提醒", QMessageBox.NoRole)
        
        msg.setDefaultButton(download_btn)
        msg.exec_()
        
        if msg.clickedButton() == download_btn:
            # 软件内下载
            self.update_status("正在准备下载更新...", "info")
            success = show_download_dialog(self, update_info)
            if success:
                self.update_status("更新安装完成", "success")
            else:
                self.update_status("更新下载已取消", "info")
        else:
            # 稍后提醒（不做任何操作）
            pass
    
    def _show_support_reminder(self):
        """显示支持提醒对话框"""
        msg = QMessageBox(self)
        msg.setWindowTitle("💖 支持作者")
        msg.setIcon(QMessageBox.Information)
        msg.setText(
            "🎨 <b>YouYu自动绘画</b>\n\n"
            "制作不易，如果觉得这个工具不错，\n"
            "可以帮忙一键三连支持一下吗？\n\n"
            "❤️ 点赞   💎 投币   ⭐ 收藏\n\n"
            "您的支持是我持续更新的最大动力！"
        )
        
        # 添加两个按钮
        ok_btn = msg.addButton("✅ 已三连", QMessageBox.AcceptRole)
        go_btn = msg.addButton("🎬 去三连", QMessageBox.ActionRole)
        msg.setDefaultButton(ok_btn)
        
        msg.exec_()
        
        # 判断用户点击了哪个按钮
        if msg.clickedButton() == go_btn:
            # 用户选择"去三连" - 打开浏览器
            webbrowser.open(self.bilibili_url)
            self.update_status("已打开B站视频，感谢支持！", "info")
    
    
    def generate_ai_image_direct(self):
        """直接从分栏生成AI图片"""
        prompt = self.ai_prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请先输入描述内容")
            return
        
        self.generate_ai_image(prompt)
    
    def generate_ai_image(self, prompt):
        """生成AI图片"""
        # 禁用生成按钮
        self.ai_generate_btn.setEnabled(False)
        self.ai_generate_btn.setText("生成中...")
        self.update_status("正在生成AI图片...", "info")
        
        # 创建并启动AI生图线程
        self.ai_thread = AIGenerateThread(self.ai_generator, prompt)
        self.ai_thread.progress.connect(self.on_ai_progress)
        self.ai_thread.finished.connect(self.on_ai_finished)
        self.ai_thread.start()
    
    def on_ai_progress(self, message):
        """AI生图进度更新"""
        self.update_status(message, "info")
    
    def on_ai_finished(self, success, result):
        """AI生图完成"""
        # 恢复生成按钮
        self.ai_generate_btn.setEnabled(True)
        self.ai_generate_btn.setText("生成简笔画")
        
        if success:
            # 生成成功，直接自动处理
            self.update_status("AI图片生成成功！正在自动处理...", "success")
            
            # 直接自动处理图片并预览
            self.load_image_for_drawing(result)
            
            # 更新历史记录
            self.refresh_ai_history()
            
        else:
            # 生成失败
            self.update_status("AI图片生成失败", "error")
            QMessageBox.critical(self, "生成失败", f"生成失败：\n\n{result}")
    
    def load_image_for_drawing(self, image_path):
        """加载图片用于绘画"""
        try:
            self.image_path = image_path
            self.update_status(f"正在处理AI生成的图片...", "info")
            
            # 自动处理图片并预览
            self.auto_process_and_preview(image_path)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载图片失败：{str(e)}")
    
    def auto_process_and_preview(self, image_path):
        """自动处理图片并在画布上预览"""
        try:
            # 获取当前处理参数
            blur = int(self.blur_slider['slider'].value() * self.blur_slider['step'])
            if blur % 2 == 0:
                blur += 1
            
            params = {
                'blur_kernel': blur,
                'threshold1': int(self.threshold1_slider['slider'].value() * self.threshold1_slider['step']),
                'threshold2': int(self.threshold2_slider['slider'].value() * self.threshold2_slider['step']),
                'min_length': int(self.min_length_slider['slider'].value() * self.min_length_slider['step']),
                'simplify': self.simplify_check.isChecked(),
                'epsilon': self.epsilon_slider['slider'].value() * self.epsilon_slider['step']
            }
            
            # 创建处理线程
            self.processing_thread = ImageProcessThread(image_path, params)
            self.processing_thread.finished.connect(self.on_auto_process_finished)
            self.processing_thread.error.connect(self.on_process_error)
            self.processing_thread.progress.connect(self.update_progress)
            
            # 显示进度
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            
            # 启动处理
            self.processing_thread.start()
            
        except Exception as e:
            self.update_status(f"自动处理失败: {str(e)}", "error")
            QMessageBox.critical(self, "错误", f"自动处理失败：{str(e)}")
    
    def on_auto_process_finished(self, strokes, processor):
        """自动处理完成"""
        try:
            self.strokes = strokes
            self.image_processor = processor
            
            # 隐藏进度条
            self.progress_bar.setVisible(False)
            
            # 获取图片尺寸并更新预览
            if hasattr(processor, 'image') and processor.image is not None:
                img_height, img_width = processor.image.shape[:2]
                self.preview_canvas.img_size = (img_width, img_height)
            else:
                # 默认尺寸
                self.preview_canvas.img_size = (512, 512)
            
            # 更新预览
            self.preview_canvas.update_preview(strokes)
            
            # 更新状态
            self.update_status(f"AI图片处理完成！识别到 {len(strokes)} 条线", "success")
            
            # 不显示弹窗，只更新状态
            pass
            
        except Exception as e:
            self.update_status(f"预览失败: {str(e)}", "error")
            QMessageBox.critical(self, "错误", f"预览失败：{str(e)}")
    
    def refresh_ai_history(self):
        """刷新AI生成历史"""
        try:
            # 检查是否已经初始化
            if not hasattr(self, 'ai_history_layout') or self.ai_history_layout is None:
                print("AI历史记录布局尚未初始化，跳过刷新")
                return
                
            # 清空现有历史
            while self.ai_history_layout.count():
                item = self.ai_history_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 获取历史记录
            history = self.ai_generator.get_history()
            
            if not history:
                # 无历史记录
                no_history = QLabel("暂无生成历史")
                no_history.setAlignment(Qt.AlignCenter)
                no_history.setStyleSheet("color: #999; padding: 20px;")
                self.ai_history_layout.addWidget(no_history)
            else:
                # 显示历史记录（最多显示5条）
                for item in history[:5]:
                    history_item = self.create_history_item(item)
                    self.ai_history_layout.addWidget(history_item)
                    
            print(f"AI历史记录已刷新，显示 {len(history)} 条记录")
            
        except Exception as e:
            print(f"刷新AI历史记录失败: {e}")
            import traceback
            traceback.print_exc()
    
    def create_history_item(self, item):
        """创建历史记录项"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 缩略图
        try:
            pixmap = QPixmap(item['path'])
            if not pixmap.isNull():
                pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                thumb = QLabel()
                thumb.setPixmap(pixmap)
                layout.addWidget(thumb)
        except:
            pass
        
        # 文件名
        name_label = QLabel(item['name'][:20] + "..." if len(item['name']) > 20 else item['name'])
        name_label.setStyleSheet("font-size: 7pt;")
        layout.addWidget(name_label, 1)
        
        # 使用按钮
        use_btn = QPushButton("使用")
        use_btn.setStyleSheet("""
            QPushButton {
                background: #9b59b6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 3px 8px;
                font-size: 7pt;
            }
            QPushButton:hover {
                background: #8e44ad;
            }
        """)
        use_btn.clicked.connect(lambda: self.load_image_for_drawing(item['path']))
        layout.addWidget(use_btn)
        
        widget.setStyleSheet("""
            QWidget {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QWidget:hover {
                background: #e9ecef;
            }
        """)
        
        return widget
    
    
    def keyPressEvent(self, event: QKeyEvent):
        """键盘事件处理"""
        # 小键盘减号键：停止绘画
        if event.key() == Qt.Key_Minus:
            if self.drawing_thread and self.drawing_thread.isRunning():
                self.stop_drawing()
                self.update_status("快捷键：小键盘-键停止绘画", "info")
        
        # 小键盘加号键：开始绘画
        elif event.key() == Qt.Key_Plus:
            if self.strokes and not (self.drawing_thread and self.drawing_thread.isRunning()):
                # 检查是否已经框选区域
                if self.draw_width > 0 and self.draw_height > 0:
                    self.start_drawing()
                    self.update_status("快捷键：小键盘+键开始绘画", "info")
                else:
                    self.update_status("请先框选绘画区域！", "error")
        
        # 调用父类的keyPressEvent
        super().keyPressEvent(event)
    
    def _on_key_press(self, key):
        """全局热键回调"""
        try:
            # 检查是否按下小键盘减号键
            if hasattr(key, 'char') and key.char == '-':
                print("检测到小键盘-键按下")
                self.minus_key_pressed = True
                # 在主线程中停止绘画
                QApplication.instance().postEvent(self, QEvent(QEvent.User))
        except:
            pass
    
    def event(self, event):
        """处理自定义事件"""
        if event.type() == QEvent.User:
            # 处理停止绘画请求
            if self.minus_key_pressed and self.drawing_thread and self.drawing_thread.isRunning():
                print("执行停止绘画")
                self.minus_key_pressed = False
                self.stop_drawing()
            return True
        return super().event(event)
    
    def _start_keyboard_listener(self):
        """启动全局键盘监听"""
        if not KEYBOARD_AVAILABLE:
            return
        
        try:
            if self.keyboard_listener is None:
                self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
                self.keyboard_listener.start()
                print("全局热键监听已启动")
        except Exception as e:
            print(f"启动键盘监听失败: {e}")
    
    def _stop_keyboard_listener(self):
        """停止全局键盘监听"""
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
                print("全局热键监听已停止")
            except:
                pass
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止键盘监听
        if KEYBOARD_AVAILABLE and self.keyboard_listener:
            self._stop_keyboard_listener()
        
        # 销毁tk根窗口
        if self.tk_root:
            try:
                self.tk_root.quit()
                self.tk_root.destroy()
                print("Tkinter根窗口已销毁")
            except Exception as e:
                print(f"销毁tk根窗口失败: {e}")
        
        event.accept()
    
    def apply_stylesheet(self):
        """应用样式表（现代简约主题）"""
        qss = """
        QMainWindow {
            background-color: #f5f6fa;
        }
        QWidget {
            font-family: 'Microsoft YaHei';
            font-size: 9pt;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3498db, stop:1 #2980b9);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 7px 14px;
            font-weight: bold;
            font-size: 9pt;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5dade2, stop:1 #3498db);
        }
        QPushButton:pressed {
            background: #2471a3;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        QLabel {
            color: #2c3e50;
            padding: 2px;
        }
        QSlider::groove:horizontal {
            border: 1px solid #bdc3c7;
            background: #ecf0f1;
            height: 6px;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3498db, stop:1 #2980b9);
            border: 1px solid #2980b9;
            width: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }
        QSlider::handle:horizontal:hover {
            background: #5dade2;
        }
        QProgressBar {
            border: 1px solid #bdc3c7;
            border-radius: 6px;
            text-align: center;
            background-color: #ecf0f1;
            height: 22px;
            color: #2c3e50;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #5dade2, stop:1 #3498db);
            border-radius: 5px;
        }
        QSpinBox {
            padding: 5px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            background-color: white;
            color: #2c3e50;
        }
        QCheckBox {
            spacing: 5px;
            color: #2c3e50;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 2px solid #3498db;
            border-radius: 3px;
            background-color: white;
        }
        QCheckBox::indicator:checked {
            background-color: #3498db;
            image: url(none);
        }
        """
        self.setStyleSheet(qss)


