"""
UI可视化调整工具
实时调整界面参数并生成代码
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QPushButton, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class UIAdjuster(QMainWindow):
    """UI参数调整工具"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouYu自动绘画 - UI参数调整工具")
        self.setGeometry(100, 100, 600, 500)
        
        # 参数字典
        self.params = {
            'panel_max_width': 280,
            'panel_min_width': 227,
            'tab_height': 500,
            'ai_spacing': 6,
            'ai_margins': 6,
            'input_height': 70,
            'history_height': 120
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("UI参数实时调整")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 参数调整区域
        self.create_slider("面板最大宽度", 'panel_max_width', 200, 400, layout)
        self.create_slider("面板最小宽度", 'panel_min_width', 150, 300, layout)
        self.create_slider("标签页高度", 'tab_height', 300, 700, layout)
        self.create_slider("AI分栏间距", 'ai_spacing', 2, 20, layout)
        self.create_slider("AI分栏边距", 'ai_margins', 2, 20, layout)
        self.create_slider("输入框高度", 'input_height', 40, 120, layout)
        self.create_slider("历史区高度", 'history_height', 60, 200, layout)
        
        # 生成代码按钮
        generate_btn = QPushButton("生成调整代码")
        generate_btn.clicked.connect(self.generate_code)
        layout.addWidget(generate_btn)
        
        # 代码显示区域
        self.code_display = QTextEdit()
        self.code_display.setMaximumHeight(150)
        layout.addWidget(self.code_display)
        
        # 初始生成代码
        self.generate_code()
    
    def create_slider(self, name, param_key, min_val, max_val, layout):
        """创建滑块控件"""
        container = QWidget()
        h_layout = QHBoxLayout(container)
        
        # 标签
        label = QLabel(f"{name}:")
        label.setMinimumWidth(100)
        h_layout.addWidget(label)
        
        # 滑块
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(self.params[param_key])
        slider.valueChanged.connect(lambda v, key=param_key: self.update_param(key, v))
        h_layout.addWidget(slider)
        
        # 数值显示
        value_label = QLabel(str(self.params[param_key]))
        value_label.setMinimumWidth(40)
        h_layout.addWidget(value_label)
        
        # 保存引用以便更新
        setattr(self, f"{param_key}_label", value_label)
        
        layout.addWidget(container)
    
    def update_param(self, key, value):
        """更新参数值"""
        self.params[key] = value
        # 更新显示
        label = getattr(self, f"{key}_label")
        label.setText(str(value))
        # 重新生成代码
        self.generate_code()
    
    def generate_code(self):
        """生成调整代码"""
        code = f"""# UI参数调整代码
# 复制以下代码到 modern_app.py 对应位置

# 1. 面板宽度调整 (第368-369行)
panel.setMaximumWidth({self.params['panel_max_width']})
panel.setMinimumWidth({self.params['panel_min_width']})

# 2. 标签页高度调整 (第383行)
tab_widget.setMinimumHeight({self.params['tab_height']})

# 3. AI分栏布局调整 (第771-772行)
tab4_layout.setSpacing({self.params['ai_spacing']})
tab4_layout.setContentsMargins({self.params['ai_margins']}, {self.params['ai_margins']}, {self.params['ai_margins']}, {self.params['ai_margins']})

# 4. 输入框高度调整 (第814行)
self.ai_prompt_edit.setMaximumHeight({self.params['input_height']})

# 5. 历史区高度调整 (第891行)
self.ai_history_scroll.setMaximumHeight({self.params['history_height']})
"""
        self.code_display.setPlainText(code)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    adjuster = UIAdjuster()
    adjuster.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
