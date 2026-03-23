"""
Sidebar Navigation Component
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from common.i18n import get_i18n_manager, tr


class SidebarButton(QPushButton):
    """Sidebar Button"""
    
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
    """Sidebar Navigation Component"""
    
    module_changed = pyqtSignal(str)
    clear_cache_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = {}
        self.i18n = get_i18n_manager()
        self._init_ui()
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect i18n signals"""
        self.i18n.language_changed.connect(self._on_language_changed)
    
    def _on_language_changed(self, lang_code: str):
        """Handle language change"""
        self._update_texts()
    
    def _update_texts(self):
        """Update all texts after language change"""
        self.title_label.setText(tr("sidebar.title"))
        self.nav_label.setText(tr("sidebar.modules"))
        self.clear_cache_btn.setText(tr("sidebar.clear_cache"))
        
        module_keys = [
            ('module1', 'module.idw', 'module.idw.tooltip'),
            ('module2', 'module.elevation', 'module.elevation.tooltip'),
            ('module3', 'module.time', 'module.time.tooltip'),
            ('module4', 'module.area', 'module.area.tooltip'),
            ('module5', 'module.coord', 'module.coord.tooltip'),
            ('module6', 'module.landslide', 'module.landslide.tooltip'),
        ]
        
        for module_id, name_key, tooltip_key in module_keys:
            if module_id in self.buttons:
                self.buttons[module_id].setText(f"  {tr(name_key)}")
                self.buttons[module_id].setToolTip(tr(tooltip_key))
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        self.title_label = QLabel(tr("sidebar.title"))
        self.title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: #1976D2; padding: 15px;")
        layout.addWidget(self.title_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(line)
        
        self.nav_label = QLabel(tr("sidebar.modules"))
        self.nav_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.nav_label.setStyleSheet("color: #666666; padding: 10px 5px;")
        layout.addWidget(self.nav_label)
        
        module_keys = [
            ('module1', 'module.idw', 'module.idw.tooltip'),
            ('module2', 'module.elevation', 'module.elevation.tooltip'),
            ('module3', 'module.time', 'module.time.tooltip'),
            ('module4', 'module.area', 'module.area.tooltip'),
            ('module5', 'module.coord', 'module.coord.tooltip'),
            ('module6', 'module.landslide', 'module.landslide.tooltip'),
        ]
        
        for module_id, name_key, tooltip_key in module_keys:
            btn = SidebarButton(f"  {tr(name_key)}", module_id)
            btn.setToolTip(tr(tooltip_key))
            btn.clicked.connect(lambda checked, mid=module_id: self._on_button_clicked(mid))
            self.buttons[module_id] = btn
            layout.addWidget(btn)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(line2)
        
        self.clear_cache_btn = QPushButton(tr("sidebar.clear_cache"))
        self.clear_cache_btn.setMinimumHeight(40)
        self.clear_cache_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_cache_btn.setStyleSheet("""
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
        self.clear_cache_btn.clicked.connect(self.clear_cache_requested.emit)
        layout.addWidget(self.clear_cache_btn)
        
        self.version_label = QLabel(tr("app.version"))
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setStyleSheet("color: #999999; padding: 10px;")
        layout.addWidget(self.version_label)
        
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
