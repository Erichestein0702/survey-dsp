"""
Main Window
"""

import sys
import gc
from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, 
    QStatusBar, QMessageBox, QApplication, QMenu, QMenuBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QActionGroup

from .sidebar import SidebarWidget
from .module_widgets import (
    IDWWidget,
    ElevationFittingWidget,
    TimeSystemWidget,
    AreaCalculationWidget,
    CoordTransformWidget,
    LandslideMonitorWidget
)
from common.i18n import get_i18n_manager, tr


class MainWindow(QMainWindow):
    """Main Window"""
    
    def __init__(self):
        super().__init__()
        self.module_widgets: Dict[str, Optional[QWidget]] = {}
        self.i18n = get_i18n_manager()
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        self.setWindowTitle(tr("app.title"))
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
        
        self.statusBar().showMessage(tr("status.ready"))
        
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
    
    def _connect_signals(self):
        """Connect i18n signals"""
        self.i18n.language_changed.connect(self._on_language_changed)
    
    def _on_language_changed(self, lang_code: str):
        """Handle language change"""
        self._update_ui_texts()
        self.i18n.save_preference(lang_code)
    
    def _update_ui_texts(self):
        """Update all UI texts after language change"""
        self.setWindowTitle(tr("app.title"))
        self.statusBar().showMessage(tr("status.ready"))
        self._update_menu_texts()
        
        for widget in self.module_widgets.values():
            if hasattr(widget, 'update_texts'):
                widget.update_texts()
    
    def _create_module_widgets(self):
        """Create module widgets"""
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
        """Create menu bar"""
        menubar = self.menuBar()
        
        self.file_menu = menubar.addMenu(tr("menu.file"))
        
        self.exit_action = QAction(tr("menu.file.exit"), self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        self.settings_menu = menubar.addMenu(tr("menu.settings"))
        
        self.language_menu = self.settings_menu.addMenu(tr("menu.settings.language"))
        
        self.lang_action_group = QActionGroup(self)
        self.lang_action_group.setExclusive(True)
        
        for lang_code, lang_name in self.i18n.get_supported_languages().items():
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setChecked(lang_code == self.i18n.get_current_language())
            action.triggered.connect(lambda checked, lc=lang_code: self._change_language(lc))
            self.lang_action_group.addAction(action)
            self.language_menu.addAction(action)
        
        self.help_menu = menubar.addMenu(tr("menu.help"))
        
        self.about_action = QAction(tr("menu.help.about"), self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)
    
    def _update_menu_texts(self):
        """Update menu texts after language change"""
        self.file_menu.setTitle(tr("menu.file"))
        self.exit_action.setText(tr("menu.file.exit"))
        self.settings_menu.setTitle(tr("menu.settings"))
        self.language_menu.setTitle(tr("menu.settings.language"))
        self.help_menu.setTitle(tr("menu.help"))
        self.about_action.setText(tr("menu.help.about"))
        
        actions = self.lang_action_group.actions()
        lang_map = self.i18n.get_supported_languages()
        for action in actions:
            for lang_code, lang_name in lang_map.items():
                if action.text() in [lang_name, self._get_old_lang_name(lang_code)]:
                    action.setText(lang_name)
                    break
    
    def _get_old_lang_name(self, lang_code: str) -> str:
        """Get old language name for comparison"""
        old_names = {'en_US': 'English', 'zh_CN': '中文'}
        return old_names.get(lang_code, lang_code)
    
    def _change_language(self, lang_code: str):
        """Change application language"""
        self.i18n.set_language(lang_code)
    
    def switch_module(self, module_id: str):
        """Switch module"""
        if module_id in self.module_widgets:
            widget = self.module_widgets[module_id]
            self.content_stack.setCurrentWidget(widget)
            module_name = widget.module_name if hasattr(widget, 'module_name') else module_id
            self.statusBar().showMessage(tr("status.current_module").format(module_name))
        else:
            self.statusBar().showMessage(tr("status.module_developing").format(module_id))
    
    def clear_cache(self):
        """Clear cache"""
        reply = QMessageBox.question(
            self, tr("dialog.confirm_clear"), 
            tr("dialog.confirm_clear_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for widget in self.module_widgets.values():
                if hasattr(widget, 'clear_data'):
                    widget.clear_data()
            
            gc.collect()
            
            self.statusBar().showMessage(tr("status.cache_cleared"))
            QMessageBox.information(self, tr("dialog.clear_complete"), tr("dialog.clear_complete_message"))
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, tr("about.title"),
            f"""<h3>{tr('about.title')}</h3>
            <p>{tr('about.version')}</p>
            <p>{tr('about.description')}</p>
            <ul>
            <li>{tr('about.module1')}</li>
            <li>{tr('about.module2')}</li>
            <li>{tr('about.module3')}</li>
            <li>{tr('about.module4')}</li>
            <li>{tr('about.module5')}</li>
            <li>{tr('about.module6')}</li>
            </ul>
            <p>{tr('about.tech')}</p>
            """
        )
    
    def closeEvent(self, event):
        """Close event"""
        reply = QMessageBox.question(
            self, tr("dialog.confirm_exit"),
            tr("dialog.confirm_exit_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def run_app():
    """Run application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    i18n = get_i18n_manager()
    i18n.set_app(app)
    
    saved_lang = i18n.load_preference()
    i18n.set_language(saved_lang)
    
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
