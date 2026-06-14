"""
截图识别选择器模块 - 用于框选并截取桌面区域进行识别
"""
import tkinter as tk
from typing import Optional
from PIL import ImageGrab
import numpy as np


class ScreenshotSelector:
    """透明全屏窗口截图选择器"""
    
    def __init__(self):
        """初始化截图选择器"""
        self.window = None
        self.canvas = None
        
        # 选择区域坐标
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        
        # 当前矩形对象
        self.rect = None
        
        # 是否已确认
        self.confirmed = False
        
        # 截图结果
        self.screenshot = None
        
    def select_and_capture(self) -> Optional[np.ndarray]:
        """
        显示透明窗口让用户选择区域并截图
        
        Returns:
            numpy.ndarray: 截取的图片（BGR格式），或 None（如果取消）
        """
        # 创建顶层窗口
        self.window = tk.Toplevel()
        self.window.title("截图识别 - 框选区域")
        
        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 设置窗口属性
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.3)  # 半透明
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.window,
            width=screen_width,
            height=screen_height,
            bg='black',
            highlightthickness=0,
            cursor='crosshair'
        )
        self.canvas.pack()
        
        # 添加提示文字
        self.canvas.create_text(
            screen_width // 2,
            50,
            text="拖动鼠标框选要识别的区域\n按 Enter 确认 | 按 ESC 取消",
            fill='white',
            font=('Microsoft YaHei', 14, 'bold'),
            tags='hint'
        )
        
        # 绑定事件
        self.canvas.bind('<Button-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.window.bind('<Return>', self._on_confirm)
        self.window.bind('<Escape>', self._on_cancel)
        
        # 等待用户操作
        self.window.wait_window()
        
        return self.screenshot
    
    def _on_mouse_down(self, event):
        """鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 删除之前的矩形
        if self.rect:
            self.canvas.delete(self.rect)
    
    def _on_mouse_drag(self, event):
        """鼠标拖动事件"""
        if self.start_x is None or self.start_y is None:
            return
        
        # 删除之前的矩形
        if self.rect:
            self.canvas.delete(self.rect)
        
        # 绘制新矩形
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            event.x,
            event.y,
            outline='red',
            width=3,
            dash=(5, 5)
        )
        
        # 保存当前坐标
        self.end_x = event.x
        self.end_y = event.y
        
        # 显示尺寸信息
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        self.canvas.delete('size_text')
        self.canvas.create_text(
            (self.start_x + event.x) / 2,
            min(self.start_y, event.y) - 10,
            text=f"{width} × {height}",
            fill='yellow',
            font=('Arial', 12, 'bold'),
            tags='size_text'
        )
    
    def _on_mouse_up(self, event):
        """鼠标释放事件"""
        self.end_x = event.x
        self.end_y = event.y
    
    def _on_confirm(self, event=None):
        """确认选择"""
        if self.start_x is None or self.end_x is None:
            return
        
        # 计算截图区域（确保坐标正确）
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        # 检查区域是否有效
        if x2 - x1 < 10 or y2 - y1 < 10:
            self.canvas.delete('error_text')
            self.canvas.create_text(
                self.window.winfo_screenwidth() // 2,
                self.window.winfo_screenheight() // 2,
                text="选择区域太小！请重新框选",
                fill='red',
                font=('Microsoft YaHei', 16, 'bold'),
                tags='error_text'
            )
            return
        
        # 隐藏窗口（避免截图到选择框）
        self.window.withdraw()
        self.window.update()
        
        # 短暂延迟确保窗口完全隐藏
        import time
        time.sleep(0.1)
        
        try:
            # 截取指定区域
            screenshot_pil = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            
            # 转换为numpy数组（RGB格式）
            screenshot_rgb = np.array(screenshot_pil)
            
            # 转换为BGR格式（OpenCV使用BGR）
            screenshot_bgr = screenshot_rgb[:, :, ::-1].copy()
            
            self.screenshot = screenshot_bgr
            self.confirmed = True
            
        except Exception as e:
            print(f"截图失败: {e}")
            self.screenshot = None
        
        # 关闭窗口
        self.window.destroy()
    
    def _on_cancel(self, event=None):
        """取消选择"""
        self.screenshot = None
        self.confirmed = False
        self.window.destroy()


def select_and_screenshot() -> Optional[np.ndarray]:
    """
    便捷函数：选择区域并截图
    
    Returns:
        numpy.ndarray: 截取的图片（BGR格式），或 None（如果取消）
    """
    selector = ScreenshotSelector()
    return selector.select_and_capture()
