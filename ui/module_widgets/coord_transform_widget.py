"""
坐标转换模块UI
支持克拉索夫斯基椭球、度分秒格式输出、B点站心参考
"""

import os
import math
import numpy as np
import pandas as pd
from typing import Optional, List, Tuple

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
    QComboBox, QTabWidget, QWidget, QGroupBox, QRadioButton,
    QButtonGroup, QSpinBox, QFileDialog, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_module_widget import BaseModuleWidget
from module5_Cord.blh_converter import BLHConverter, BLHCoordinate
from module5_Cord.neu_converter import NEUConverter, NEUCoordinate
from module5_Cord.coord_transformer import CoordinateTransformer
from module5_Cord.dms_converter import DMSConverter
from common.ellipsoid_manager import EllipsoidManager, Ellipsoid
from common.exporter import Exporter


class CoordInputDialog(QDialog):
    """坐标输入对话框"""
    
    def __init__(self, mode: str = 'xyz', parent=None):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle("输入坐标数据")
        self.setMinimumSize(600, 400)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        if self.mode == 'xyz':
            self.table = QTableWidget()
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["点号", "X坐标", "Y坐标", "Z坐标"])
        elif self.mode == 'blh':
            self.table = QTableWidget()
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["点号", "纬度B(度)", "经度L(度)", "大地高H(m)"])
        else:
            self.table = QTableWidget()
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["点号", "X", "Y", "Z"])
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(6)  # 默认6行，对应A-F点
        
        # 预设点号
        for i in range(6):
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
    
    def get_data(self) -> Optional[pd.DataFrame]:
        data = []
        for row in range(self.table.rowCount()):
            row_data = {}
            try:
                name_item = self.table.item(row, 0)
                row_data['ID'] = name_item.text() if name_item else chr(ord('A') + row)
                
                if self.mode == 'xyz':
                    row_data['X'] = float(self.table.item(row, 1).text())
                    row_data['Y'] = float(self.table.item(row, 2).text())
                    row_data['Z'] = float(self.table.item(row, 3).text())
                elif self.mode == 'blh':
                    row_data['B'] = float(self.table.item(row, 1).text())
                    row_data['L'] = float(self.table.item(row, 2).text())
                    row_data['H'] = float(self.table.item(row, 3).text())
                else:
                    row_data['X'] = float(self.table.item(row, 1).text())
                    row_data['Y'] = float(self.table.item(row, 2).text())
                    row_data['Z'] = float(self.table.item(row, 3).text())
                data.append(row_data)
            except (ValueError, AttributeError):
                continue
        
        if len(data) == 0:
            QMessageBox.warning(self, "数据不足", "请至少输入一个坐标点！")
            return None
        
        return pd.DataFrame(data)


class CoordTransformWidget(BaseModuleWidget):
    """坐标转换模块 - 支持克拉索夫斯基椭球、度分秒格式、B点站心"""
    
    def __init__(self, parent=None):
        self.transformer: Optional[CoordinateTransformer] = None
        self.ellipsoid: Optional[Ellipsoid] = None
        self.conversion_results: Optional[List] = None
        self.conversion_mode: str = 'xyz_to_blh'
        super().__init__("坐标转换", parent)
    
    def init_ui(self):
        # 转换模式选择
        mode_group = QGroupBox("转换模式")
        mode_layout = QHBoxLayout(mode_group)
        self.input_layout.addWidget(mode_group)
        
        self.mode_group = QButtonGroup(self)
        
        modes = [
            ('xyz_to_blh', 'XYZ → BLH'),
            ('blh_to_xyz', 'BLH → XYZ'),
            ('xyz_to_neu', 'XYZ → NEU (B点参考)'),
        ]
        
        for i, (mode_id, mode_name) in enumerate(modes):
            radio = QRadioButton(mode_name)
            self.mode_group.addButton(radio, i)
            mode_layout.addWidget(radio)
            if i == 0:
                radio.setChecked(True)
        
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        
        # 参数设置
        params_layout = QHBoxLayout()
        self.input_layout.addLayout(params_layout)
        
        params_layout.addWidget(QLabel("椭球参数:"))
        self.ellipsoid_combo = QComboBox()
        self.ellipsoid_combo.addItems(['WGS84', 'CGCS2000', 'Krassovsky'])
        params_layout.addWidget(self.ellipsoid_combo)
        
        # 度分秒格式选项
        self.dms_check = QCheckBox("度分秒格式输出")
        self.dms_check.setChecked(True)
        params_layout.addWidget(self.dms_check)
        
        params_layout.addStretch()
        
        # 数据表
        self.data_table = QTableWidget()
        self.data_table.setMinimumHeight(150)
        self.input_layout.addWidget(self.data_table)
        
        self.info_label = QLabel("请选择转换模式并导入或输入坐标数据")
        self.info_label.setStyleSheet("color: #666666; padding: 5px;")
        self.input_layout.addWidget(self.info_label)
        
        self._update_table_headers()
    
    def _on_mode_changed(self, button):
        idx = self.mode_group.checkedId()
        modes = ['xyz_to_blh', 'blh_to_xyz', 'xyz_to_neu']
        self.conversion_mode = modes[idx]
        self._update_table_headers()
    
    def _update_table_headers(self):
        if self.conversion_mode in ['xyz_to_blh', 'xyz_to_neu']:
            self.data_table.setColumnCount(4)
            self.data_table.setHorizontalHeaderLabels(['点号', 'X', 'Y', 'Z'])
        else:
            self.data_table.setColumnCount(4)
            self.data_table.setHorizontalHeaderLabels(['点号', 'B(度)', 'L(度)', 'H(m)'])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def import_file(self):
        """导入文本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入坐标文件", "", 
            "文本文件 (*.txt);;CSV文件 (*.csv);;所有文件 (*.*)"
        )
        if file_path:
            self._load_file_data(file_path)
    
    def _load_file_data(self, file_path: str):
        """从文件路径加载数据"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            data.append({
                                'ID': parts[0], 
                                'X': float(parts[1]), 
                                'Y': float(parts[2]), 
                                'Z': float(parts[3])
                            })
                        except:
                            pass
            
            if data:
                self._raw_data = pd.DataFrame(data)
                self._display_data()
                self.info_label.setText(f"已加载 {len(data)} 个坐标点")
            else:
                self.show_error("文件中没有有效数据")
                
        except Exception as e:
            self.show_error(f"导入失败: {str(e)}")
    
    def import_excel(self):
        """导入Excel文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入Excel文件", "", 
            "Excel文件 (*.xlsx *.xls);;所有文件 (*.*)"
        )
        if file_path:
            self._load_excel_data(file_path)
    
    def _load_excel_data(self, file_path: str):
        """从Excel文件路径加载数据"""
        try:
            df = pd.read_excel(file_path)
            if 'X' in df.columns and 'Y' in df.columns and 'Z' in df.columns:
                self._raw_data = df
                self._display_data()
                self.info_label.setText(f"已加载 {len(df)} 个坐标点")
            else:
                self.show_error("Excel文件必须包含X、Y、Z列")
        except Exception as e:
            self.show_error(f"导入失败: {str(e)}")
    
    def manual_input(self):
        mode_map = {
            'xyz_to_blh': 'xyz',
            'blh_to_xyz': 'blh',
            'xyz_to_neu': 'xyz'
        }
        dialog = CoordInputDialog(mode_map[self.conversion_mode], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data is not None:
                self._raw_data = data
                self._display_data()
                self.info_label.setText(f"已输入 {len(data)} 个坐标点")
    
    def calculate(self):
        if self._raw_data is None or len(self._raw_data) == 0:
            self.show_error("请先导入或输入坐标数据！")
            return
        
        try:
            manager = EllipsoidManager()
            ellipsoid_name = self.ellipsoid_combo.currentText()
            self.ellipsoid = manager.get_ellipsoid(ellipsoid_name)
            
            self.conversion_results = []
            
            if self.conversion_mode == 'xyz_to_blh':
                self._convert_xyz_to_blh()
            elif self.conversion_mode == 'blh_to_xyz':
                self._convert_blh_to_xyz()
            elif self.conversion_mode == 'xyz_to_neu':
                self._convert_xyz_to_neu()
            
            self._result_data = self.conversion_results
            self._display_results()
            self.show_info("转换完成")
            
            # 绘制图形
            self.plot_result()
            
            # 启用导出按钮
            self.btn_export_md.setEnabled(True)
            self.btn_export_csv.setEnabled(True)
            self.btn_export_image.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"转换失败: {str(e)}")
    
    def _convert_xyz_to_blh(self):
        """XYZ转BLH，输出度分秒格式"""
        converter = BLHConverter(self.ellipsoid)
        use_dms = self.dms_check.isChecked()
        
        for _, row in self._raw_data.iterrows():
            result = converter.xyz_to_blh(row['X'], row['Y'], row['Z'])
            
            result_dict = {
                'ID': row.get('ID', ''),
                'X': row['X'], 
                'Y': row['Y'], 
                'Z': row['Z'],
                'B_deg': result.B_deg, 
                'L_deg': result.L_deg, 
                'H': result.H
            }
            
            # 添加度分秒格式
            if use_dms:
                result_dict['B_dms'] = DMSConverter.format_blh_dms(result.B_deg, 0, 0).split(',')[0]
                result_dict['L_dms'] = DMSConverter.format_blh_dms(0, result.L_deg, 0).split(',')[1]
            
            self.conversion_results.append(result_dict)
    
    def _convert_blh_to_xyz(self):
        """BLH转XYZ"""
        converter = BLHConverter(self.ellipsoid)
        
        for _, row in self._raw_data.iterrows():
            B_rad = math.radians(row['B'])
            L_rad = math.radians(row['L'])
            X, Y, Z = converter.blh_to_xyz(B_rad, L_rad, row['H'])
            self.conversion_results.append({
                'ID': row.get('ID', ''),
                'B_deg': row['B'], 
                'L_deg': row['L'], 
                'H': row['H'],
                'X': X, 
                'Y': Y, 
                'Z': Z
            })
    
    def _convert_xyz_to_neu(self):
        """XYZ转NEU，以B点为参考站"""
        converter = NEUConverter(self.ellipsoid)
        
        # 查找B点作为参考站
        b_point = None
        for _, row in self._raw_data.iterrows():
            if row.get('ID', '').upper() == 'B':
                b_point = (row['X'], row['Y'], row['Z'])
                break
        
        # 如果没有B点，使用第一个点作为参考
        if b_point is None:
            first_row = self._raw_data.iloc[0]
            b_point = (first_row['X'], first_row['Y'], first_row['Z'])
            self.show_info("未找到B点，使用第一个点作为参考站")
        
        X0, Y0, Z0 = b_point
        
        for _, row in self._raw_data.iterrows():
            neu = converter.xyz_to_neu(row['X'], row['Y'], row['Z'], X0, Y0, Z0)
            self.conversion_results.append({
                'ID': row.get('ID', ''),
                'X': row['X'], 
                'Y': row['Y'], 
                'Z': row['Z'],
                'Ref_X': X0,
                'Ref_Y': Y0,
                'Ref_Z': Z0,
                'N': neu.N, 
                'E': neu.E, 
                'U': neu.U
            })
    
    def _display_results(self):
        """显示转换结果"""
        lines = []
        lines.append("=" * 70)
        
        if self.conversion_mode == 'xyz_to_blh':
            lines.append("XYZ → BLH 转换结果")
            lines.append(f"椭球: {self.ellipsoid.name}")
            lines.append("=" * 70)
            lines.append("")
            
            use_dms = self.dms_check.isChecked()
            
            for r in self.conversion_results:
                lines.append(f"点号: {r.get('ID', '')}")
                lines.append(f"  XYZ: ({r['X']:.4f}, {r['Y']:.4f}, {r['Z']:.4f})")
                
                if use_dms and 'B_dms' in r:
                    lines.append(f"  BLH: {r['B_dms']}, {r['L_dms']}, H={r['H']:.3f}m")
                else:
                    lines.append(f"  BLH: B={r['B_deg']:.6f}°, L={r['L_deg']:.6f}°, H={r['H']:.3f}m")
                lines.append("")
                
        elif self.conversion_mode == 'blh_to_xyz':
            lines.append("BLH → XYZ 转换结果")
            lines.append(f"椭球: {self.ellipsoid.name}")
            lines.append("=" * 70)
            lines.append("")
            
            for r in self.conversion_results:
                lines.append(f"点号: {r.get('ID', '')}")
                lines.append(f"  BLH: B={r['B_deg']:.6f}°, L={r['L_deg']:.6f}°, H={r['H']:.3f}m")
                lines.append(f"  XYZ: ({r['X']:.4f}, {r['Y']:.4f}, {r['Z']:.4f})")
                lines.append("")
                
        elif self.conversion_mode == 'xyz_to_neu':
            lines.append("XYZ → NEU 转换结果 (B点站心坐标系)")
            lines.append(f"椭球: {self.ellipsoid.name}")
            lines.append("=" * 70)
            lines.append("")
            
            # 显示参考站信息
            if self.conversion_results:
                ref = self.conversion_results[0]
                lines.append(f"参考站(B点): ({ref['Ref_X']:.4f}, {ref['Ref_Y']:.4f}, {ref['Ref_Z']:.4f})")
                lines.append("")
            
            for r in self.conversion_results:
                lines.append(f"点号: {r.get('ID', '')}")
                lines.append(f"  XYZ: ({r['X']:.4f}, {r['Y']:.4f}, {r['Z']:.4f})")
                lines.append(f"  NEU: N={r['N']:.4f}m, E={r['E']:.4f}m, U={r['U']:.4f}m")
                lines.append("")
        
        lines.append("=" * 70)
        self.result_text.setText("\n".join(lines))
    
    def export(self):
        """导出坐标转换结果"""
        if not self.conversion_results:
            self.show_error("暂无结果可导出！")
            return
        
        try:
            export_dir = QFileDialog.getExistingDirectory(
                self, "选择导出目录", "reports"
            )
            
            if not export_dir:
                return
            
            # 准备导出数据
            blh_results = []
            neu_results = []
            
            if self.conversion_mode == 'xyz_to_blh':
                for result in self.conversion_results:
                    use_dms = self.dms_check.isChecked()
                    if use_dms and 'B_dms' in result:
                        blh_results.append({
                            '点号': result.get('ID', ''),
                            '椭球类型': self.ellipsoid.name,
                            '大地纬度(B)': result['B_dms'],
                            '大地经度(L)': result['L_dms'],
                            '大地高(H)(m)': round(result['H'], 4)
                        })
                    else:
                        blh_results.append({
                            '点号': result.get('ID', ''),
                            '椭球类型': self.ellipsoid.name,
                            '大地纬度(B)': f"{result['B_deg']:.6f}°",
                            '大地经度(L)': f"{result['L_deg']:.6f}°",
                            '大地高(H)(m)': round(result['H'], 4)
                        })
                        
            elif self.conversion_mode == 'xyz_to_neu':
                for result in self.conversion_results:
                    neu_results.append({
                        '点号': result.get('ID', ''),
                        '北坐标N(m)': round(result['N'], 4),
                        '东坐标E(m)': round(result['E'], 4),
                        '天坐标U(m)': round(result['U'], 4)
                    })
            
            # 导出结果
            exporter = Exporter(export_dir)
            results = exporter.export_coordinate(blh_results, neu_results, export_dir)
            
            success_count = sum(1 for r in results if r.success)
            if success_count > 0:
                self.show_info(f"导出成功！共导出 {success_count} 个文件")
            else:
                self.show_error("导出失败")
                
        except Exception as e:
            self.show_error(f"导出失败: {str(e)}")
    
    def get_result_text(self) -> str:
        return self.result_text.toPlainText()
    
    def _get_export_data(self) -> pd.DataFrame:
        """获取坐标转换结果用于导出"""
        if not self.conversion_results:
            return None
        
        export_data = []
        
        for r in self.conversion_results:
            row = {'点号': r.get('ID', '')}
            
            if self.conversion_mode == 'xyz_to_blh':
                # XYZ -> BLH
                row['X'] = r['X']
                row['Y'] = r['Y']
                row['Z'] = r['Z']
                if 'B_dms' in r:
                    row['纬度B(度分秒)'] = r['B_dms']
                    row['经度L(度分秒)'] = r['L_dms']
                else:
                    row['纬度B(度)'] = r['B_deg']
                    row['经度L(度)'] = r['L_deg']
                row['大地高H(m)'] = r['H']
                
            elif self.conversion_mode == 'blh_to_xyz':
                # BLH -> XYZ
                row['纬度B(度)'] = r['B_deg']
                row['经度L(度)'] = r['L_deg']
                row['大地高H(m)'] = r['H']
                row['X'] = r['X']
                row['Y'] = r['Y']
                row['Z'] = r['Z']
                
            elif self.conversion_mode == 'xyz_to_neu':
                # XYZ -> NEU
                row['X'] = r['X']
                row['Y'] = r['Y']
                row['Z'] = r['Z']
                row['参考站X'] = r['Ref_X']
                row['参考站Y'] = r['Ref_Y']
                row['参考站Z'] = r['Ref_Z']
                row['北向N(m)'] = r['N']
                row['东向E(m)'] = r['E']
                row['天向U(m)'] = r['U']
            
            export_data.append(row)
        
        return pd.DataFrame(export_data)
    
    def plot_result(self):
        """绘制结果图表"""
        self.clear_figure()
        
        if not self.conversion_results:
            return
        
        df = pd.DataFrame(self.conversion_results)
        
        if self.conversion_mode in ['xyz_to_blh', 'blh_to_xyz']:
            ax1 = self.figure.add_subplot(121)
            ax2 = self.figure.add_subplot(122)
            
            if 'B_deg' in df.columns and 'L_deg' in df.columns:
                ax1.scatter(df['L_deg'], df['B_deg'], c='#2196F3', s=50, alpha=0.7)
                ax1.set_xlabel('经度 L (度)')
                ax1.set_ylabel('纬度 B (度)')
                ax1.set_title('BLH坐标分布')
                ax1.grid(True, alpha=0.3)
            
            if 'H' in df.columns:
                ax2.hist(df['H'], bins=15, color='#4CAF50', edgecolor='white', alpha=0.7)
                ax2.set_xlabel('大地高 H (m)')
                ax2.set_ylabel('频数')
                ax2.set_title('高程分布')
                
        elif self.conversion_mode == 'xyz_to_neu':
            ax = self.figure.add_subplot(111)
            if 'N' in df.columns and 'E' in df.columns:
                # 标注点号
                for _, row in df.iterrows():
                    ax.scatter(row['E'], row['N'], c='#2196F3', s=50, alpha=0.7)
                    ax.annotate(row.get('ID', ''), (row['E'], row['N']), 
                               textcoords="offset points", xytext=(5, 5))
                
                ax.set_xlabel('东向 E (m)')
                ax.set_ylabel('北向 N (m)')
                ax.set_title('NEU坐标分布 (B点站心)')
                ax.grid(True, alpha=0.3)
                ax.axis('equal')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _display_data(self):
        if self._raw_data is None:
            return
        
        self._update_table_headers()
        self.data_table.setRowCount(len(self._raw_data))
        
        cols = ['ID', 'X', 'Y', 'Z'] if 'X' in self._raw_data.columns else ['ID', 'B', 'L', 'H']
        
        for i, row in self._raw_data.iterrows():
            for j, col in enumerate(cols):
                if col in row:
                    value = row[col]
                    if isinstance(value, (int, float)):
                        self.data_table.setItem(i, j, QTableWidgetItem(f"{value:.4f}"))
                    else:
                        self.data_table.setItem(i, j, QTableWidgetItem(str(value)))
    
    def clear_data(self):
        """清空数据"""
        super().clear_data()
        self.conversion_results = None
        self.data_table.setRowCount(0)
        self.result_text.clear()
        self.info_label.setText("请选择转换模式并导入或输入坐标数据")
