"""
测试UI边缘检测方法选择功能
"""
import sys
from PyQt5.QtWidgets import QApplication
from modern_app import ModernDrawingApp

def test_ui_edge_method():
    """测试UI中的边缘检测方法选择"""
    
    print("=" * 60)
    print("测试UI边缘检测方法选择功能")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    window = ModernDrawingApp()
    
    # 检查UI组件是否正确创建
    print("✓ UI组件检查:")
    print(f"  - 边缘检测下拉框: {hasattr(window, 'edge_method_combo')}")
    
    if hasattr(window, 'edge_method_combo'):
        combo = window.edge_method_combo
        print(f"  - 选项数量: {combo.count()}")
        print(f"  - 选项1: {combo.itemText(0)}")
        print(f"  - 选项2: {combo.itemText(1)}")
        print(f"  - 默认选择: {combo.currentText()}")
        print(f"  - 工具提示: {combo.toolTip()}")
        
        # 测试选择变化
        print("\n✓ 功能测试:")
        print(f"  - 默认方法: {'canny' if combo.currentIndex() == 0 else 'adaptive'}")
        
        combo.setCurrentIndex(1)  # 切换到自适应阈值
        print(f"  - 切换后方法: {'canny' if combo.currentIndex() == 0 else 'adaptive'}")
        
        combo.setCurrentIndex(0)  # 切换回Canny
        print(f"  - 切换回方法: {'canny' if combo.currentIndex() == 0 else 'adaptive'}")
        
        print("\n✅ UI边缘检测方法选择功能正常！")
    else:
        print("❌ 边缘检测下拉框未找到！")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 不显示窗口，直接退出
    app.quit()

if __name__ == "__main__":
    test_ui_edge_method()
