"""
测试多种边缘/线条检测算法
对比不同方法的效果和性能
"""
import cv2
import numpy as np
import sys
import time
from PIL import Image, ImageDraw, ImageFont

def load_image(image_path):
    """加载图片（支持中文路径）"""
    img_data = np.fromfile(image_path, dtype=np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    return img

def method_canny(img):
    """方法1: Canny边缘检测（当前使用）"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    elapsed = (time.time() - start) * 1000
    edge_count = cv2.countNonZero(edges)
    
    return edges, elapsed, edge_count, "Canny边缘检测"

def method_sobel(img):
    """方法2: Sobel算子"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Sobel X和Y方向
    sobelx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    
    # 合并
    sobel = np.sqrt(sobelx**2 + sobely**2)
    sobel = np.uint8(sobel / sobel.max() * 255)
    
    # 二值化
    _, edges = cv2.threshold(sobel, 50, 255, cv2.THRESH_BINARY)
    
    elapsed = (time.time() - start) * 1000
    edge_count = cv2.countNonZero(edges)
    
    return edges, elapsed, edge_count, "Sobel算子"

def method_laplacian(img):
    """方法3: Laplacian算子"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Laplacian
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F, ksize=3)
    laplacian = np.uint8(np.absolute(laplacian))
    
    # 二值化
    _, edges = cv2.threshold(laplacian, 30, 255, cv2.THRESH_BINARY)
    
    elapsed = (time.time() - start) * 1000
    edge_count = cv2.countNonZero(edges)
    
    return edges, elapsed, edge_count, "Laplacian算子"

def method_scharr(img):
    """方法4: Scharr算子（Sobel增强版）"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Scharr X和Y方向
    scharrx = cv2.Scharr(blurred, cv2.CV_64F, 1, 0)
    scharry = cv2.Scharr(blurred, cv2.CV_64F, 0, 1)
    
    # 合并
    scharr = np.sqrt(scharrx**2 + scharry**2)
    scharr = np.uint8(scharr / scharr.max() * 255)
    
    # 二值化
    _, edges = cv2.threshold(scharr, 50, 255, cv2.THRESH_BINARY)
    
    elapsed = (time.time() - start) * 1000
    edge_count = cv2.countNonZero(edges)
    
    return edges, elapsed, edge_count, "Scharr算子"

def method_prewitt(img):
    """方法5: Prewitt算子"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Prewitt核
    kernelx = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)
    kernely = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)
    
    prewittx = cv2.filter2D(blurred, cv2.CV_64F, kernelx)
    prewitty = cv2.filter2D(blurred, cv2.CV_64F, kernely)
    
    # 合并
    prewitt = np.sqrt(prewittx**2 + prewitty**2)
    prewitt = np.uint8(prewitt / prewitt.max() * 255)
    
    # 二值化
    _, edges = cv2.threshold(prewitt, 50, 255, cv2.THRESH_BINARY)
    
    elapsed = (time.time() - start) * 1000
    edge_count = cv2.countNonZero(edges)
    
    return edges, elapsed, edge_count, "Prewitt算子"

def method_adaptive_threshold(img):
    """方法6: 自适应阈值"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 自适应阈值
    edges = cv2.adaptiveThreshold(
        blurred, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11, 2
    )
    
    elapsed = (time.time() - start) * 1000
    edge_count = cv2.countNonZero(edges)
    
    return edges, elapsed, edge_count, "自适应阈值"

def method_morphological_gradient(img):
    """方法7: 形态学梯度"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 形态学梯度 = 膨胀 - 腐蚀
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    gradient = cv2.morphologyEx(blurred, cv2.MORPH_GRADIENT, kernel)
    
    # 二值化
    _, edges = cv2.threshold(gradient, 30, 255, cv2.THRESH_BINARY)
    
    elapsed = (time.time() - start) * 1000
    edge_count = cv2.countNonZero(edges)
    
    return edges, elapsed, edge_count, "形态学梯度"

def method_hough_lines(img):
    """方法8: 霍夫直线检测"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges_canny = cv2.Canny(blurred, 50, 150)
    
    # 霍夫直线检测
    lines = cv2.HoughLinesP(
        edges_canny, 
        rho=1, 
        theta=np.pi/180, 
        threshold=50,
        minLineLength=30,
        maxLineGap=10
    )
    
    # 绘制检测到的直线
    edges = np.zeros_like(edges_canny)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(edges, (x1, y1), (x2, y2), 255, 1)
    
    elapsed = (time.time() - start) * 1000
    edge_count = cv2.countNonZero(edges)
    line_count = len(lines) if lines is not None else 0
    
    return edges, elapsed, edge_count, f"霍夫直线检测({line_count}条)"

def test_all_methods(image_path):
    """测试所有方法"""
    print("=" * 80)
    print("线条识别算法对比测试")
    print("=" * 80)
    print(f"\n测试图片: {image_path}\n")
    
    # 加载图片
    img = load_image(image_path)
    print(f"图片尺寸: {img.shape[1]}x{img.shape[0]}\n")
    
    # 所有方法
    methods = [
        method_canny,
        method_sobel,
        method_laplacian,
        method_scharr,
        method_prewitt,
        method_adaptive_threshold,
        method_morphological_gradient,
        method_hough_lines
    ]
    
    results = []
    
    # 测试每个方法
    for method in methods:
        try:
            edges, elapsed, edge_count, name = method(img)
            
            # 计算轮廓数
            contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            contours = [c for c in contours if cv2.arcLength(c, False) > 50]
            
            results.append({
                'name': name,
                'edges': edges,
                'elapsed': elapsed,
                'edge_count': edge_count,
                'contour_count': len(contours)
            })
            
            print(f"✓ {name:20s} | 耗时: {elapsed:6.1f}ms | 边缘: {edge_count:6d}像素 | 轮廓: {len(contours):3d}条")
        except Exception as e:
            print(f"✗ {method.__name__:20s} | 错误: {str(e)}")
    
    # 生成对比图
    print("\n" + "=" * 80)
    print("生成对比图...")
    print("=" * 80)
    
    # 2x4布局
    h, w = img.shape[:2]
    target_size = (400, 400)
    
    comparison = np.ones((target_size[1] * 2 + 60, target_size[0] * 4 + 100, 3), dtype=np.uint8) * 255
    
    positions = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3)]
    
    # 转换为PIL图像以支持中文
    comparison_pil = Image.fromarray(cv2.cvtColor(comparison, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(comparison_pil)
    
    # 尝试加载中文字体
    try:
        font_title = ImageFont.truetype("msyh.ttc", 16)  # 微软雅黑
        font_info = ImageFont.truetype("msyh.ttc", 14)
    except:
        font_title = ImageFont.load_default()
        font_info = ImageFont.load_default()
    
    for i, result in enumerate(results):
        if i >= len(positions):
            break
        
        row, col = positions[i]
        y_offset = 50 + row * (target_size[1] + 10)
        x_offset = 20 + col * (target_size[0] + 5)
        
        # resize
        edges_resized = cv2.resize(result['edges'], target_size)
        edges_rgb = cv2.cvtColor(edges_resized, cv2.COLOR_GRAY2RGB)
        edges_pil = Image.fromarray(edges_rgb)
        
        # 粘贴图像
        comparison_pil.paste(edges_pil, (x_offset, y_offset))
        
        # 绘制中文标题
        text1 = result['name']
        text2 = f"{result['elapsed']:.0f}ms {result['contour_count']}条"
        draw.text((x_offset + 5, y_offset - 35), text1, fill=(255, 0, 0), font=font_title)
        draw.text((x_offset + 5, y_offset - 18), text2, fill=(100, 100, 100), font=font_info)
    
    # 转回OpenCV格式
    comparison = cv2.cvtColor(np.array(comparison_pil), cv2.COLOR_RGB2BGR)
    
    # 保存
    output_path = 'edge_methods_comparison.png'
    cv2.imwrite(output_path, comparison)
    print(f"\n对比图已保存: {output_path}")
    
    # 显示
    scale = 0.6
    h, w = comparison.shape[:2]
    comparison_resized = cv2.resize(comparison, (int(w * scale), int(h * scale)))
    cv2.imshow('线条识别算法对比 (按任意键关闭)', comparison_resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 推荐
    print("\n" + "=" * 80)
    print("推荐算法:")
    print("=" * 80)
    
    # 按轮廓数排序（适中最好）
    sorted_by_contours = sorted(results, key=lambda x: abs(x['contour_count'] - 40))
    best = sorted_by_contours[0]
    
    print(f"✓ 最佳: {best['name']}")
    print(f"  - 轮廓数适中: {best['contour_count']}条")
    print(f"  - 性能: {best['elapsed']:.1f}ms")
    print(f"  - 边缘像素: {best['edge_count']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_all_methods(sys.argv[1])
    else:
        print("使用方法: python test_edge_methods.py <图片路径>")
        print("\n这个脚本会测试8种不同的线条识别算法并生成对比图。")
