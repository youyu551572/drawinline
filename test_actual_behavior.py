"""测试软件实际行为（与modern_app.py完全一致）"""
import sys
from imgprocess import ImageProcessor

def test_actual_behavior(image_path):
    """使用与软件完全相同的参数测试"""
    
    print("=" * 80)
    print(f"测试图片: {image_path}")
    print("=" * 80)
    
    # 创建处理器（与软件相同）
    processor = ImageProcessor(image_path)
    
    # 使用软件默认参数
    params = {
        'blur_kernel': 5,
        'threshold1': 50,
        'threshold2': 150,
        'min_length': 50,
        'simplify': False,
        'epsilon': 2.0
    }
    
    # 预处理（与modern_app.py第59-65行相同）
    processor.preprocess(
        blur_kernel=params['blur_kernel'],
        threshold1=params['threshold1'],
        threshold2=params['threshold2'],
        use_skeleton=False,
        skeleton_method='gentle'
    )
    
    # 提取轮廓（与modern_app.py第69-73行相同）
    contours = processor.extract_contours(
        min_length=params['min_length'],
        remove_duplicates=False,  # v2.0.44: 关闭去重以提升性能
        duplicate_threshold=5.0
    )
    
    # 获取绘画点（与modern_app.py第76-80行相同）
    strokes = processor.get_drawing_points(
        simplify=params['simplify'],
        epsilon=params['epsilon'],
        smooth=True
    )
    
    # 统计
    total_points = sum(len(stroke) for stroke in strokes)
    
    print("\n" + "=" * 80)
    print("处理结果:")
    print("=" * 80)
    print(f"轮廓数: {len(contours)}")
    print(f"笔画数: {len(strokes)}")
    print(f"总点数: {total_points}")
    print("=" * 80)
    
    return processor, strokes

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_actual_behavior(sys.argv[1])
    else:
        print("使用方法: python test_actual_behavior.py <图片路径>")
        print("\n这个脚本使用与软件完全相同的参数和流程。")
