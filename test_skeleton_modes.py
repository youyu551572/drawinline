"""测试不同骨架化模式的效果"""
import cv2
import numpy as np
from imgprocess import ImageProcessor
import sys

def test_skeleton_modes(image_path):
    """对比不同骨架化模式的效果"""
    
    print("=" * 80)
    print("骨架化模式对比测试")
    print("=" * 80)
    
    modes = [
        ('无处理', False, 'gentle', False),
        ('轮廓去重', False, 'gentle', True),
        ('骨架化（温和）', True, 'gentle', False),
        ('骨架化（强力）', True, 'strong', False)
    ]
    
    results = []
    
    for mode_name, use_skeleton, skeleton_method, remove_duplicates in modes:
        print(f"\n{'='*80}")
        print(f"测试: {mode_name}")
        print(f"{'='*80}")
        
        # 创建新的处理器
        processor = ImageProcessor(image_path)
        
        # 预处理
        processor.preprocess(
            blur_kernel=5,
            threshold1=50,
            threshold2=150,
            use_skeleton=use_skeleton,
            skeleton_method=skeleton_method
        )
        
        # 提取轮廓
        contours = processor.extract_contours(
            min_length=50,
            remove_duplicates=remove_duplicates,
            duplicate_threshold=5.0
        )
        print(f"检测到 {len(contours)} 条线条")
        
        # 获取绘画点
        strokes = processor.get_drawing_points(simplify=False, smooth=True)
        total_points = sum(len(stroke) for stroke in strokes)
        print(f"共 {len(strokes)} 条笔画，{total_points} 个点")
        
        # 保存结果图
        preview = np.ones_like(processor.original_image) * 255
        cv2.drawContours(preview, processor.contours, -1, (0, 0, 0), 1)
        
        results.append((mode_name, preview, len(contours), total_points))
    
    print(f"\n{'='*80}")
    print("生成对比图...")
    print(f"{'='*80}")
    
    # 统一所有图像尺寸到固定大小（避免尺寸不匹配）
    target_size = (400, 400)
    
    # 统一尺寸并转换为彩色
    unified_results = []
    for mode_name, preview, contours, points in results:
        # 确保preview是彩色图像
        if len(preview.shape) == 2:
            preview = cv2.cvtColor(preview, cv2.COLOR_GRAY2BGR)
        
        # resize到统一大小
        preview_resized = cv2.resize(preview, target_size)
        unified_results.append((mode_name, preview_resized, contours, points))
    
    # 创建对比图（2x2布局，因为有4种模式）
    height, width = target_size[1], target_size[0]
    gap = 20  # 图片间隙
    comparison = np.ones((height * 2 + gap * 3, width * 2 + gap * 3, 3), dtype=np.uint8) * 255
    
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    
    for i, (mode_name, preview, contours, points) in enumerate(unified_results):
        if i >= len(positions):
            break
        row, col = positions[i]
        y_offset = gap + row * (height + gap)
        x_offset = gap + col * (width + gap)
        
        comparison[y_offset:y_offset+height, x_offset:x_offset+width] = preview
        
        # 添加标题（在图片上方）
        text = f"{mode_name}"
        text2 = f"{contours}条线 {points}点"
        # 确保标题在图片范围内
        title_y1 = max(y_offset - 5, 15)
        title_y2 = max(y_offset + 20, 35)
        cv2.putText(comparison, text, (x_offset + 10, title_y1), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(comparison, text2, (x_offset + 10, title_y2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
    
    # 显示对比图
    scale = 0.8
    h, w = comparison.shape[:2]
    comparison_resized = cv2.resize(comparison, (int(w * scale), int(h * scale)))
    
    cv2.imshow('骨架化模式对比 (按任意键关闭)', comparison_resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 保存对比图
    output_path = 'skeleton_comparison.png'
    cv2.imwrite(output_path, comparison)
    print(f"\n对比图已保存到: {output_path}")
    
    print(f"\n{'='*80}")
    print("对比总结:")
    print(f"{'='*80}")
    for mode_name, _, contours, points in results:
        print(f"{mode_name:12s}: {contours:4d}条线, {points:6d}个点")
    
    print(f"\n推荐:")
    print("  - 如果双线条严重 → 使用【强力模式】")
    print("  - 如果需要保留细节 → 使用【温和模式】")
    print("  - 如果需要最原始的识别 → 使用【无骨架化】")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_skeleton_modes(sys.argv[1])
    else:
        print("使用方法: python test_skeleton_modes.py <图片路径>")
        print("\n示例:")
        print("  python test_skeleton_modes.py test.png")
        print("\n将生成三种模式的对比图，帮助选择最佳处理方式。")
