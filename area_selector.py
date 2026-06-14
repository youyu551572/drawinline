"""
区域选择器模块 - 用于在透明窗口中框选绘画区域
"""
import tkinter as tk
from typing import Tuple, Optional
import time


class AreaSelector:
    """透明全屏窗口区域选择器"""
    
    def __init__(self):
        """初始化区域选择器"""
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
        
        # 选择结果
        self.selected_area = None
        
        # 保存当前框选的坐标（修复确认时坐标不一致问题）
        self.current_x1 = None
        self.current_y1 = None
        self.current_width = None
        self.current_height = None
        
    def select_area(self) -> Optional[Tuple[int, int, int, int]]:
        """
        显示透明窗口让用户选择区域
        
        Returns:
            (x, y, width, height) 或 None（如果取消）
        """
        # 创建顶层窗口
        self.window = tk.Toplevel()
        self.window.title("选择绘画区域")
        
        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 设置窗口为全屏
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        
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
            cursor='cross'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 添加提示文字
        self.canvas.create_text(
            screen_width // 2,
            30,
            text="拖动鼠标选择绘画区域，按 Enter 确认，按 Esc 取消",
            fill='white',
            font=('Arial', 16, 'bold'),
            tags='hint'
        )
        
        # 绑定鼠标事件
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # 绑定键盘事件
        self.window.bind('<Return>', self.on_confirm)
        self.window.bind('<Escape>', self.on_cancel)
        
        # 设置焦点
        self.window.focus_force()
        
        # 等待窗口关闭
        self.window.wait_window()
        
        return self.selected_area
    
    def on_mouse_down(self, event):
        """鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 删除旧矩形
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
    
    def on_mouse_drag(self, event):
        """鼠标拖动事件"""
        if self.start_x is None or self.start_y is None:
            return
        
        # 删除旧矩形
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
            tags='selection'
        )
        
        # 更新坐标显示
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)
        
        # 删除旧的坐标文字
        self.canvas.delete('coords')
        
        # 显示当前选择的坐标和尺寸
        text = f"起点: ({self.start_x}, {self.start_y})  当前: ({event.x}, {event.y})  尺寸: {width} x {height}"
        self.canvas.create_text(
            self.canvas.winfo_width() // 2,
            60,
            text=text,
            fill='yellow',
            font=('Arial', 12),
            tags='coords'
        )
        
        self.end_x = event.x
        self.end_y = event.y
    
    def on_mouse_up(self, event):
        """鼠标释放事件"""
        self.end_x = event.x
        self.end_y = event.y
    
    def on_confirm(self, event=None):
        """确认选择"""
        if self.start_x is None or self.end_x is None:
            return
        
        # 计算实际区域（确保左上角为起点）
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        width = x2 - x1
        height = y2 - y1
        
        # 确保有效区域
        if width > 10 and height > 10:
            self.selected_area = (x1, y1, width, height)
            self.confirmed = True
            self.window.destroy()
        else:
            # 区域太小，显示提示
            self.canvas.delete('error')
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                90,
                text="选择区域太小，请重新选择",
                fill='red',
                font=('Arial', 14, 'bold'),
                tags='error'
            )
    
    def on_cancel(self, event=None):
        """取消选择"""
        self.selected_area = None
        self.window.destroy()


class AreaSelectorV2:
    """改进版区域选择器 - 更清晰的视觉效果"""
    
    def __init__(self, strokes=None, image_size=None):
        """
        初始化区域选择器
        
        Args:
            strokes: 线条数据 List[List[Tuple[int, int]]]
            image_size: 原始图片尺寸 (width, height)
        """
        self.window = None
        self.canvas = None
        self.selected_area = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        
        # 性能优化：防抖动绘制
        self.draw_timer = None
        self.pending_draw = None
        self.overlay_rects = []
        
        # 线条预览数据
        self.strokes = strokes or []
        self.image_size = image_size or (800, 600)
        self.preview_lines = []
        
        # 保存当前框选的坐标（修复确认时坐标不一致问题）
        self.current_x1 = None
        self.current_y1 = None
        self.current_width = None
        self.current_height = None
        
        # 性能优化：节流控制
        self.last_preview_time = 0
        self.preview_interval = 0.1  # 100ms更新一次预览（减少卡顿）
        
        # 红色十字光标
        self.cursor_lines = []
        self.last_mouse_pos = (0, 0)
        
    def select_area(self) -> Optional[Tuple[int, int, int, int]]:
        """
        显示选择窗口
        
        Returns:
            (x, y, width, height) 或 None
        """
        # 创建窗口
        self.window = tk.Toplevel()
        self.window.title("选择绘画区域")
        
        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 全屏设置
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-topmost', True)
        
        # 持续保持最上层显示
        def keep_on_top():
            try:
                if self.window and self.window.winfo_exists():
                    self.window.attributes('-topmost', True)
                    self.window.after(100, keep_on_top)
            except:
                pass
        keep_on_top()
        
        # 创建画布（半透明黑色背景）
        self.canvas = tk.Canvas(
            self.window,
            width=screen_width,
            height=screen_height,
            bg='black',
            highlightthickness=0,
            cursor='crosshair'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 设置透明度
        self.window.attributes('-alpha', 0.5)
        
        # 提示信息
        hint_bg = self.canvas.create_rectangle(
            0, 0, screen_width, 100,
            fill='black',
            outline='',
            tags='hint_bg'
        )
        
        self.canvas.create_text(
            screen_width // 2, 25,
            text="📍 拖动鼠标框选绘画区域",
            fill='white',
            font=('Microsoft YaHei', 18, 'bold'),
            tags='hint'
        )
        
        self.canvas.create_text(
            screen_width // 2, 55,
            text="按 Enter 确认 | 按 Esc 取消",
            fill='#00FF00',
            font=('Microsoft YaHei', 14),
            tags='hint'
        )
        
        # 绑定事件
        self.canvas.bind('<Motion>', self.on_mouse_move)  # 鼠标移动（绘制红色十字）
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.window.bind('<Return>', self.on_confirm)
        self.window.bind('<Escape>', self.on_cancel)
        self.window.bind('<KP_Enter>', self.on_confirm)  # 小键盘Enter
        
        self.window.focus_force()
        self.window.wait_window()
        
        return self.selected_area
    
    def on_mouse_move(self, event):
        """鼠标移动 - 绘制红色十字光标"""
        # 清除旧的十字光标
        self.canvas.delete('cursor')
        
        # 获取屏幕尺寸
        screen_width = self.canvas.winfo_width()
        screen_height = self.canvas.winfo_height()
        
        # 绘制红色十字光标（横线和竖线）
        cursor_size = 20  # 十字大小
        
        # 横线
        self.canvas.create_line(
            event.x - cursor_size, event.y,
            event.x + cursor_size, event.y,
            fill='red',
            width=2,
            tags='cursor'
        )
        
        # 竖线
        self.canvas.create_line(
            event.x, event.y - cursor_size,
            event.x, event.y + cursor_size,
            fill='red',
            width=2,
            tags='cursor'
        )
        
        # 中心圆点
        self.canvas.create_oval(
            event.x - 3, event.y - 3,
            event.x + 3, event.y + 3,
            fill='red',
            outline='white',
            width=1,
            tags='cursor'
        )
    
    def on_mouse_down(self, event):
        """鼠标按下"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 清除旧的选择
        self.canvas.delete('selection')
        self.canvas.delete('info')
        for rect in self.overlay_rects:
            self.canvas.delete(rect)
        self.overlay_rects = []

    def on_mouse_drag(self, event):
        """鼠标拖动"""
        if self.start_x is None:
            return

        # 计算区域
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        width = x2 - x1
        height = y2 - y1
        
        # 保存当前框选的坐标
        self.current_x1 = x1
        self.current_y1 = y1
        self.current_width = width
        self.current_height = height

        # 节流控制：只在特定时间间隔更新预览
        current_time = time.time()
        should_update_preview = (current_time - self.last_preview_time) >= self.preview_interval
        
        # 清除旧图形
        self.canvas.delete('selection')
        self.canvas.delete('info')
        if should_update_preview:
            self.canvas.delete('preview')
        
        # 绘制预览线条（节流控制）
        if should_update_preview and self.strokes and width > 50 and height > 50:
            self._draw_preview_strokes(x1, y1, width, height)
            self.last_preview_time = current_time
        
        # 绘制红色矩形框
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='red',
            width=3,
            tags='selection'
        )
        
        # 绘制填充（更透明）
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill='red',
            stipple='gray25',
            outline='',
            tags='selection'
        )
        
        # 显示信息
        info_text = f"位置: ({x1}, {y1})  尺寸: {width} × {height} 像素"
        if self.strokes:
            info_text += f"  线条: {len(self.strokes)}条"
        
        # 信息背景
        self.canvas.create_rectangle(
            10, 110, 500, 150,
            fill='black',
            outline='yellow',
            width=2,
            tags='info'
        )
        
        self.canvas.create_text(
            20, 130,
            text=info_text,
            fill='yellow',
            font=('Consolas', 12, 'bold'),
            anchor='w',
            tags='info'
        )
        
        # 性能优化：使用防抖动绘制预览
        if self.strokes and self.image_size:
            # 取消之前的定时器
            if self.draw_timer:
                self.window.after_cancel(self.draw_timer)
            
            # 保存当前绘制参数
            self.pending_draw = (x1, y1, width, height)
            
            # 30ms后执行绘制（防抖动）
            self.draw_timer = self.window.after(30, self._execute_draw)
    
    def _execute_draw(self):
        """执行延迟的绘制（防抖动）"""
        if self.pending_draw:
            x1, y1, width, height = self.pending_draw
            self._draw_preview_strokes(x1, y1, width, height)
            self.pending_draw = None
        self.draw_timer = None
    
    def _draw_preview_strokes(self, x1, y1, width, height):
        """
        在选择区域内绘制预览线条（性能优化版本）
        
        Args:
            x1, y1: 区域左上角坐标
            width, height: 区域尺寸
        """
        if not self.strokes or not self.image_size:
            return
        
        img_width, img_height = self.image_size
        
        # 计算缩放比例
        scale_x = width / img_width
        scale_y = height / img_height
        
        # 性能优化：智能简化线条
        # 根据区域大小动态调整显示精度
        area_size = width * height
        screen_area = self.window.winfo_screenwidth() * self.window.winfo_screenheight()
        
        # 如果框选区域很小，可以简化显示
        if area_size < screen_area * 0.05:  # 小于屏幕5%
            # 采样显示（快速模式）
            stroke_step = max(1, len(self.strokes) // 200)  # 最多200条线
            point_step = 3  # 每3个点显示一次
        elif area_size < screen_area * 0.2:  # 小于屏幕20%
            # 中等质量
            stroke_step = max(1, len(self.strokes) // 500)  # 最多500条线
            point_step = 2  # 每2个点显示一次
        else:
            # 高质量（大区域时显示所有）
            stroke_step = 1
            point_step = 1
        
        # 性能优化：一次性绘制每条stroke
        for idx, stroke in enumerate(self.strokes):
            # 根据步长决定是否跳过
            if idx % stroke_step != 0:
                continue
                
            if len(stroke) < 2:
                continue
            
            # 收集stroke的所有点（根据point_step采样）
            stroke_coords = []
            for i in range(0, len(stroke), point_step):
                if i >= len(stroke):
                    break
                    
                x_point, y_point = stroke[i]
                
                # 缩放到当前框选区域（使用int(round())与实际绘画完全一致）
                new_x = x1 + int(round(x_point * scale_x))
                new_y = y1 + int(round(y_point * scale_y))
                stroke_coords.extend([new_x, new_y])
            
            # 一次性绘制整条线
            if len(stroke_coords) >= 4:
                self.canvas.create_line(
                    *stroke_coords,
                    fill='#00FF00',
                    width=1,
                    smooth=False,
                    tags='preview'
                )
    
    def on_mouse_up(self, event):
        """鼠标释放"""
        pass
    
    def on_confirm(self, event=None):
        """确认选择"""
        # 使用保存的框选坐标，而不是重新计算鼠标位置
        # 这样可以避免用户在确认时鼠标移动导致的坐标偏差
        if self.current_x1 is not None and self.current_width is not None:
            if self.current_width > 10 and self.current_height > 10:
                self.selected_area = (
                    self.current_x1, 
                    self.current_y1, 
                    self.current_width, 
                    self.current_height
                )
                print(f"确认框选区域: 位置({self.current_x1}, {self.current_y1}), 尺寸({self.current_width} × {self.current_height})")
                self.window.destroy()
        elif self.start_x is not None:
            # 如果没有拖动过，使用旧逻辑
            x = self.window.winfo_pointerx() - self.window.winfo_rootx()
            y = self.window.winfo_pointery() - self.window.winfo_rooty()
            
            x1 = min(self.start_x, x)
            y1 = min(self.start_y, y)
            x2 = max(self.start_x, x)
            y2 = max(self.start_y, y)
            
            width = x2 - x1
            height = y2 - y1
            
            if width > 10 and height > 10:
                self.selected_area = (x1, y1, width, height)
                self.window.destroy()
    
    def on_cancel(self, event=None):
        """取消"""
        self.selected_area = None
        self.window.destroy()


# 默认使用改进版
def select_drawing_area(strokes=None, image_size=None) -> Optional[Tuple[int, int, int, int]]:
    """
    显示区域选择器，让用户框选绘画区域
    
    Args:
        strokes: 线条数据 List[List[Tuple[int, int]]]，用于实时预览
        image_size: 原始图片尺寸 (width, height)
    
    Returns:
        (x, y, width, height) 或 None（取消）
    """
    selector = AreaSelectorV2(strokes=strokes, image_size=image_size)
    return selector.select_area()


if __name__ == "__main__":
    # 测试
    root = tk.Tk()
    root.withdraw()
    
    result = select_drawing_area()
    
    if result:
        x, y, width, height = result
        print(f"选择的区域: 位置({x}, {y}), 尺寸({width} x {height})")
    else:
        print("取消选择")
    
    root.destroy()
