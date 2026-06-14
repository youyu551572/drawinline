"""
图片线条自动绘画工具 - 主程序
"""
import ctypes
import sys

# ⚠️ 关键：必须在导入tkinter之前设置DPI感知
try:
    # Windows 10 1703+ 推荐方案
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except:
    try:
        # 旧版Windows 降级方案
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass  # 如果都失败，继续执行

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os
import webbrowser

from imgprocess import ImageProcessor
from mctl import MouseController
from area_selector import select_drawing_area


class CollapsibleFrame(ttk.Frame):
    """可折叠面板（带流畅动画）"""
    
    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self.is_collapsed = False
        
        # 标题栏（可点击）
        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill=tk.X, pady=(0, 2))
        
        # 箭头指示器
        self.arrow_label = ttk.Label(
            self.title_frame, 
            text="▼",  # 展开状态
            font=("Arial", 8),
            foreground="#666666",
            cursor="hand2"
        )
        self.arrow_label.pack(side=tk.LEFT, padx=(0, 3))
        
        # 标题文字
        self.title_label = ttk.Label(
            self.title_frame,
            text=text,
            font=("Microsoft YaHei", 7, "bold"),
            foreground="#333333",
            cursor="hand2"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # 绑定点击事件
        self.arrow_label.bind("<Button-1>", lambda e: self.toggle())
        self.title_label.bind("<Button-1>", lambda e: self.toggle())
        self.title_frame.bind("<Button-1>", lambda e: self.toggle())
        
        # 内容区域
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def toggle(self):
        """切换展开/折叠状态（带动画）"""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()
    
    def collapse(self):
        """折叠（隐藏内容）"""
        if not self.is_collapsed:
            self.is_collapsed = True
            # 更改箭头方向
            self.arrow_label.config(text="▶")
            # 隐藏内容区域
            self.content_frame.pack_forget()
    
    def expand(self):
        """展开（显示内容）"""
        if self.is_collapsed:
            self.is_collapsed = False
            # 更改箭头方向
            self.arrow_label.config(text="▼")
            # 显示内容区域
            self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def get_content_frame(self):
        """获取内容区域供添加组件"""
        return self.content_frame

# 尝试导入键盘监听库
try:
    from pynput import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("提示：安装 pynput 库可启用空格键暂停功能: pip install pynput")


class DrawingApp:
    """主应用程序GUI"""
    
    def __init__(self, root):
        """初始化应用程序"""
        self.root = root
        self.root.title("🎨 YouYu自动绘画")
        self.root.geometry("900x650")  # 更紧凑可爱
        
        # 数据
        self.image_processor = None
        self.mouse_controller = MouseController()
        self.strokes = []
        self.is_drawing = False
        self.is_paused = False
        
        # 键盘监听
        self.keyboard_listener = None
        self.space_pressed = False
        
        # 参数 - 默认使用复杂模式设置（优化后）
        self.image_path = tk.StringVar()
        self.blur_kernel = tk.IntVar(value=7)  # 增加模糊减少抖动
        self.threshold1 = tk.IntVar(value=50)  # 更敏感的边缘检测
        self.threshold2 = tk.IntVar(value=150)  # 相应调整
        self.min_length = tk.IntVar(value=10)  # 保留更短的线条
        self.simplify = tk.BooleanVar(value=False)  # 默认不简化，保留所有细节
        self.epsilon = tk.DoubleVar(value=1.0)
        self.speed = tk.DoubleVar(value=0.001)  # 使用Win32 API，速度可以更快
        self.countdown = tk.IntVar(value=3)
        
        # 绘画位置和区域
        self.offset_x = tk.IntVar(value=100)
        self.offset_y = tk.IntVar(value=100)
        self.draw_width = tk.IntVar(value=0)
        self.draw_height = tk.IntVar(value=0)
        
        # 获取屏幕分辨率
        self.screen_width = self.mouse_controller.get_screen_size()[0]
        self.screen_height = self.mouse_controller.get_screen_size()[1]
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建所有界面组件"""
        # 配置窗口样式
        self.root.configure(bg='#f0f0f0')
        
        # 左侧控制面板（超紧凑）
        left_frame = ttk.Frame(self.root, padding="3")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 系统信息显示（可折叠）
        info_section = CollapsibleFrame(left_frame, text="📊 系统")
        info_section.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 2))
        info_content = info_section.get_content_frame()
        screen_info = f"🖥️ {self.screen_width}×{self.screen_height}"
        ttk.Label(info_content, text=screen_info, foreground="#0066cc", font=("Microsoft YaHei", 7)).pack(anchor=tk.W, padx=3, pady=2)
        
        # 文件选择组（可折叠）
        file_section = CollapsibleFrame(left_frame, text="📁 图片")
        file_section.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 2))
        file_content = file_section.get_content_frame()
        ttk.Entry(file_content, textvariable=self.image_path, width=28, font=("Arial", 7)).pack(fill=tk.X, padx=3, pady=(0, 2))
        ttk.Button(file_content, text="📂 选择", command=self.select_image).pack(fill=tk.X, padx=3)
        
        # 图像处理参数组（可折叠）
        param_section = CollapsibleFrame(left_frame, text="🎨 处理参数")
        param_section.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 2))
        param_content = param_section.get_content_frame()
        
        # 参数滑块（更紧凑的布局）
        self._create_param_slider(param_content, "模糊核:", self.blur_kernel, 1, 15)
        self._create_param_slider(param_content, "阈值1:", self.threshold1, 10, 200)
        self._create_param_slider(param_content, "阈值2:", self.threshold2, 50, 300)
        self._create_param_slider(param_content, "最小长度:", self.min_length, 10, 200)
        
        # 简化选项（紧凑）
        simplify_frame = ttk.Frame(param_content)
        simplify_frame.pack(fill=tk.X, pady=1, padx=3)
        ttk.Checkbutton(simplify_frame, text="简化线条", variable=self.simplify).pack(side=tk.LEFT)
        
        self._create_param_slider(param_content, "简化程度:", self.epsilon, 0.5, 10)
        
        # 处理按钮
        ttk.Button(param_content, text="⚡ 处理", command=self.process_image).pack(fill=tk.X, padx=3, pady=(3, 0))
        
        # 绘画参数组（可折叠）
        draw_section = CollapsibleFrame(left_frame, text="🗌️ 绘画")
        draw_section.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 2))
        draw_content = draw_section.get_content_frame()
        
        # 绘画区域信息（超紧凑）
        area_inner = ttk.Frame(draw_content)
        area_inner.pack(fill=tk.X, padx=3, pady=(0, 2))
        
        pos_frame = ttk.Frame(area_inner)
        pos_frame.pack(fill=tk.X, pady=0)
        ttk.Label(pos_frame, text="位:", width=3, font=("Arial", 7)).pack(side=tk.LEFT)
        ttk.Label(pos_frame, text="X", font=("Arial", 7)).pack(side=tk.LEFT, padx=(2,0))
        ttk.Entry(pos_frame, textvariable=self.offset_x, width=5, font=("Arial", 7)).pack(side=tk.LEFT, padx=1)
        ttk.Label(pos_frame, text="Y", font=("Arial", 7)).pack(side=tk.LEFT, padx=(5,0))
        ttk.Entry(pos_frame, textvariable=self.offset_y, width=5, font=("Arial", 7)).pack(side=tk.LEFT, padx=1)
        
        size_frame = ttk.Frame(area_inner)
        size_frame.pack(fill=tk.X, pady=0)
        ttk.Label(size_frame, text="寸:", width=3, font=("Arial", 7)).pack(side=tk.LEFT)
        ttk.Label(size_frame, text="宽", font=("Arial", 7)).pack(side=tk.LEFT, padx=(2,0))
        ttk.Entry(size_frame, textvariable=self.draw_width, width=5, state='readonly', font=("Arial", 7)).pack(side=tk.LEFT, padx=1)
        ttk.Label(size_frame, text="高", font=("Arial", 7)).pack(side=tk.LEFT, padx=(5,0))
        ttk.Entry(size_frame, textvariable=self.draw_height, width=5, state='readonly', font=("Arial", 7)).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(draw_content, text="📍 框选区域", command=self.select_position).pack(fill=tk.X, padx=3, pady=(2, 3))
        
        # 绘画速度和倒计时（紧凑）
        self._create_param_slider(draw_content, "速度:", self.speed, 0.001, 0.02)
        
        countdown_frame = ttk.Frame(draw_content)
        countdown_frame.pack(fill=tk.X, padx=3, pady=1)
        ttk.Label(countdown_frame, text="倒计时:", width=8, font=("Arial", 7)).pack(side=tk.LEFT)
        ttk.Entry(countdown_frame, textvariable=self.countdown, width=5, font=("Arial", 7)).pack(side=tk.LEFT, padx=3)
        ttk.Label(countdown_frame, text="秒", font=("Arial", 7)).pack(side=tk.LEFT)
        
        # 绘画控制按钮（紧凑）
        button_inner = ttk.Frame(draw_content)
        button_inner.pack(fill=tk.X, padx=3, pady=(3, 0))
        
        self.start_button = ttk.Button(button_inner, text="▶️ 开始", command=self.start_drawing, state=tk.DISABLED, width=8)
        self.start_button.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        
        self.pause_button = ttk.Button(button_inner, text="⏸️ 暂停", command=self.pause_drawing, state=tk.DISABLED, width=6)
        self.pause_button.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        
        self.stop_button = ttk.Button(button_inner, text="⏹️ 停止", command=self.stop_drawing, state=tk.DISABLED, width=6)
        self.stop_button.pack(side=tk.LEFT, padx=1, fill=tk.X, expand=True)
        
        # 进度条（超紧凑）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(left_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=20, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=4)
        
        self.status_label = ttk.Label(left_frame, text="就绪", foreground="green", font=("Microsoft YaHei", 7))
        self.status_label.grid(row=21, column=0, columnspan=3, pady=1)
        
        # 作者信息和支持区域（可折叠）
        author_section = CollapsibleFrame(left_frame, text="💖 作者:YouYu")
        author_section.grid(row=22, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(4, 0))
        author_content = author_section.get_content_frame()
        
        # 一键三连按钮（超紧凑）
        support_button = ttk.Button(
            author_content,
            text="🎬 B站三连",
            command=self.open_bilibili
        )
        support_button.pack(fill=tk.X, padx=3, pady=1)
        
        # 超简洁提示
        tip_label = ttk.Label(
            author_content,
            text="点赞❤️投币💎收藏⭐",
            font=("Microsoft YaHei", 7),
            foreground="#ff6b9d",
            justify=tk.CENTER
        )
        tip_label.pack(padx=3, pady=1)
        
        # 右侧预览区域（超紧凑）
        right_frame = ttk.Frame(self.root, padding="3")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(right_frame, text="📻 预览", font=("Microsoft YaHei", 8, "bold")).pack(anchor=tk.W, pady=(0, 3))
        
        # 画布用于显示预览（超紧凑尺寸）
        self.canvas = tk.Canvas(right_frame, width=560, height=560, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(pady=3)
        
        # 信息标签（紧凑）
        self.info_label = ttk.Label(right_frame, text="", justify=tk.LEFT, font=("Microsoft YaHei", 7))
        self.info_label.pack(anchor=tk.W, pady=5)
        
        # 配置网格权重
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def _create_param_slider(self, parent, label, variable, from_, to):
        """创建参数滑块的辅助方法（超紧凑）"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=3, pady=1)
        
        ttk.Label(frame, text=label, width=7, font=("Arial", 7)).pack(side=tk.LEFT)
        ttk.Scale(frame, from_=from_, to=to, variable=variable, orient=tk.HORIZONTAL, length=120).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        ttk.Label(frame, textvariable=variable, width=4, font=("Arial", 7)).pack(side=tk.LEFT)
    
    def open_bilibili(self):
        """打开B站视频进行一键三连"""
        bilibili_url = "https://www.bilibili.com/video/BV1ibz3YcEMX/?vd_source=aa808187ad407782ee737fe6a139b954"
        try:
            webbrowser.open(bilibili_url)
            self.update_status("已打开B站视频，感谢您的支持！❤️", "green")
        except Exception as e:
            messagebox.showinfo("提示", f"无法自动打开浏览器，请手动访问：\n{bilibili_url}")
    
    def select_image(self):
        """选择图片文件"""
        filename = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.image_path.set(filename)
            self.update_status("已选择图片，请点击'处理图片'", "blue")
    
    def process_image(self):
        """处理图片（优化版：后台线程+进度提示）"""
        image_file = self.image_path.get()
        
        if not image_file or not os.path.exists(image_file):
            messagebox.showerror("错误", "请先选择有效的图片文件")
            return
        
        # 在后台线程中处理，避免UI卡顿
        def process_thread():
            try:
                self.update_status("⏳ 正在加载图片...", "orange")
                self.progress_var.set(10)
                
                # 创建图像处理器
                self.image_processor = ImageProcessor(image_file)
                
                # 检查图片尺寸，大图片给出提示
                img_size = self.image_processor.get_image_size()
                if img_size[0] > 2000 or img_size[1] > 2000:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "提示", 
                        f"图片较大 ({img_size[0]}×{img_size[1]})\n处理需要10-30秒，请耐心等待"
                    ))
                
                self.update_status("🔍 正在检测边缘...", "orange")
                self.progress_var.set(30)
                
                # 预处理
                blur = self.blur_kernel.get()
                if blur % 2 == 0:
                    blur += 1
                
                self.image_processor.preprocess(
                    blur_kernel=blur,
                    threshold1=self.threshold1.get(),
                    threshold2=self.threshold2.get()
                )
                
                self.update_status("📐 正在提取线条...", "orange")
                self.progress_var.set(60)
                
                # 提取轮廓
                self.image_processor.extract_contours(min_length=self.min_length.get())
                
                self.update_status("✂️ 正在优化线条...", "orange")
                self.progress_var.set(80)
                
                # 获取绘画点
                self.strokes = self.image_processor.get_drawing_points(
                    simplify=self.simplify.get(),
                    epsilon=self.epsilon.get()
                )
                
                self.progress_var.set(90)
                
                # 在主线程中显示预览
                self.root.after(0, self.show_preview)
                
                # 更新信息
                total_points = sum(len(stroke) for stroke in self.strokes)
                info_text = f"✅ 检测到 {len(self.strokes)} 条线条\n"
                info_text += f"📍 共 {total_points} 个绘画点\n"
                info_text += f"📐 图片: {img_size[0]}×{img_size[1]}"
                self.root.after(0, lambda: self.info_label.config(text=info_text))
                
                # 启用开始按钮
                self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                self.progress_var.set(100)
                self.update_status("✅ 处理完成，可以开始绘画", "green")
                
                # 清理内存
                import gc
                gc.collect()
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"处理图片时出错：{str(e)}"))
                self.update_status("❌ 处理失败", "red")
                self.progress_var.set(0)
        
        # 启动后台线程
        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()
    
    def show_preview(self):
        """显示预览图片"""
        if not self.image_processor or not self.strokes:
            return
        
        # 获取原图尺寸
        img_width, img_height = self.image_processor.get_image_size()
        
        # 计算缩放比例以适应画布（超紧凑尺寸）
        canvas_width = 560
        canvas_height = 560
        scale = min(canvas_width / img_width, canvas_height / img_height)
        
        # 清空画布
        self.canvas.delete("all")
        
        # 性能优化：限制显示的线条数和点数
        total_strokes = len(self.strokes)
        max_display_strokes = 1000  # 最多显示1000条线条
        stroke_step = max(1, total_strokes // max_display_strokes) if total_strokes > max_display_strokes else 1
        
        # 绘制线条（性能优化版本）
        for idx, stroke in enumerate(self.strokes):
            # 采样显示，避免卡顿
            if idx % stroke_step != 0 and total_strokes > max_display_strokes:
                continue
                
            if len(stroke) < 2:
                continue
            
            # 缩放坐标（使用round，与实际绘画完全一致）
            scaled_points = [(int(round(x * scale)), int(round(y * scale))) for x, y in stroke]
            
            # 性能优化：对超长线条进行点采样
            if len(scaled_points) > 100:
                # 每隔几个点取一个，保持形状但减少绘制量
                step = max(2, len(scaled_points) // 50)
                scaled_points = scaled_points[::step]
            
            # 一次性绘制整条线（而不是逐段绘制）
            if len(scaled_points) >= 2:
                # 将点列表展平为坐标序列
                coords = []
                for x, y in scaled_points:
                    coords.extend([x, y])
                
                # 一次调用绘制整条线
                self.canvas.create_line(*coords, fill="#0066CC", width=1, smooth=False)
    
    def select_position(self):
        """选择绘画位置 - 使用透明窗口框选"""
        self.update_status("正在打开区域选择器...", "blue")
        
        try:
            # 最小化主窗口，避免干扰
            self.root.iconify()
            
            # 准备线条数据和图片尺寸用于预览
            strokes = None
            image_size = None
            
            if self.strokes and self.image_processor:
                strokes = self.strokes
                image_size = self.image_processor.get_image_size()
            
            # 使用区域选择器（带预览）
            result = select_drawing_area(strokes=strokes, image_size=image_size)
            
            # 恢复主窗口显示
            self.root.deiconify()
            
            if result:
                x, y, width, height = result
                self.offset_x.set(x)
                self.offset_y.set(y)
                self.draw_width.set(width)
                self.draw_height.set(height)
                
                status_msg = f"已选择区域: 位置({x}, {y}), 尺寸({width} × {height})"
                if strokes:
                    status_msg += f" [已预览{len(strokes)}条线条]"
                
                self.update_status(status_msg, "green")
            else:
                self.update_status("已取消选择", "orange")
                
        except Exception as e:
            # 确保窗口恢复
            self.root.deiconify()
            messagebox.showerror("错误", f"选择区域时出错：{str(e)}")
            self.update_status("选择失败", "red")
    
    def start_drawing(self):
        """开始绘画"""
        if not self.strokes:
            messagebox.showwarning("警告", "请先处理图片")
            return
        
        if self.is_drawing:
            messagebox.showinfo("提示", "正在绘画中...")
            return
        
        # 确认开始
        result = messagebox.askyesno(
            "确认",
            f"将在位置 ({self.offset_x.get()}, {self.offset_y.get()}) 开始绘画\n"
            f"共 {len(self.strokes)} 条线条\n"
            f"{self.countdown.get()} 秒后开始\n\n"
            "请确保目标绘画程序已打开并处于可绘画状态\n"
            "提示：将鼠标移到左上角可紧急停止\n\n"
            "确定要开始吗？"
        )
        
        if not result:
            return
        
        # 最小化窗口
        self.root.iconify()
        
        # 启动绘画线程
        self.is_drawing = True
        self.is_paused = False
        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.drawing_thread)
        thread.daemon = True
        thread.start()
    
    def drawing_thread(self):
        """绘画线程"""
        try:
            # 启动键盘监听（如果可用）
            if KEYBOARD_AVAILABLE:
                self._start_keyboard_listener()
                self.root.after(0, lambda: self.update_status(
                    "绘画中... (空格键暂停/继续)", "orange"
                ))
            
            # 设置偏移量
            self.mouse_controller.set_offset(self.offset_x.get(), self.offset_y.get())
            
            # 缩放线条到目标区域（如果设置了目标尺寸）
            strokes_to_draw = self.strokes
            if self.draw_width.get() > 0 and self.draw_height.get() > 0 and self.image_processor:
                # 获取原图尺寸
                img_width, img_height = self.image_processor.get_image_size()
                
                # 计算缩放比例（与预览保持一致）
                scale_x = self.draw_width.get() / img_width
                scale_y = self.draw_height.get() / img_height
                
                # 缩放所有线条（使用round确保精度，与预览一致）
                strokes_to_draw = []
                for stroke in self.strokes:
                    # 使用round而不是int，避免截断误差
                    scaled_stroke = [(int(round(x * scale_x)), int(round(y * scale_y))) for x, y in stroke]
                    strokes_to_draw.append(scaled_stroke)
            
            # 进度回调
            def progress_callback(current, total):
                progress = (current / total) * 100
                self.progress_var.set(progress)
                
                # 显示状态（包括空格键提示）
                status_text = f"正在绘画: {current}/{total} ({progress:.1f}%)"
                if KEYBOARD_AVAILABLE:
                    if self.is_paused:
                        status_text += " [已暂停 - 按空格继续]"
                    else:
                        status_text += " [空格键暂停]"
                
                self.root.after(0, lambda: self.update_status(status_text, "orange"))
            
            # 暂停检查
            def pause_callback():
                # 检查空格键状态并自动切换暂停
                if KEYBOARD_AVAILABLE and self.space_pressed:
                    self.space_pressed = False  # 重置标志
                    self.is_paused = not self.is_paused
                    
                    # 更新GUI
                    if self.is_paused:
                        self.root.after(0, lambda: self.pause_button.config(text="继续"))
                    else:
                        self.root.after(0, lambda: self.pause_button.config(text="暂停"))
                
                return self.is_paused or not self.is_drawing
            
            # 开始绘画（使用缩放后的线条）
            self.mouse_controller.draw_all(
                strokes_to_draw,
                speed=self.speed.get(),
                progress_callback=progress_callback,
                pause_callback=pause_callback,
                countdown=self.countdown.get()
            )
            
            # 停止键盘监听
            if KEYBOARD_AVAILABLE and self.keyboard_listener:
                self._stop_keyboard_listener()
            
            # 完成
            self.root.after(0, lambda: self.drawing_complete())
            
        except Exception as e:
            # 停止键盘监听
            if KEYBOARD_AVAILABLE and self.keyboard_listener:
                self._stop_keyboard_listener()
            
            self.root.after(0, lambda: messagebox.showerror("错误", f"绘画出错：{str(e)}"))
            self.root.after(0, lambda: self.drawing_complete())
    
    def pause_drawing(self):
        """暂停/继续绘画"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="继续")
            self.update_status("已暂停", "orange")
        else:
            self.pause_button.config(text="暂停")
            self.update_status("继续绘画...", "orange")
    
    def stop_drawing(self):
        """停止绘画"""
        self.is_drawing = False
        self.is_paused = False
        self.mouse_controller.stop()
        self.drawing_complete()
    
    def drawing_complete(self):
        """绘画完成"""
        self.is_drawing = False
        self.is_paused = False
        
        # 停止键盘监听
        if KEYBOARD_AVAILABLE and self.keyboard_listener:
            self._stop_keyboard_listener()
        
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="暂停")
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("绘画完成", "green")
        
        # 恢复窗口
        self.root.deiconify()
    
    def _on_key_press(self, key):
        """键盘按键回调"""
        try:
            if key == keyboard.Key.space:
                self.space_pressed = True
        except:
            pass
    
    def _start_keyboard_listener(self):
        """启动键盘监听"""
        if not KEYBOARD_AVAILABLE:
            return
        
        try:
            self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
            self.keyboard_listener.start()
        except Exception as e:
            print(f"启动键盘监听失败: {e}")
    
    def _stop_keyboard_listener(self):
        """停止键盘监听"""
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            except:
                pass
    
    def update_status(self, message, color="black"):
        """更新状态标签"""
        self.status_label.config(text=message, foreground=color)


def main():
    """主函数"""
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
