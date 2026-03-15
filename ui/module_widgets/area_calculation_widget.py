"""
多边形面积计算模块UI
使用海伦公式计算6个固定三角形的面积
"""

import os
import numpy as np
import pandas as pd
from typing import Optional, List, Tuple

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QDialogButtonBox, QMessageBox, QCheckBox, QFileDialog, QPushButton,
    QTabWidget, QWidget, QGroupBox, QLineEdit
)
from PyQt6.QtCore import Qt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_module_widget import BaseModuleWidget
from module4_Area.heron_calculator import HeronCalculator, HeronAreaResult
from common.exporter import Exporter


class PolygonInputDialog(QDialog):
    """多边形顶点输入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入多边形顶点")
        self.setMinimumSize(500, 400)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel("请输入多边形顶点坐标（至少3个顶点）\n建议使用8个顶点以获得6个三角形")
        info_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["点号", "X坐标", "Y坐标"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(8)  # 默认8行
        
        # 预设点号
        for i in range(8):
            self.table.setItem(i, 0, QTableWidgetItem(chr(ord('A') + i)))
        
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        
        btn_add_row = QPushButton("添加行")
        btn_add_row.clicked.connect(self._add_row)
        btn_layout.addWidget(btn_add_row)
        
        btn_remove_row = QPushButton("删除选中行")
        btn_remove_row.clicked.connect(self._remove_row)
        btn_layout.addWidget(btn_remove_row)
        
        layout.addLayout(btn_layout)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(chr(ord('A') + row)))
    
    def _remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
    
    def get_points(self) -> Optional[Tuple[List[str], List[Tuple[float, float]]]]:
        names = []
        points = []
        
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            x_item = self.table.item(row, 1)
            y_item = self.table.item(row, 2)
            
            if x_item and y_item:
                try:
                    name = name_item.text() if name_item else chr(ord('A') + row)
                    x = float(x_item.text())
                    y = float(y_item.text())
                    names.append(name)
                    points.append((x, y))
                except ValueError:
                    continue
        
        if len(points) < 3:
            QMessageBox.warning(self, "数据不足", "多边形至少需要3个顶点！")
            return None
        
        return names, points


class AreaCalculationWidget(BaseModuleWidget):
    """多边形面积计算模块 - 海伦公式版本"""
    
    def __init__(self, parent=None):
        self.heron_result: Optional[HeronAreaResult] = None
        self.vertex_names: List[str] = []
        self.points: List[Tuple[float, float]] = []
        super().__init__("多边形面积计算", parent)
    
    def init_ui(self):
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 文件导入页
        self.file_tab = QWidget()
        self._init_file_tab()
        self.tab_widget.addTab(self.file_tab, "文件导入")
        
        # 手动输入页
        self.manual_tab = QWidget()
        self._init_manual_tab()
        self.tab_widget.addTab(self.manual_tab, "手动输入")
        
        self.input_layout.insertWidget(1, self.tab_widget)

    def _init_file_tab(self):
        """初始化文件导入页"""
        layout = QVBoxLayout(self.file_tab)
        
        # 文件选择
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        
        btn_layout = QHBoxLayout()
        self.btn_select_file = QPushButton("选择顶点数据文件")
        self.btn_select_file.clicked.connect(self._select_file)
        btn_layout.addWidget(self.btn_select_file)
        
        self.lbl_file_path = QLabel("未选择文件")
        self.lbl_file_path.setWordWrap(True)
        btn_layout.addWidget(self.lbl_file_path)
        btn_layout.addStretch()
        
        file_layout.addLayout(btn_layout)
        
        # 文件格式说明
        format_label = QLabel("文件格式：点号 X Y（空格分隔，每行一个顶点）")
        format_label.setStyleSheet("color: gray;")
        file_layout.addWidget(format_label)
        
        layout.addWidget(file_group)
        
        # 文件内容预览
        preview_group = QGroupBox("文件内容预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.file_preview = QTableWidget()
        self.file_preview.setColumnCount(3)
        self.file_preview.setHorizontalHeaderLabels(["点号", "X", "Y"])
        self.file_preview.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        preview_layout.addWidget(self.file_preview)
        
        layout.addWidget(preview_group)
        
        # 计算按钮
        self.btn_calc_file = QPushButton("计算面积")
        self.btn_calc_file.clicked.connect(self._calculate_from_file)
        self.btn_calc_file.setEnabled(False)
        layout.addWidget(self.btn_calc_file)
        
        layout.addStretch()

    def _init_manual_tab(self):
        """初始化手动输入页"""
        layout = QVBoxLayout(self.manual_tab)
        
        info_label = QLabel("手动输入多边形顶点坐标，将使用海伦公式计算6个三角形面积")
        info_label.setStyleSheet("color: #666;")
        layout.addWidget(info_label)
        
        # 顶点数据表
        self.data_table = QTableWidget()
        self.data_table.setMinimumHeight(200)
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["点号", "X", "Y"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.data_table)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.btn_add_row = QPushButton("添加行")
        self.btn_add_row.clicked.connect(self._add_table_row)
        btn_layout.addWidget(self.btn_add_row)
        
        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self._clear_table)
        btn_layout.addWidget(self.btn_clear)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 计算按钮
        self.btn_calc_manual = QPushButton("计算面积")
        self.btn_calc_manual.clicked.connect(self._calculate_manual)
        layout.addWidget(self.btn_calc_manual)
        
        # 初始化8行
        self._init_table_rows(8)
        
        layout.addStretch()

    def _init_table_rows(self, count: int):
        """初始化表格行"""
        self.data_table.setRowCount(count)
        for i in range(count):
            self.data_table.setItem(i, 0, QTableWidgetItem(chr(ord('A') + i)))

    def _add_table_row(self):
        """添加表格行"""
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        self.data_table.setItem(row, 0, QTableWidgetItem(chr(ord('A') + row)))

    def _clear_table(self):
        """清空表格"""
        self.data_table.clearContents()
        self._init_table_rows(8)

    def _select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择顶点数据文件", "", 
            "文本文件 (*.txt *.csv *.dat);;所有文件 (*.*)"
        )
        
        if file_path:
            self._current_file = file_path
            self.lbl_file_path.setText(file_path)
            
            # 读取并预览
            try:
                result, errors = HeronCalculator.calculate_from_file(file_path)
                
                # 显示在预览表中
                if result:
                    self.file_preview.setRowCount(result.vertex_count)
                    for i, (name, (x, y)) in enumerate(zip(
                        [t.vertex_a for t in result.triangles[:1]] + 
                        [t.vertex_b for t in result.triangles] + 
                        [result.triangles[-1].vertex_c if result.triangles else ''],
                        [(0,0)] * result.vertex_count  # 这里简化处理
                    )):
                        pass  # 简化处理
                
                # 重新读取原始数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                preview_data = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 3:
                            preview_data.append((parts[0], parts[1], parts[2]))
                
                self.file_preview.setRowCount(len(preview_data))
                for i, (name, x, y) in enumerate(preview_data):
                    self.file_preview.setItem(i, 0, QTableWidgetItem(name))
                    self.file_preview.setItem(i, 1, QTableWidgetItem(x))
                    self.file_preview.setItem(i, 2, QTableWidgetItem(y))
                
                self.btn_calc_file.setEnabled(True)
                
            except Exception as e:
                self.show_error(f"无法读取文件: {str(e)}")
                self.btn_calc_file.setEnabled(False)

    def _calculate_from_file(self):
        """从文件计算"""
        if not hasattr(self, '_current_file'):
            self.show_error("请先选择文件")
            return
        
        try:
            result, errors = HeronCalculator.calculate_from_file(self._current_file)
            
            if errors:
                for err in errors:
                    self.show_info(f"警告: {err}")
            
            if result is None:
                self.show_error("计算失败，请检查数据")
                return
            
            self.heron_result = result
            self._result_data = result
            
            # 显示结果
            output = HeronCalculator.format_output(result)
            self.result_text.setText(output)
            
            self.show_info(f"计算完成！总面积: {result.total_area:.4f} m²")
            
            # 绘制图形
            self.plot_result()
            
            # 启用导出
            self.btn_export_md.setEnabled(True)
            self.btn_export_csv.setEnabled(True)
            self.btn_export_image.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"计算失败: {str(e)}")

    def _calculate_manual(self):
        """手动计算"""
        names = []
        points = []
        
        for row in range(self.data_table.rowCount()):
            name_item = self.data_table.item(row, 0)
            x_item = self.data_table.item(row, 1)
            y_item = self.data_table.item(row, 2)
            
            if x_item and y_item and x_item.text() and y_item.text():
                try:
                    name = name_item.text() if name_item else chr(ord('A') + row)
                    x = float(x_item.text())
                    y = float(y_item.text())
                    names.append(name)
                    points.append((x, y))
                except ValueError:
                    continue
        
        if len(points) < 3:
            self.show_error("至少需要3个顶点")
            return
        
        try:
            result = HeronCalculator.calculate_from_vertices(points, names)
            self.heron_result = result
            self._result_data = result
            self.vertex_names = names
            self.points = points
            
            # 显示结果
            output = HeronCalculator.format_output(result)
            self.result_text.setText(output)
            
            self.show_info(f"计算完成！总面积: {result.total_area:.4f} m²")
            
            # 绘制图形
            self.plot_result()
            
            # 启用导出
            self.btn_export_md.setEnabled(True)
            self.btn_export_csv.setEnabled(True)
            self.btn_export_image.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"计算失败: {str(e)}")

    def import_file(self):
        """导入文件"""
        self.tab_widget.setCurrentIndex(0)
        self._select_file()

    def import_excel(self):
        """导入Excel"""
        self.show_info("面积计算模块支持文本文件导入，请使用文件导入功能")

    def _load_file_data(self, file_path: str):
        """加载文件数据"""
        self.tab_widget.setCurrentIndex(0)
        self._current_file = file_path
        self.lbl_file_path.setText(file_path)
        self._calculate_from_file()

    def _load_excel_data(self, file_path: str):
        """加载Excel数据"""
        self.show_info("面积计算模块不支持Excel导入")

    def manual_input(self):
        """手动输入"""
        self.tab_widget.setCurrentIndex(1)

    def calculate(self):
        """计算"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:
            self._calculate_from_file()
        else:
            self._calculate_manual()

    def export(self):
        """导出结果"""
        if not self.heron_result:
            self.show_error("暂无结果可导出")
            return
        
        try:
            export_dir = QFileDialog.getExistingDirectory(
                self, "选择导出目录", "reports"
            )
            
            if not export_dir:
                return
            
            # 准备三角形数据
            triangle_results = []
            for tri in self.heron_result.triangles:
                triangle_results.append({
                    'index': tri.index,
                    'vertices': f"{tri.vertex_a}-{tri.vertex_b}-{tri.vertex_c}",
                    'side1': tri.side_a,
                    'side2': tri.side_b,
                    'side3': tri.side_c,
                    'area': tri.area
                })
            
            # 导出
            exporter = Exporter(export_dir)
            export_result = exporter.export_area(
                triangle_results, 
                self.heron_result.total_area, 
                export_dir
            )
            
            if export_result.success:
                self.show_info(f"导出成功: {export_result.file_path}")
            else:
                self.show_error(f"导出失败: {export_result.message}")
                
        except Exception as e:
            self.show_error(f"导出失败: {str(e)}")

    def get_result_text(self) -> str:
        if self.heron_result is None:
            return "无结果"
        return HeronCalculator.format_output(self.heron_result)
    
    def _get_export_data(self) -> pd.DataFrame:
        """获取面积计算结果用于导出"""
        if self.heron_result is None:
            return None
        
        export_data = []
        
        # 导出每个三角形的结果
        for tri in self.heron_result.triangles:
            export_data.append({
                '三角形编号': tri.index,
                '顶点': f"{tri.vertex_a}-{tri.vertex_b}-{tri.vertex_c}",
                '边a(m)': round(tri.side_a, 4),
                '边b(m)': round(tri.side_b, 4),
                '边c(m)': round(tri.side_c, 4),
                '面积(m²)': round(tri.area, 4)
            })
        
        # 添加总面积行
        export_data.append({
            '三角形编号': '合计',
            '顶点': '',
            '边a(m)': '',
            '边b(m)': '',
            '边c(m)': '',
            '面积(m²)': round(self.heron_result.total_area, 4)
        })
        
        return pd.DataFrame(export_data)

    def plot_result(self):
        """绘制结果"""
        self.clear_figure()
        
        if self.heron_result is None or not self.points:
            return
        
        ax = self.figure.add_subplot(111)
        
        # 绘制多边形
        vertices = self.points + [self.points[0]]
        x_coords = [v[0] for v in vertices]
        y_coords = [v[1] for v in vertices]
        
        ax.fill(x_coords, y_coords, alpha=0.3, color='#2196F3', label='多边形区域')
        ax.plot(x_coords, y_coords, 'b-', linewidth=2, marker='o', markersize=8)
        
        # 标注顶点
        names = self.vertex_names if self.vertex_names else [chr(ord('A') + i) for i in range(len(self.points))]
        for i, (x, y) in enumerate(self.points):
            name = names[i] if i < len(names) else f'P{i+1}'
            ax.annotate(name, (x, y), textcoords="offset points", 
                       xytext=(5, 5), fontsize=10, fontweight='bold')
        
        # 绘制三角形分割线
        if len(self.points) >= 3:
            for tri in self.heron_result.triangles:
                # 找到三角形顶点索引
                try:
                    idx_a = names.index(tri.vertex_a)
                    idx_b = names.index(tri.vertex_b)
                    idx_c = names.index(tri.vertex_c)
                    
                    # 绘制虚线
                    ax.plot([self.points[idx_a][0], self.points[idx_c][0]], 
                           [self.points[idx_a][1], self.points[idx_c][1]], 
                           'r--', linewidth=1, alpha=0.5)
                except (ValueError, IndexError):
                    pass
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title(f'多边形海伦公式分割 (总面积: {self.heron_result.total_area:.2f} m²)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        self.figure.tight_layout()
        self.canvas.draw()

    def clear_data(self):
        """清空数据"""
        super().clear_data()
        self.heron_result = None
        self.vertex_names = []
        self.points = []
        self.result_text.clear()
        self._clear_table()
