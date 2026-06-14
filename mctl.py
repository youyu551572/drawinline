"""
鼠标控制模块 - 用于自动绘画
"""
import time
from typing import List, Tuple, Callable
import ctypes
from ctypes import windll

# Windows API 常量
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

# DPI Awareness常量
PROCESS_DPI_UNAWARE = 0
PROCESS_SYSTEM_DPI_AWARE = 1
PROCESS_PER_MONITOR_DPI_AWARE = 2


class MouseController:
    """鼠标控制器，负责自动绘画（使用Win32 API加速）"""
    
    def __init__(self):
        """初始化鼠标控制器"""
        self.offset_x = 0
        self.offset_y = 0
        self.is_drawing = False
        self.pause_flag = False
        
        # 获取屏幕尺寸
        # 注意：DPI感知应在程序启动时（main.py开头）设置，而不是这里
        self.screen_width = windll.user32.GetSystemMetrics(0)
        self.screen_height = windll.user32.GetSystemMetrics(1)
        
    def set_offset(self, x: int, y: int):
        """
        设置绘画区域的偏移量
        
        Args:
            x: X轴偏移
            y: Y轴偏移
        """
        self.offset_x = x
        self.offset_y = y
    
    def move_to(self, x: int, y: int):
        """
        移动鼠标到指定位置（使用Win32 API mouse_event）
        
        Args:
            x: 目标X坐标（相对于图像原点）
            y: 目标Y坐标（相对于图像原点）
        """
        # 应用偏移量（绘画区域的起始位置）
        target_x = int(round(x)) + self.offset_x
        target_y = int(round(y)) + self.offset_y
        
        # 确保坐标为正数
        target_x = max(0, target_x)
        target_y = max(0, target_y)
        
        # 转换为Win32 API的绝对坐标（0-65535范围）
        # 使用浮点数精确计算，避免整数除法精度损失
        abs_x = int(round(target_x * 65535.0 / (self.screen_width - 1)))
        abs_y = int(round(target_y * 65535.0 / (self.screen_height - 1)))
        
        # 边界检查
        abs_x = max(0, min(65535, abs_x))
        abs_y = max(0, min(65535, abs_y))
        
        # 使用Win32 API移动鼠标
        windll.user32.mouse_event(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
            abs_x, abs_y, 0, 0
        )
    
    def mouse_down(self):
        """按下鼠标左键（使用Win32 API）"""
        windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    
    def mouse_up(self):
        """释放鼠标左键（使用Win32 API）"""
        windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    def draw_stroke(self, points: List[Tuple[int, int]], 
                   speed: float = 0.001,
                   pause_callback: Callable = None):
        """
        快速绘制线段（使用Win32 API）
        
        Args:
            points: 点列表 [(x1, y1), (x2, y2), ...]
            speed: 绘画速度（每个点的停留时间，极短）
            pause_callback: 暂停检查回调函数
        """
        if not points or len(points) < 2:
            return True
        
        # 快速移动到起始点
        start_x, start_y = points[0]
        self.move_to(start_x, start_y)
        time.sleep(0.05)  # 短暂准备
        
        # 按下鼠标开始绘制
        self.mouse_down()
        time.sleep(0.02)  # 极短落笔停顿
        
        # 快速绘制线条
        for i in range(1, len(points)):
            # 每隔10个点检查一次暂停（减少检查频率）
            if i % 10 == 0 and pause_callback and pause_callback():
                self.mouse_up()
                return False
            
            curr_point = points[i]
            
            # 快速移动到下一点
            self.move_to(curr_point[0], curr_point[1])
            
            # 极短延迟（仅用于绘画软件捕捉轨迹）
            if speed > 0:
                time.sleep(speed)
        
        # 释放鼠标
        self.mouse_up()
        time.sleep(0.03)  # 极短抬笔停顿
        
        return True
    
    def draw_all(self, strokes: List[List[Tuple[int, int]]], 
                speed: float = 0.005,
                delay_between_strokes: float = 0.1,
                progress_callback: Callable = None,
                pause_callback: Callable = None,
                countdown: int = 3):
        """
        绘制所有线条
        
        Args:
            strokes: 所有笔画的点列表
            speed: 绘画速度
            delay_between_strokes: 笔画之间的延迟
            progress_callback: 进度回调函数 callback(current, total)
            pause_callback: 暂停检查回调函数
            countdown: 开始前倒计时秒数
        """
        # 倒计时
        if countdown > 0:
            print(f"将在 {countdown} 秒后开始绘画...")
            for i in range(countdown, 0, -1):
                if pause_callback and pause_callback():
                    return False
                print(f"{i}...")
                time.sleep(1)
            print("开始绘画！")
        
        self.is_drawing = True
        total_strokes = len(strokes)
        
        try:
            for idx, stroke in enumerate(strokes):
                # 检查暂停
                if pause_callback and pause_callback():
                    print("\n绘画已暂停")
                    break
                
                # 绘制当前笔画
                success = self.draw_stroke(stroke, speed, pause_callback)
                
                if not success:
                    print("\n绘画已中断")
                    break
                
                # 进度回调
                if progress_callback:
                    progress_callback(idx + 1, total_strokes)
                
                # 极短的笔画间延迟
                if idx < total_strokes - 1:
                    time.sleep(delay_between_strokes * 0.5)  # 缩短延迟
            
            print("\n绘画完成！")
            return True
            
        except Exception as e:
            print(f"\n绘画出错: {e}")
            return False
        
        finally:
            self.is_drawing = False
    
    def stop(self):
        """停止绘画"""
        self.is_drawing = False
    
    @staticmethod
    def get_mouse_position() -> Tuple[int, int]:
        """获取当前鼠标位置（使用Win32 API）"""
        from ctypes import wintypes
        point = wintypes.POINT()
        windll.user32.GetCursorPos(ctypes.byref(point))
        return (point.x, point.y)
    
    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """获取屏幕尺寸（使用Win32 API）"""
        width = windll.user32.GetSystemMetrics(0)
        height = windll.user32.GetSystemMetrics(1)
        return (width, height)


def test_mouse_controller():
    """测试鼠标控制功能"""
    controller = MouseController()
    
    print("屏幕尺寸:", controller.get_screen_size())
    print("当前鼠标位置:", controller.get_mouse_position())
    
    # 测试绘制一个简单的正方形
    print("\n3秒后将绘制一个正方形...")
    time.sleep(3)
    
    # 设置偏移量（在屏幕中心附近）
    screen_width, screen_height = controller.get_screen_size()
    controller.set_offset(screen_width // 2 - 50, screen_height // 2 - 50)
    
    # 正方形的四个顶点
    square = [
        (0, 0),
        (100, 0),
        (100, 100),
        (0, 100),
        (0, 0)
    ]
    
    controller.draw_stroke(square, speed=0.01)
    print("测试完成！")


if __name__ == "__main__":
    test_mouse_controller()
