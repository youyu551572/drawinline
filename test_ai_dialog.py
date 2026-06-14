"""
测试AI生图功能（现在集成在分栏中）
"""
import sys
from PyQt5.QtWidgets import QApplication
from modern_app import ModernDrawingApp

def test_ai_feature():
    """测试AI生图功能"""
    app = QApplication(sys.argv)
    
    # 创建主应用
    main_app = ModernDrawingApp()
    main_app.show()
    
    print("AI生图功能已集成到分栏中，请在软件中测试")
    print("1. 点击'AI生图'标签页")
    print("2. 在输入框中输入描述")
    print("3. 或点击快速选择按钮")
    print("4. 点击'生成简笔画'按钮")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_ai_feature()
