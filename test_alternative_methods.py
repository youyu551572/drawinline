"""
详细测试自适应阈值和形态学梯度
与当前Canny方法对比
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

def method_current_canny(img):
    """当前方法: Canny + CLAHE"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    elapsed = (time.time() - start) * 1000
    return edges, elapsed, "当前Canny方法"

def method_adaptive_threshold(img):
    """方法1: 自适应阈值"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # CLAHE增强（与当前方法保持一致）
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # 自适应阈值
    edges = cv2.adaptiveThreshold(
        blurred, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11, 2
    )
    
    elapsed = (time.time() - start) * 1000
    return edges, elapsed, "自适应阈值"

def method_morphological_gradient(img):
    """方法2: 形态学梯度"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # CLAHE增强（与当前方法保持一致）
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # 形态学梯度 = 膨胀 - 腐蚀
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    gradient = cv2.morphologyEx(blurred, cv2.MORPH_GRADIENT, kernel)
    
    # 二值化
    _, edges = cv2.threshold(gradient, 30, 255, cv2.THRESH_BINARY)
    
    elapsed = (time.time() - start) * 1000
    return edges, elapsed, "形态学梯度"

def method_adaptive_optimized(img):
    """方法3: 优化的自适应阈值（多参数）"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # 更大的窗口，更好的适应性
    edges = cv2.adaptiveThreshold(
        blurred, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        15, 3  # 更大的窗口
    )
    
    elapsed = (time.time() - start) * 1000
    return edges, elapsed, "自适应阈值(优化)"

def method_morphological_optimized(img):
    """方法4: 优化的形态学梯度（多尺度）"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # 多尺度形态学梯度
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    
    gradient1 = cv2.morphologyEx(blurred, cv2.MORPH_GRADIENT, kernel1)
    gradient2 = cv2.morphologyEx(blurred, cv2.MORPH_GRADIENT, kernel2)
    
    # 合并
    gradient = cv2.addWeighted(gradient1, 0.7, gradient2, 0.3, 0)
    
    # 二值化
    _, edges = cv2.threshold(gradient, 25, 255, cv2.THRESH_BINARY)
    
    elapsed = (time.time() - start) * 1000
    return edges, elapsed, "形态学梯度(多尺度)"

def method_hybrid(img):
    """方法5: 混合方法（Canny + 形态学）"""
    start = time.time()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # Canny
    canny = cv2.Canny(blurred, 50, 150)
    
    # 形态学梯度
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    gradient = cv2.morphologyEx(blurred, cv2.MORPH_GRADIENT, kernel)
    _, gradient_binary = cv2.threshold(gradient, 30, 255, cv2.THRESH_BINARY)
    
    # 合并（取并集）
    edges = cv2.bitwise_or(canny, gradient_binary)
    
    elapsed = (time.time() - start) * 1000
    return edges, elapsed, "混合方法(Canny+形态学)"

def analyze_method(edges, name):
    """分析方法效果"""
    # 边缘像素数
    edge_count = cv2.countNonZero(edges)
    
    # 轮廓数和点数
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours_filtered = [c for c in contours if cv2.arcLength(c, False) > 50]
    
    total_points = sum(len(c) for c in contours_filtered)
    
    return {
        'name': name,
        'edges': edges,
        'edge_count': edge_count,
        'contour_count': len(contours_filtered),
        'total_points': total_points
    }

def test_methods(image_path):
    """测试所有方法"""
    print("=" * 80)
    print("线条识别算法详细对比")
    print("=" * 80)
    print(f"\n测试图片: {image_path}\n")
    
    img = load_image(image_path)
    print(f"图片尺寸: {img.shape[1]}x{img.shape[0]}\n")
    
    methods = [
        method_current_canny,
        method_adaptive_threshold,
        method_morphological_gradient,
        method_adaptive_optimized,
        method_morphological_optimized,
        method_hybrid
    ]
    
    results = []
    
    print("=" * 80)
    print("性能测试")
    print("=" * 80)
    
    for method in methods:
        edges, elapsed, name = method(img)
        analysis = analyze_method(edges, name)
        analysis['elapsed'] = elapsed
        results.append(analysis)
        
        print(f"{name:25s} | {elapsed:5.1f}ms | {analysis['edge_count']:6d}像素 | "
              f"{analysis['contour_count']:3d}条线 | {analysis['total_points']:6d}点")
    
    # 生成对比图
    print("\n" + "=" * 80)
    print("生成对比图...")
    print("=" * 80)
    
    target_size = (400, 400)
    comparison = np.ones((target_size[1] * 2 + 80, target_size[0] * 3 + 80, 3), dtype=np.uint8) * 255
    
    positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    
    # 转换为PIL以支持中文
    comparison_pil = Image.fromarray(cv2.cvtColor(comparison, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(comparison_pil)
    
    try:
        font_title = ImageFont.truetype("msyh.ttc", 16)
        font_info = ImageFont.truetype("msyh.ttc", 13)
    except:
        font_title = ImageFont.load_default()
        font_info = ImageFont.load_default()
    
    for i, result in enumerate(results):
        if i >= len(positions):
            break
        
        row, col = positions[i]
        y_offset = 60 + row * (target_size[1] + 20)
        x_offset = 20 + col * (target_size[0] + 20)
        
        # 图像
        edges_resized = cv2.resize(result['edges'], target_size)
        edges_rgb = cv2.cvtColor(edges_resized, cv2.COLOR_GRAY2RGB)
        edges_pil = Image.fromarray(edges_rgb)
        comparison_pil.paste(edges_pil, (x_offset, y_offset))
        
        # 标题
        text1 = result['name']
        text2 = f"{result['elapsed']:.1f}ms | {result['contour_count']}条线"
        text3 = f"{result['total_points']}点"
        
        draw.text((x_offset + 5, y_offset - 50), text1, fill=(255, 0, 0), font=font_title)
        draw.text((x_offset + 5, y_offset - 30), text2, fill=(0, 100, 0), font=font_info)
        draw.text((x_offset + 5, y_offset - 15), text3, fill=(100, 100, 100), font=font_info)
    
    comparison = cv2.cvtColor(np.array(comparison_pil), cv2.COLOR_RGB2BGR)
    
    # 保存
    output_path = 'alternative_methods_comparison.png'
    cv2.imwrite(output_path, comparison)
    print(f"\n对比图已保存: {output_path}")
    
    # 显示
    scale = 0.7
    h, w = comparison.shape[:2]
    comparison_resized = cv2.resize(comparison, (int(w * scale), int(h * scale)))
    cv2.imshow('线条识别算法对比 (按任意键关闭)', comparison_resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 推荐
    print("\n" + "=" * 80)
    print("对比分析")
    print("=" * 80)
    
    current = results[0]
    print(f"\n当前方法 ({current['name']}):")
    print(f"  - 耗时: {current['elapsed']:.1f}ms")
    print(f"  - 线条数: {current['contour_count']}条")
    print(f"  - 总点数: {current['total_points']}点")
    
    print("\n替代方案对比:")
    for i, result in enumerate(results[1:], 1):
        time_diff = result['elapsed'] - current['elapsed']
        contour_diff = result['contour_count'] - current['contour_count']
        point_diff = result['total_points'] - current['total_points']
        
        print(f"\n{i}. {result['name']}:")
        print(f"   耗时: {result['elapsed']:.1f}ms ({time_diff:+.1f}ms)")
        print(f"   线条数: {result['contour_count']}条 ({contour_diff:+d}条)")
        print(f"   总点数: {result['total_points']}点 ({point_diff:+d}点)")
        
        # 评价
        if abs(time_diff) < 1 and abs(contour_diff) < 5:
            print(f"   ✓ 性能相当，线条数接近")
        elif time_diff < -1 and abs(contour_diff) < 10:
            print(f"   ✓✓ 性能更好，线条数可接受")
        elif contour_diff < -10:
            print(f"   ⚠ 线条数明显减少，可能丢失细节")
        elif contour_diff > 10:
            print(f"   ⚠ 线条数明显增加，可能过于敏感")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_methods(sys.argv[1])
    else:
        print("使用方法: python test_alternative_methods.py <图片路径>")
        print("\n详细对比自适应阈值、形态学梯度等替代方法。")
