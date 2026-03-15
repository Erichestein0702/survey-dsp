"""
主窗口
"""

import sys
import gc
from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, 
    QStatusBar, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

from .sidebar import SidebarWidget
from .module_widgets import (
    IDWWidget,
    ElevationFittingWidget,
    TimeSystemWidget,
    AreaCalculationWidget,
    CoordTransformWidget,
    LandslideMonitorWidget
)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.module_widgets: Dict[str, Optional[QWidget]] = {}
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("测绘综合实习DSP系统")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = SidebarWidget()
        self.sidebar.module_changed.connect(self.switch_module)
        self.sidebar.clear_cache_requested.connect(self.clear_cache)
        main_layout.addWidget(self.sidebar)
        
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.content_stack, 1)
        
        self._create_module_widgets()
        
        self.statusBar().showMessage("就绪")
        
        self._create_menu()
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QStatusBar {
                background-color: #E0E0E0;
                color: #666666;
            }
        """)
    
    def _create_module_widgets(self):
        """创建模块组件"""
        self.module_widgets['module1'] = IDWWidget()
        self.module_widgets['module2'] = ElevationFittingWidget()
        self.module_widgets['module3'] = TimeSystemWidget()
        self.module_widgets['module4'] = AreaCalculationWidget()
        self.module_widgets['module5'] = CoordTransformWidget()
        self.module_widgets['module6'] = LandslideMonitorWidget()
        
        for widget in self.module_widgets.values():
            self.content_stack.addWidget(widget)
        
        self.content_stack.setCurrentWidget(self.module_widgets['module1'])
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件")
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def switch_module(self, module_id: str):
        """切换模块"""
        if module_id in self.module_widgets:
            widget = self.module_widgets[module_id]
            self.content_stack.setCurrentWidget(widget)
            self.statusBar().showMessage(f"当前模块: {widget.module_name}")
        else:
            self.statusBar().showMessage(f"模块 {module_id} 正在开发中...")
    
    def clear_cache(self):
        """清理缓存"""
        reply = QMessageBox.question(
            self, "确认清理", 
            "确定要清理缓存吗？这将释放内存但不会影响已保存的数据。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for widget in self.module_widgets.values():
                if hasattr(widget, 'clear_data'):
                    widget.clear_data()
            
            gc.collect()
            
            self.statusBar().showMessage("缓存已清理")
            QMessageBox.information(self, "完成", "缓存清理完成！")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            """<h3>测绘综合实习DSP系统</h3>
            <p>版本: 1.0.0</p>
            <p>本系统实现以下DSP算法模块：</p>
            <ul>
            <li>模块1: IDW插值 (反距离加权)</li>
            <li>模块2: GPS高程拟合</li>
            <li>模块3: 时间系统转换</li>
            <li>模块4: 多边形面积计算</li>
            <li>模块5: 坐标转换</li>
            <li>模块6: 滑坡监测</li>
            </ul>
            <p>使用Python + PyQt6开发</p>
            """
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self, "确认退出",
            "确定要退出程序吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def run_app():
    """运行应用程序"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    app.setStyleSheet("""
        QToolTip {
            background-color: #333333;
            color: white;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 3px;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #CCCCCC;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QTableWidget {
            gridline-color: #E0E0E0;
            border: 1px solid #CCCCCC;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QTableWidget::item:selected {
            background-color: #BBDEFB;
            color: black;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    run_app()
