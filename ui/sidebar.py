"""
侧边栏导航组件
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class SidebarButton(QPushButton):
    """侧边栏按钮"""
    
    def __init__(self, text: str, module_id: str, parent=None):
        super().__init__(text, parent)
        self.module_id = module_id
        self.setCheckable(True)
        self.setMinimumHeight(45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }
        """)


class SidebarWidget(QWidget):
    """侧边栏导航组件"""
    
    module_changed = pyqtSignal(str)
    clear_cache_requested = pyqtSignal()
    
    MODULES = [
        ("module1", "IDW插值", "反距离加权插值 (开发中)"),
        ("module2", "GPS高程拟合", "平面/二次曲面拟合"),
        ("module3", "时间系统转换", "公历/JD/GPS时间互转 (开发中)"),
        ("module4", "多边形面积计算", "鞋带公式计算"),
        ("module5", "坐标转换", "XYZ与BLH/NEU坐标互转"),
        ("module6", "滑坡监测", "变形速度与应变分析"),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = {}
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        title_label = QLabel("DSP测绘系统")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #1976D2; padding: 15px;")
        layout.addWidget(title_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(line)
        
        nav_label = QLabel("功能模块")
        nav_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        nav_label.setStyleSheet("color: #666666; padding: 10px 5px;")
        layout.addWidget(nav_label)
        
        for module_id, module_name, tooltip in self.MODULES:
            btn = SidebarButton(f"  {module_name}", module_id)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, mid=module_id: self._on_button_clicked(mid))
            self.buttons[module_id] = btn
            layout.addWidget(btn)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(line2)
        
        clear_cache_btn = QPushButton("清理缓存")
        clear_cache_btn.setMinimumHeight(40)
        clear_cache_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_cache_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
            QPushButton:pressed {
                background-color: #BF360C;
            }
        """)
        clear_cache_btn.clicked.connect(self.clear_cache_requested.emit)
        layout.addWidget(clear_cache_btn)
        
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #999999; padding: 10px;")
        layout.addWidget(version_label)
        
        self.setMinimumWidth(220)
        self.setMaximumWidth(280)
        self.setStyleSheet("background-color: #FAFAFA;")
        
        if self.buttons:
            first_module = list(self.buttons.keys())[0]
            self.buttons[first_module].setChecked(True)
    
    def _on_button_clicked(self, module_id: str):
        for btn in self.buttons.values():
            btn.setChecked(False)
        self.buttons[module_id].setChecked(True)
        self.module_changed.emit(module_id)
    
    def set_current_module(self, module_id: str):
        if module_id in self.buttons:
            self._on_button_clicked(module_id)
