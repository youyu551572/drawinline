"""测试不同Canny阈值对双线条的影响"""
import cv2
import numpy as np
from imgprocess import ImageProcessor
import sys

def test_canny_thresholds(image_path):
    """对比不同Canny阈值的效果"""
    
    print("=" * 80)
    print("Canny阈值对比测试 - 解决双线条问题")
    print("=" * 80)
    
    # 测试不同的阈值组合
    threshold_configs = [
        ('默认（敏感）', 50, 150),
        ('适中', 70, 180),
        ('较高', 90, 220),
        ('很高', 110, 260),
    ]
    
    results = []
    
    for config_name, threshold1, threshold2 in threshold_configs:
        print(f"\n{'='*80}")
        print(f"测试: {config_name} (threshold1={threshold1}, threshold2={threshold2})")
        print(f"{'='*80}")
        
        # 创建新的处理器
        processor = ImageProcessor(image_path)
        
        # 预处理（不使用骨架化）
        processor.preprocess(
            blur_kernel=5,
            threshold1=threshold1,
            threshold2=threshold2,
            use_skeleton=False  # 关键：不用骨架化
        )
        
        # 提取轮廓
        contours = processor.extract_contours(min_length=50)
        print(f"检测到 {len(contours)} 条线条")
        
        # 获取绘画点
        strokes = processor.get_drawing_points(simplify=False, smooth=True)
        total_points = sum(len(stroke) for stroke in strokes)
        print(f"共 {len(strokes)} 条笔画，{total_points} 个点")
        
        # 保存结果图
        preview = np.ones_like(processor.original_image) * 255
        cv2.drawContours(preview, processor.contours, -1, (0, 0, 0), 1)
        
        results.append((config_name, threshold1, threshold2, preview, len(contours), total_points))
    
    print(f"\n{'='*80}")
    print("生成对比图...")
    print(f"{'='*80}")
    
    # 创建对比图（2x2布局）
    height, width = results[0][3].shape[:2]
    
    # 两行两列
    comparison = np.ones((height * 2 + 20, width * 2 + 20, 3), dtype=np.uint8) * 255
    
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    
    for idx, (config_name, t1, t2, preview, contours, points) in enumerate(results):
        row, col = positions[idx]
        y_offset = row * (height + 20)
        x_offset = col * (width + 20)
        
        # 确保preview是彩色图像
        if len(preview.shape) == 2:
            preview = cv2.cvtColor(preview, cv2.COLOR_GRAY2BGR)
        
        comparison[y_offset:y_offset+height, x_offset:x_offset+width] = preview
        
        # 添加标题和统计
        text1 = f"{config_name}"
        text2 = f"T:{t1}/{t2}"
        text3 = f"{contours}条线 {points}点"
        
        cv2.putText(comparison, text1, (x_offset + 10, y_offset + 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(comparison, text2, (x_offset + 10, y_offset + 55), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv2.putText(comparison, text3, (x_offset + 10, y_offset + 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
    
    # 显示对比图
    scale = 0.6
    h, w = comparison.shape[:2]
    comparison_resized = cv2.resize(comparison, (int(w * scale), int(h * scale)))
    
    cv2.imshow('Canny阈值对比 (按任意键关闭)', comparison_resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 保存对比图
    output_path = 'canny_threshold_comparison.png'
    cv2.imwrite(output_path, comparison)
    print(f"\n对比图已保存到: {output_path}")
    
    print(f"\n{'='*80}")
    print("对比总结:")
    print(f"{'='*80}")
    print(f"{'配置':<15s} {'阈值':<12s} {'线条数':>8s} {'点数':>8s}")
    print("-" * 80)
    for config_name, t1, t2, _, contours, points in results:
        threshold_str = f"{t1}/{t2}"
        print(f"{config_name:<15s} {threshold_str:<12s} {contours:>8d} {points:>8d}")
    
    print(f"\n{'='*80}")
    print("选择建议:")
    print(f"{'='*80}")
    
    # 找到线条数最少的配置（可能是双线条最少的）
    min_contours = min(r[4] for r in results)
    best_configs = [r for r in results if r[4] == min_contours]
    
    if len(best_configs) == 1:
        config = best_configs[0]
        print(f"✅ 推荐使用: {config[0]}")
        print(f"   阈值: threshold1={config[1]}, threshold2={config[2]}")
        print(f"   效果: {config[4]}条线，{config[5]}个点")
    else:
        print("推荐配置（线条数相同，选择阈值较高的）:")
        for config in best_configs:
            print(f"  - {config[0]}: threshold1={config[1]}, threshold2={config[2]}")
    
    print(f"\n💡 通用建议:")
    print("  - 如果双线条严重 → 选择阈值更高的配置")
    print("  - 如果细节丢失 → 选择阈值较低的配置")
    print("  - 通常【适中】或【较高】配置效果最好")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_canny_thresholds(sys.argv[1])
    else:
        print("使用方法: python test_canny_thresholds.py <图片路径>")
        print("\n示例:")
        print("  python test_canny_thresholds.py test.png")
        print("\n将测试4种不同的Canny阈值配置，找到解决双线条的最佳参数。")
