"""
Base Module Widget
All functional module UIs inherit from this class
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
import pandas as pd

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QFileDialog, QMessageBox, QSplitter, QFrame,
    QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from common.i18n import get_i18n_manager, tr

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class BaseModuleWidget(QWidget):
    """Base Module Widget"""
    
    result_changed = pyqtSignal()
    
    def __init__(self, module_name: str, parent=None):
        super().__init__(parent)
        self.module_name = module_name
        self._result_data: Optional[Any] = None
        self._raw_data: Optional[pd.DataFrame] = None
        self.i18n = get_i18n_manager()
        self._init_base_ui()
        self.init_ui()
        self._connect_signals()
    
    def _connect_signals(self):
        self.i18n.language_changed.connect(self._on_language_changed)
    
    def _on_language_changed(self, lang_code: str):
        self.update_texts()
    
    def update_texts(self):
        self.input_group.setTitle(tr("label.input_data"))
        self.output_group.setTitle(tr("label.results"))
        self.btn_export_md.setText(tr("button.export_markdown"))
        self.btn_export_csv.setText(tr("button.export_csv"))
        self.btn_export_image.setText(tr("button.export_image"))
        self.btn_manual_input.setText(tr("button.manual_input"))
        self.btn_clear_data.setText(tr("button.clear"))
        self.btn_calculate.setText(tr("button.calculate"))
        self.btn_browse_file.setText(tr("button.browse"))
        self.btn_load_data.setText(tr("button.load"))
        self.file_type_label.setText(tr("label.file_type") + ":")
        self.file_path_label.setText(tr("label.file_path"))
        
        if self._raw_data is not None:
            self.data_info_label.setText(tr("message.file_loaded").format(len(self._raw_data)))
        else:
            self.data_info_label.setText(tr("message.no_data"))
    
    def _init_base_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        self.title_label = QLabel(self.module_name)
        self.title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #1976D2; padding: 5px;")
        self.main_layout.addWidget(self.title_label)
        
        self.content_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_layout.addWidget(self.content_splitter)
        
        self.input_group = QGroupBox(tr("label.input_data"))
        self.input_layout = QVBoxLayout(self.input_group)
        self.content_splitter.addWidget(self.input_group)
        
        self.output_group = QGroupBox(tr("label.results"))
        self.output_layout = QVBoxLayout(self.output_group)
        self.content_splitter.addWidget(self.output_group)
        
        self.export_layout = QHBoxLayout()
        self.output_layout.addLayout(self.export_layout)
        
        export_btn_style = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 2px solid #1976D2;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 120px;
                min-height: 35px;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
                border: 2px solid #9E9E9E;
            }
        """
        
        self.btn_export_md = QPushButton(tr("button.export_markdown"))
        self.btn_export_md.clicked.connect(lambda: self.export_result('md'))
        self.btn_export_md.setEnabled(False)
        self.btn_export_md.setStyleSheet(export_btn_style)
        self.export_layout.addWidget(self.btn_export_md)
        
        self.btn_export_csv = QPushButton(tr("button.export_csv"))
        self.btn_export_csv.clicked.connect(lambda: self.export_result('csv'))
        self.btn_export_csv.setEnabled(False)
        self.btn_export_csv.setStyleSheet(export_btn_style)
        self.export_layout.addWidget(self.btn_export_csv)
        
        self.btn_export_image = QPushButton(tr("button.export_image"))
        self.btn_export_image.clicked.connect(lambda: self.export_result('image'))
        self.btn_export_image.setEnabled(False)
        self.btn_export_image.setStyleSheet(export_btn_style)
        self.export_layout.addWidget(self.btn_export_image)
        
        self.output_tabs = QSplitter(Qt.Orientation.Horizontal)
        self.output_layout.addWidget(self.output_tabs)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 10))
        self.output_tabs.addWidget(self.result_text)
        
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.output_tabs.addWidget(self.canvas)
        
        file_input_layout = QHBoxLayout()
        
        self.file_type_label = QLabel(tr("label.file_type") + ":")
        file_input_layout.addWidget(self.file_type_label)
        
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItem("Text File", "txt")
        self.file_type_combo.addItem("CSV File", "csv")
        self.file_type_combo.addItem("Excel File", "xlsx")
        self.file_type_combo.setMinimumHeight(32)
        self.file_type_combo.setMinimumWidth(120)
        self.file_type_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #2196F3;
                border-radius: 4px;
                padding: 5px;
                background: white;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView {
                border: 1px solid #2196F3;
                selection-background-color: #E3F2FD;
            }
        """)
        self.file_type_combo.currentIndexChanged.connect(self._on_file_type_changed)
        file_input_layout.addWidget(self.file_type_combo)
        
        self.file_path_label = QLabel(tr("label.file_path"))
        file_input_layout.addWidget(self.file_path_label)
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText(tr("message.select_file"))
        self.file_path_edit.setMinimumHeight(32)
        file_input_layout.addWidget(self.file_path_edit, 1)
        
        self.btn_browse_file = QPushButton(tr("button.browse"))
        self.btn_browse_file.setMinimumHeight(32)
        self.btn_browse_file.setMinimumWidth(80)
        self.btn_browse_file.setMaximumWidth(100)
        self.btn_browse_file.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #455A64; }
        """)
        self.btn_browse_file.clicked.connect(self._browse_file)
        file_input_layout.addWidget(self.btn_browse_file)
        
        self.btn_load_data = QPushButton(tr("button.load"))
        self.btn_load_data.setMinimumHeight(32)
        self.btn_load_data.setMaximumWidth(80)
        self.btn_load_data.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.btn_load_data.clicked.connect(self._load_from_path)
        file_input_layout.addWidget(self.btn_load_data)
        
        self.input_layout.addLayout(file_input_layout)
        
        self.button_layout = QHBoxLayout()
        self.input_layout.addLayout(self.button_layout)
        
        self.btn_manual_input = QPushButton(tr("button.manual_input"))
        self.btn_manual_input.setMinimumHeight(35)
        self.btn_manual_input.clicked.connect(self.manual_input)
        self.button_layout.addWidget(self.btn_manual_input)
        
        self.btn_clear_data = QPushButton(tr("button.clear"))
        self.btn_clear_data.setMinimumHeight(35)
        self.btn_clear_data.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #E64A19; }
        """)
        self.btn_clear_data.clicked.connect(self.clear_data)
        self.button_layout.addWidget(self.btn_clear_data)
        
        self.btn_calculate = QPushButton(tr("button.calculate"))
        self.btn_calculate.setMinimumHeight(35)
        self.btn_calculate.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #43A047; }
        """)
        self.btn_calculate.clicked.connect(self.calculate)
        self.button_layout.addWidget(self.btn_calculate)
        
        self.data_info_label = QLabel(tr("message.no_data"))
        self.data_info_label.setStyleSheet("color: #666666; padding: 5px; font-style: italic;")
        self.input_layout.addWidget(self.data_info_label)
        
        self.data_preview_table = QTableWidget()
        self.data_preview_table.setMaximumHeight(200)
        self.data_preview_table.setAlternatingRowColors(True)
        self.data_preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.input_layout.addWidget(self.data_preview_table)
        
        self.content_splitter.setSizes([300, 400])
    
    def _on_file_type_changed(self, index):
        self.file_path_edit.setPlaceholderText(tr("message.select_file"))
    
    def _browse_file(self):
        file_type = self.file_type_combo.currentData()
        if file_type == 'txt':
            filter_str = "Text Files (*.txt);;All Files (*)"
        elif file_type == 'csv':
            filter_str = "CSV Files (*.csv);;All Files (*)"
        elif file_type == 'xlsx':
            filter_str = "Excel Files (*.xlsx *.xls);;All Files (*)"
        else:
            filter_str = "All Files (*)"
        
        file_path, _ = QFileDialog.getOpenFileName(self, tr("message.select_file"), "", filter_str)
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def _load_from_path(self):
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            self.show_error(tr("message.select_file"))
            return
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                self._load_excel_data(file_path)
            else:
                self._load_file_data(file_path)
        except Exception as e:
            self.show_error(f"{tr('message.invalid_data')}: {str(e)}")
    
    def _load_file_data(self, file_path: str):
        self.import_file()
    
    def _load_excel_data(self, file_path: str):
        self.import_excel()
    
    @abstractmethod
    def init_ui(self):
        pass
    
    @abstractmethod
    def import_file(self):
        pass
    
    @abstractmethod
    def import_excel(self):
        pass
    
    @abstractmethod
    def manual_input(self):
        pass
    
    @abstractmethod
    def calculate(self):
        pass
    
    @abstractmethod
    def get_result_text(self) -> str:
        pass
    
    @abstractmethod
    def plot_result(self):
        pass
    
    def _get_export_data(self) -> Optional[pd.DataFrame]:
        if isinstance(self._result_data, pd.DataFrame):
            return self._result_data
        elif self._raw_data is not None:
            return self._raw_data
        return None
    
    def clear_data(self):
        self._raw_data = None
        self._result_data = None
        self.file_path_edit.clear()
        self.data_preview_table.clear()
        self.data_preview_table.setRowCount(0)
        self.data_preview_table.setColumnCount(0)
        self.data_info_label.setText(tr("message.no_data"))
        self.result_text.clear()
        self.clear_figure()
        self.btn_export_md.setEnabled(False)
        self.btn_export_csv.setEnabled(False)
        self.btn_export_image.setEnabled(False)
        self.show_info(tr("message.no_data"))
    
    def update_data_preview(self, data: pd.DataFrame):
        if data is None or data.empty:
            return
        self._raw_data = data
        self.data_preview_table.clear()
        self.data_preview_table.setColumnCount(len(data.columns))
        self.data_preview_table.setRowCount(min(len(data), 50))
        self.data_preview_table.setHorizontalHeaderLabels(data.columns.tolist())
        for i in range(min(len(data), 50)):
            for j, col in enumerate(data.columns):
                item = QTableWidgetItem(str(data.iloc[i, j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.data_preview_table.setItem(i, j, item)
        self.data_info_label.setText(tr("message.file_loaded").format(len(data)))
    
    def export_result(self, format_type: str):
        if self._result_data is None:
            QMessageBox.warning(self, tr("dialog.confirm_clear"), tr("message.no_data"))
            return
        
        if format_type == 'md':
            file_path, _ = QFileDialog.getSaveFileName(self, tr("button.export_markdown"), "", "Markdown Files (*.md);;All Files (*)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.get_result_text())
                QMessageBox.information(self, tr("dialog.clear_complete"), f"{tr('message.export_success')}: {file_path}")
        elif format_type == 'csv':
            file_path, _ = QFileDialog.getSaveFileName(self, tr("button.export_csv"), "", "CSV Files (*.csv);;All Files (*)")
            if file_path:
                export_data = self._get_export_data()
                if export_data is not None:
                    export_data.to_csv(file_path, index=False, encoding='utf-8-sig')
                    QMessageBox.information(self, tr("dialog.clear_complete"), f"{tr('message.export_success')}: {file_path}")
                else:
                    QMessageBox.warning(self, tr("dialog.confirm_clear"), tr("message.no_data"))
        elif format_type == 'image':
            file_path, _ = QFileDialog.getSaveFileName(self, tr("button.export_image"), "", "PNG Images (*.png);;PDF Files (*.pdf);;All Files (*)")
            if file_path:
                self.figure.savefig(file_path, dpi=150, bbox_inches='tight')
                QMessageBox.information(self, tr("dialog.clear_complete"), f"{tr('message.export_success')}: {file_path}")
    
    def display_result(self):
        self.result_text.setPlainText(self.get_result_text())
        self.plot_result()
    
    def show_error(self, message: str):
        QMessageBox.critical(self, tr("dialog.confirm_clear"), message)
    
    def show_info(self, message: str):
        QMessageBox.information(self, tr("dialog.clear_complete"), message)
    
    def create_data_table(self, data: pd.DataFrame, max_rows: int = 100) -> QTableWidget:
        table = QTableWidget()
        display_data = data.head(max_rows) if len(data) > max_rows else data
        table.setColumnCount(len(display_data.columns))
        table.setRowCount(len(display_data))
        table.setHorizontalHeaderLabels(display_data.columns.tolist())
        for i, row in display_data.iterrows():
            for j, col in enumerate(display_data.columns):
                item = QTableWidgetItem(str(row[col]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(display_data.index.get_loc(i), j, item)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        return table
    
    def clear_figure(self):
        self.figure.clear()
        self.canvas.draw()
