"""
图像处理模块 - 用于识别图片中的线条
"""
import cv2
import numpy as np
from typing import List, Tuple


class ImageProcessor:
    """图像处理类，负责提取图片中的线条"""
    
    def __init__(self, image_path: str = None):
        """
        初始化图像处理器
        
        Args:
            image_path: 图片路径（可选，用于从文件加载）
        """
        self.original_image = None
        
        # 如果提供了图片路径，则加载图片
        if image_path:
            # 使用支持中文路径的方式读取图片
            try:
                # 使用numpy读取文件，然后用imdecode解码
                # 这种方式支持中文路径
                img_data = np.fromfile(image_path, dtype=np.uint8)
                self.original_image = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
                
                if self.original_image is None:
                    raise ValueError(f"无法解码图片: {image_path}")
            except Exception as e:
                raise ValueError(f"无法读取图片: {image_path}\n错误: {str(e)}")
        
        self.processed_image = None
        self.contours = []
        self.drawing_points = []
        
    def _morphological_skeleton(self, image: np.ndarray) -> np.ndarray:
        """形态学骨架化"""
        size = np.size(image)
        skel = np.zeros_like(image, dtype=np.uint8)
        
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        
        while True:
            eroded = cv2.erode(image, element)
            temp = cv2.dilate(eroded, element)
            temp = cv2.subtract(image, temp)
            skel = cv2.bitwise_or(skel, temp)
            image = eroded.copy()
            
            zeros = size - cv2.countNonZero(image)
            if zeros == size:
                break
        
        return skel
    
    def preprocess(self, blur_kernel: int = 5, threshold1: int = 50, threshold2: int = 150, 
                   use_skeleton: bool = False, skeleton_method: str = 'gentle', 
):
        """
        预处理图像，提取边缘（增强自适应+CLAHE）
        
        Args:
            blur_kernel: 高斯模糊核大小
            threshold1: Canny边缘检测低阈值（基准值）
            threshold2: Canny边缘检测高阈值（基准值）
            use_skeleton: 是否使用骨架化消除双线条（默认False，保留细节）
            skeleton_method: 骨架化方法 'gentle'（温和）或 'strong'（强力）
        """
        if self.original_image is None:
            raise ValueError("请先加载图像")
        
        # 转换为灰度图
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        
        # 使用CLAHE增强对比度（对低对比度图片特别有效）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 高斯模糊减少噪声
        blurred = cv2.GaussianBlur(enhanced, (blur_kernel, blur_kernel), 0)
        
        # 多策略自适应阈值
        # 策略1：基于中值
        median = np.median(blurred)
        method1_low = max(0, int(median * 0.5))
        method1_high = min(255, int(median * 1.0))
        
        # 策略2：基于Otsu
        otsu_val, _ = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # 确保otsu_val是标量
        if isinstance(otsu_val, np.ndarray):
            otsu_val = float(otsu_val.flat[0])
        else:
            otsu_val = float(otsu_val)
        method2_low = max(0, int(otsu_val * 0.5))
        method2_high = min(255, int(otsu_val * 1.0))
        
        # 选择更敏感的阈值（更低的阈值）
        adaptive_threshold1 = min(method1_low, method2_low, threshold1)
        adaptive_threshold2 = min(method1_high, method2_high, threshold2)
        
        # 确保阈值在合理范围
        adaptive_threshold1 = max(10, adaptive_threshold1)
        adaptive_threshold2 = max(50, min(200, adaptive_threshold2))
        
        print(f"自适应阈值: {adaptive_threshold1}/{adaptive_threshold2} (中值={median:.1f}, Otsu={otsu_val:.1f})")
        
        # Canny边缘检测
        edges = cv2.Canny(blurred, adaptive_threshold1, adaptive_threshold2)
        edge_count = cv2.countNonZero(edges)
        print(f"Canny边缘检测: {edge_count}像素")
        
        # 多级降级策略
        if edge_count < 500:
            print("边缘较少，尝试更低阈值...")
            adaptive_threshold1 = max(5, int(adaptive_threshold1 * 0.3))
            adaptive_threshold2 = int(adaptive_threshold2 * 0.5)
            edges = cv2.Canny(blurred, adaptive_threshold1, adaptive_threshold2)
            edge_count = cv2.countNonZero(edges)
            print(f"重新检测: {edge_count}像素 (阈值={adaptive_threshold1}/{adaptive_threshold2})")
            
            # 如果还是太少，使用极低阈值
            if edge_count < 100:
                print("边缘极少，使用极低阈值...")
                edges = cv2.Canny(blurred, 5, 30)
                edge_count = cv2.countNonZero(edges)
                print(f"极低阈值检测: {edge_count}像素")
        
        # 应用骨架化，解决双线条问题（将粗线变成单像素宽的中心线）
        if use_skeleton:
            print(f"应用骨架化（{skeleton_method}模式），消除双线条...")
            
            if skeleton_method == 'gentle':
                # 改进的温和方法：闭运算+细化
                # 先闭运算合并接近的线条（消除双线条之间的间隙）
                kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_close, iterations=2)
                
                # 使用Zhang-Suen细化算法（保留连接性和拓扑结构）
                try:
                    edges = cv2.ximgproc.thinning(edges, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)
                    skeleton_count = cv2.countNonZero(edges)
                    print(f"Zhang-Suen细化后: {skeleton_count}像素")
                except (AttributeError, cv2.error):
                    # 如果没有ximgproc模块，使用距离变换方法
                    print("使用距离变换骨架化...")
                    # 距离变换 + 局部最大值提取（更好的中心线）
                    dist_transform = cv2.distanceTransform(edges, cv2.DIST_L2, 5)
                    # 归一化
                    dist_norm = cv2.normalize(dist_transform, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
                    # 提取骨架（距离变换的局部最大值）
                    _, edges = cv2.threshold(dist_norm, 0.5 * dist_norm.max(), 255, cv2.THRESH_BINARY)
                    # 再次细化
                    kernel_cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
                    edges = cv2.erode(edges, kernel_cross, iterations=1)
                    skeleton_count = cv2.countNonZero(edges)
                    print(f"距离变换骨架化后: {skeleton_count}像素")
            else:
                # 强力方法：闭运算 + 完全骨架化
                # 先大力闭运算，强制合并双线条
                kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_close, iterations=3)
                
                # 然后完全骨架化
                edges = self._morphological_skeleton(edges)
                skeleton_count = cv2.countNonZero(edges)
                print(f"强力骨架化后: {skeleton_count}像素 (减少{edge_count - skeleton_count}像素)")
        else:
            print("跳过骨架化（保持原始边缘）")
        
        self.processed_image = edges
        return self.processed_image
    
    def extract_contours(self, min_length: int = 50, remove_duplicates: bool = True, 
                        duplicate_threshold: float = 5.0):
        """
        提取轮廓线条（保留所有点以确保流畅）
        
        Args:
            min_length: 最小线条长度，过滤掉太短的线条
            remove_duplicates: 是否去除重复的平行线条（解决双线条问题）
            duplicate_threshold: 判定为重复线条的最大距离（像素）
        """
        import time
        start_time = time.time()
        
        if self.processed_image is None:
            self.preprocess()
        
        # 查找轮廓 - 使用CHAIN_APPROX_NONE保留所有轮廓点
        t1 = time.time()
        contours, hierarchy = cv2.findContours(
            self.processed_image, 
            cv2.RETR_LIST, 
            cv2.CHAIN_APPROX_NONE  # 保留所有点，确保线条流畅
        )
        print(f"[性能] 查找轮廓: {(time.time()-t1)*1000:.0f}ms")
        
        # 过滤太短的轮廓
        t2 = time.time()
        self.contours = []
        for cnt in contours:
            length = cv2.arcLength(cnt, False)
            if length > min_length:
                self.contours.append(cnt)
        print(f"[性能] 过滤轮廓: {(time.time()-t2)*1000:.0f}ms")
        
        # 按长度排序，优先绘制主要轮廓
        t3 = time.time()
        self.contours.sort(key=lambda cnt: cv2.arcLength(cnt, False), reverse=True)
        print(f"[性能] 排序: {(time.time()-t3)*1000:.0f}ms")
        
        # 去除重复的平行线条（解决双线条问题）
        if remove_duplicates and len(self.contours) > 1:
            t4 = time.time()
            print(f"检查重复线条（阈值={duplicate_threshold}px）...")
            original_count = len(self.contours)
            self.contours = self._remove_duplicate_contours(self.contours, duplicate_threshold)
            removed_count = original_count - len(self.contours)
            print(f"[性能] 去重: {(time.time()-t4)*1000:.0f}ms")
            if removed_count > 0:
                print(f"去除了 {removed_count} 条重复线条")
        
        print(f"[性能] extract_contours总计: {(time.time()-start_time)*1000:.0f}ms")
        return self.contours
    
    def _remove_duplicate_contours(self, contours, threshold):
        """
        去除重复的平行线条（双线条问题）
        
        Args:
            contours: 轮廓列表
            threshold: 判定为重复的最大距离
            
        Returns:
            去重后的轮廓列表
        """
        if len(contours) < 2:
            return contours
        
        # 标记要保留的轮廓
        keep = [True] * len(contours)
        
        # 遍历所有轮廓对
        for i in range(len(contours)):
            if not keep[i]:
                continue
                
            for j in range(i + 1, len(contours)):
                if not keep[j]:
                    continue
                
                # 检查两条线是否是双线条
                if self._is_duplicate_pair(contours[i], contours[j], threshold):
                    # 保留较长的线条
                    len_i = cv2.arcLength(contours[i], False)
                    len_j = cv2.arcLength(contours[j], False)
                    if len_i >= len_j:
                        keep[j] = False
                    else:
                        keep[i] = False
                        break
        
        # 返回保留的轮廓
        return [cnt for i, cnt in enumerate(contours) if keep[i]]
    
    def _is_duplicate_pair(self, contour1, contour2, threshold):
        """
        判断两条轮廓是否是重复的双线条
        
        策略：
        1. 采样两条线的点
        2. 计算平均距离
        3. 如果平均距离小于阈值，认为是双线条
        """
        # 采样点（最多20个点）
        step1 = max(1, len(contour1) // 20)
        step2 = max(1, len(contour2) // 20)
        sample1 = contour1[::step1]
        sample2 = contour2[::step2]
        
        # 计算每个sample1点到sample2的最小距离
        distances = []
        for pt1 in sample1:
            min_dist = float('inf')
            for pt2 in sample2:
                dist = np.linalg.norm(pt1[0].astype(float) - pt2[0].astype(float))
                min_dist = min(min_dist, dist)
            distances.append(min_dist)
        
        # 计算平均距离
        avg_distance = np.mean(distances)
        
        # 如果平均距离小于阈值，认为是双线条
        return avg_distance < threshold
    
    def get_drawing_points(self, simplify: bool = False, epsilon: float = 2.0, smooth: bool = True):
        """
        获取用于绘画的点序列（优化流畅性）
        
        Args:
            simplify: 是否简化线条（减少点数但保持流畅）
            epsilon: 简化程度，值越大简化越多
            smooth: 是否平滑线条（去除抖动）
            
        Returns:
            List[List[Tuple[int, int]]]: 每条线的点列表
        """
        import time
        start_time = time.time()
        
        if not self.contours:
            self.extract_contours()
        
        all_strokes = []
        smooth_time = 0
        
        for contour in self.contours:
            points = [tuple(point[0]) for point in contour]
            
            # 智能平滑：去除抖动但保持形状
            # 对较长的线条应用平滑，短线条保持原样
            if smooth and len(points) > 5:
                t_smooth = time.time()
                points = self._smooth_points(points)
                smooth_time += time.time() - t_smooth
            
            # 可选的简化（减少点数，加快绘画速度）
            # 默认关闭，因为平滑后已经比较流畅了
            if simplify and len(points) > 20:
                epsilon_value = epsilon
                approx = cv2.approxPolyDP(
                    np.array(points).reshape(-1, 1, 2).astype(np.int32),
                    epsilon_value, 
                    False
                )
                points = [tuple(point[0]) for point in approx]
            
            if len(points) > 1:
                all_strokes.append(points)
        
        # 按照线条长度排序，先画主要线条
        all_strokes.sort(key=lambda stroke: len(stroke), reverse=True)
        
        print(f"[性能] 平滑处理: {smooth_time*1000:.0f}ms")
        print(f"[性能] get_drawing_points总计: {(time.time()-start_time)*1000:.0f}ms")
        
        self.drawing_points = all_strokes
        return all_strokes
    
    def _smooth_points(self, points, window_size=5, iterations=1):
        """
        极致平滑算法 - 一笔画效果
        
        Args:
            points: 原始点序列
            window_size: 平滑窗口大小
            iterations: 平滑迭代次数
        """
        if len(points) < 4:
            return points
        
        # 方法1：使用样条插值（极致平滑）
        try:
            from scipy.interpolate import splprep, splev
            
            # 提取x, y坐标
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            
            # 平滑参数：优先保证形状准确度
            # 极低平滑强度，只去除轻微抖动，最大程度保持原始形状
            s_value = len(points) * 0.3  # 极轻微平滑，高度保真
            
            # 使用三次样条
            tck, u = splprep([x, y], s=s_value, k=min(3, len(points)-1))
            
            # 点数控制：保持尽可能多的点，确保形状高度准确
            # 极保守策略：只对超长线条进行轻微减少
            if len(points) < 100:
                target_points = len(points)  # <100点：完全保持
            elif len(points) < 300:
                target_points = int(len(points) * 0.95)  # 100-300点：只减少5%
            else:
                target_points = int(len(points) * 0.9)  # >300点：只减少10%
            
            # 确保不会减少太多
            target_points = max(target_points, min(50, len(points)))
            
            # 生成平滑曲线
            u_final = np.linspace(0, 1, target_points)
            final_x, final_y = splev(u_final, tck)
            smoothed = [(int(float(final_x[i])), int(float(final_y[i]))) for i in range(len(final_x))]
            return smoothed
            
        except:
            # 如果scipy不可用，使用增强高斯滤波
            pass
        
        # 方法2：高斯平滑（备选，平衡速度和平滑度）
        smoothed = list(points)
        
        # 适度迭代，平衡速度
        for _ in range(2):  # 2次迭代（之前3次）
            temp = []
            for i in range(len(smoothed)):
                if i == 0 or i == len(smoothed) - 1:
                    temp.append(smoothed[i])
                else:
                    # 使用更大的窗口
                    half_window = 7 // 2  # 窗口7
                    start = max(0, i - half_window)
                    end = min(len(smoothed), i + half_window + 1)
                    window = smoothed[start:end]
                    
                    # 强高斯加权
                    weights = []
                    sigma = 1.5  # 更平滑的高斯
                    for j in range(len(window)):
                        dist = abs(j - (len(window) // 2))
                        weight = np.exp(-(dist * dist) / (2 * sigma * sigma))
                        weights.append(weight)
                    
                    total_weight = sum(weights)
                    avg_x = sum(p[0] * w for p, w in zip(window, weights)) / total_weight
                    avg_y = sum(p[1] * w for p, w in zip(window, weights)) / total_weight
                    temp.append((int(avg_x), int(avg_y)))
            
            smoothed = temp
        
        # 对高斯平滑结果进行极度保守的点数控制
        # 几乎不减少点数
        if len(smoothed) > 500:
            # 仅对超长线条进行采样
            step = max(1, len(smoothed) // 400)  # 保持绝大多数点
            smoothed = smoothed[::step]
        
        return smoothed
    
    def preview_result(self, scale: float = 1.0):
        """
        预览处理结果
        
        Args:
            scale: 显示缩放比例
        """
        if not self.contours:
            self.extract_contours()
        
        # 创建白色背景
        preview = np.ones_like(self.original_image) * 255
        
        # 绘制所有轮廓
        cv2.drawContours(preview, self.contours, -1, (0, 0, 0), 2)
        
        # 调整显示大小
        if scale != 1.0:
            height, width = preview.shape[:2]
            new_size = (int(width * scale), int(height * scale))
            preview = cv2.resize(preview, new_size)
        
        cv2.imshow('预览 - 按任意键关闭', preview)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return preview
    
    def get_image_size(self) -> Tuple[int, int]:
        """获取图片尺寸 (宽, 高)"""
        if self.original_image is None:
            return 0, 0
        height, width = self.original_image.shape[:2]
        return width, height
    
    def save_preview(self, output_path: str):
        """
        保存预览图片
        
        Args:
            output_path: 输出路径
        """
        if not self.contours:
            self.extract_contours()
        
        preview = np.ones_like(self.original_image) * 255
        cv2.drawContours(preview, self.contours, -1, (0, 0, 0), 2)
        
        # 使用支持中文路径的方式保存图片
        _, img_encoded = cv2.imencode('.png', preview)
        img_encoded.tofile(output_path)


def test_image_processor(image_path: str):
    """测试图像处理功能"""
    processor = ImageProcessor(image_path)
    
    print(f"图片尺寸: {processor.get_image_size()}")
    
    # 预处理
    processor.preprocess(blur_kernel=5, threshold1=50, threshold2=150)
    
    # 提取轮廓
    contours = processor.extract_contours(min_length=50)
    print(f"检测到 {len(contours)} 条线条")
    
    # 获取绘画点
    strokes = processor.get_drawing_points(simplify=True, epsilon=2.0)
    total_points = sum(len(stroke) for stroke in strokes)
    print(f"共 {len(strokes)} 条笔画，{total_points} 个点")
    
    # 预览
    processor.preview_result(scale=0.5)
    
    return processor


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_image_processor(sys.argv[1])
    else:
        print("使用方法: python imgprocess.py <图片路径>")
