"""
滑坡监测模块UI
仅考虑XY二维坐标，不考虑Z坐标
"""

import os
import numpy as np
import pandas as pd
from typing import Optional, List

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox,
    QComboBox, QGroupBox, QSpinBox, QFileDialog, QPushButton
)
from PyQt6.QtCore import Qt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_module_widget import BaseModuleWidget
from module6_Slide.deformation_analyzer import DeformationAnalyzer, DeformationResult
from common.exporter import Exporter


class LandslideInputDialog(QDialog):
    """滑坡监测数据输入对话框 - 仅XY二维"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入监测数据")
        self.setMinimumSize(600, 450)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel("请输入监测点数据：点号(ID)、期号(Epoch)、X坐标、Y坐标\n(注：本模块仅考虑XY二维坐标，不考虑Z坐标)")
        info_label.setStyleSheet("color: #666;")
        layout.addWidget(info_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["点号ID", "期号Epoch", "X坐标", "Y坐标"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(12)
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
        self.table.insertRow(self.table.rowCount())
    
    def _remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
    
    def get_data(self) -> Optional[pd.DataFrame]:
        data = []
        for row in range(self.table.rowCount()):
            try:
                id_item = self.table.item(row, 0)
                epoch_item = self.table.item(row, 1)
                x_item = self.table.item(row, 2)
                y_item = self.table.item(row, 3)
                
                if all([id_item, epoch_item, x_item, y_item]):
                    data.append({
                        'ID': id_item.text(),
                        'Epoch': int(float(epoch_item.text())),
                        'X': float(x_item.text()),
                        'Y': float(y_item.text())
                    })
            except (ValueError, AttributeError):
                continue
        
        if len(data) < 2:
            QMessageBox.warning(self, "数据不足", "请至少输入2条监测数据！")
            return None
        
        df = pd.DataFrame(data)
        if df['ID'].nunique() < 1:
            QMessageBox.warning(self, "数据无效", "至少需要1个监测点的数据！")
            return None
        
        return df


class LandslideMonitorWidget(BaseModuleWidget):
    """滑坡监测模块 - 仅XY二维分析"""
    
    def __init__(self, parent=None):
        self.analyzer: Optional[DeformationAnalyzer] = None
        self.deformation_result: Optional[DeformationResult] = None
        super().__init__("滑坡监测", parent)
    
    def init_ui(self):
        # 参数设置
        params_layout = QHBoxLayout()
        self.input_layout.addLayout(params_layout)
        
        params_layout.addWidget(QLabel("速度阈值(mm/期):"))
        self.velocity_threshold = QDoubleSpinBox()
        self.velocity_threshold.setRange(0.1, 100.0)
        self.velocity_threshold.setValue(5.0)
        self.velocity_threshold.setSingleStep(0.5)
        params_layout.addWidget(self.velocity_threshold)
        
        params_layout.addSpacing(20)
        
        params_layout.addWidget(QLabel("应变阈值:"))
        self.strain_threshold = QDoubleSpinBox()
        self.strain_threshold.setRange(0.0001, 1.0)
        self.strain_threshold.setValue(0.001)
        self.strain_threshold.setSingleStep(0.0001)
        self.strain_threshold.setDecimals(4)
        params_layout.addWidget(self.strain_threshold)
        
        params_layout.addStretch()
        
        # 说明标签
        info_label = QLabel("注：本模块仅考虑XY二维坐标进行变形分析，不考虑Z坐标")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        self.input_layout.addWidget(info_label)
        
        # 数据表
        self.data_table = QTableWidget()
        self.data_table.setMinimumHeight(150)
        self.input_layout.addWidget(self.data_table)
        
        self.info_label = QLabel("请导入监测数据或手动输入，每个监测点需要至少2期数据")
        self.info_label.setStyleSheet("color: #666666; padding: 5px;")
        self.input_layout.addWidget(self.info_label)

    def import_file(self):
        """导入文本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入监测数据文件", "", 
            "文本文件 (*.txt);;CSV文件 (*.csv);;所有文件 (*.*)"
        )
        if file_path:
            self._load_file_data(file_path)

    def _load_file_data(self, file_path: str):
        """从文件路径加载数据"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                idx = 0
                while idx < len(lines):
                    line = lines[idx].strip()
                    if not line or line.startswith('#'):
                        idx += 1
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            point_id = parts[0]
                            epochs = int(parts[1])
                            idx += 1
                            for j in range(epochs):
                                if idx >= len(lines):
                                    break
                                epoch_parts = lines[idx].strip().split()
                                if len(epoch_parts) >= 3:
                                    data.append({
                                        'ID': point_id,
                                        'Epoch': int(epoch_parts[0]),
                                        'X': float(epoch_parts[1]),
                                        'Y': float(epoch_parts[2])
                                    })
                                idx += 1
                        except:
                            idx += 1
                    else:
                        idx += 1
            
            if data:
                df = pd.DataFrame(data)
                self._raw_data = df
                self._display_data()
                n_points = df['ID'].nunique()
                n_epochs = df['Epoch'].nunique()
                self.info_label.setText(f"已加载 {n_points} 个监测点，{n_epochs} 期数据 (仅XY)")
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
            required_cols = ['ID', 'Epoch', 'X', 'Y']
            if not all(col in df.columns for col in required_cols):
                self.show_error("Excel文件必须包含ID、Epoch、X、Y列！")
                return
            
            self._raw_data = df[required_cols].copy()
            self._display_data()
            n_points = df['ID'].nunique()
            n_epochs = df['Epoch'].nunique()
            self.info_label.setText(f"已加载 {n_points} 个监测点，{n_epochs} 期数据 (仅XY)")
        except Exception as e:
            self.show_error(f"导入失败: {str(e)}")

    def manual_input(self):
        dialog = LandslideInputDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data is not None:
                self._raw_data = data
                self._display_data()
                n_points = data['ID'].nunique()
                self.info_label.setText(f"已输入 {n_points} 个监测点的数据 (仅XY)")

    def calculate(self):
        if self._raw_data is None or len(self._raw_data) == 0:
            self.show_error("请先导入或输入监测数据！")
            return
        
        try:
            self.analyzer = DeformationAnalyzer()
            self.deformation_result = self.analyzer.analyze(self._raw_data)
            self._result_data = self.deformation_result
            
            # 显示结果
            self._display_results()
            
            self.show_info("二维变形分析完成")
            
            # 绘制图形
            self.plot_result()
            
            # 启用导出按钮
            self.btn_export_md.setEnabled(True)
            self.btn_export_csv.setEnabled(True)
            self.btn_export_image.setEnabled(True)
            
            if self.deformation_result.warnings:
                warning_text = "\n".join(self.deformation_result.warnings)
                QMessageBox.warning(self, "预警信息", warning_text)
            
        except Exception as e:
            self.show_error(f"分析失败: {str(e)}")

    def _display_results(self):
        """显示分析结果"""
        if not self.deformation_result:
            return
        
        result = self.deformation_result
        lines = []
        
        lines.append("=" * 70)
        lines.append("滑坡监测分析报告 (仅XY二维坐标)")
        lines.append("=" * 70)
        lines.append("")
        
        # 变形速度
        lines.append("一、各监测点变形速度")
        lines.append("-" * 70)
        lines.append(f"{'点号':<10} {'变形速度(mm/期)':>20} {'状态':>15}")
        lines.append("-" * 70)
        
        threshold = self.velocity_threshold.value()
        for pid, v in sorted(result.velocities.items()):
            v_mm = v * 1000
            status = "异常" if v_mm > threshold else "正常"
            lines.append(f"{pid:<10} {v_mm:>20.3f} {status:>15}")
        
        lines.append("-" * 70)
        lines.append(f"最大速度点: {result.max_velocity_point}")
        lines.append("")
        
        # 相对应变
        lines.append("二、各监测点相对应变")
        lines.append("-" * 70)
        lines.append(f"{'点号':<10} {'相对应变':>20} {'状态':>15}")
        lines.append("-" * 70)
        
        strain_threshold = self.strain_threshold.value()
        for pid, e in sorted(result.strains.items()):
            status = "异常" if abs(e) > strain_threshold else "正常"
            lines.append(f"{pid:<10} {e:>20.6f} {status:>15}")
        
        lines.append("-" * 70)
        lines.append(f"最大应变点: {result.max_strain_point}")
        lines.append("")
        
        # 预警信息
        if result.warnings:
            lines.append("三、预警信息")
            lines.append("-" * 70)
            for w in result.warnings:
                lines.append(f"  ⚠️ {w}")
            lines.append("")
        
        # 结论
        lines.append("四、分析结论")
        lines.append("-" * 70)
        
        if result.warnings:
            lines.append("  存在异常监测点，建议加强监测频率并采取相应措施。")
        else:
            lines.append("  所有监测点变形均在正常范围内。")
        
        lines.append("")
        lines.append("=" * 70)
        
        self.result_text.setText("\n".join(lines))

    def export(self):
        """导出滑坡监测结果"""
        if not self.deformation_result:
            self.show_error("暂无结果可导出！")
            return
        
        try:
            export_dir = QFileDialog.getExistingDirectory(
                self, "选择导出目录", "reports"
            )
            
            if not export_dir:
                return
            
            # 准备导出数据
            deformation_results = []
            strain_results = []
            
            # 变形速度数据
            for point_id, velocity in self.deformation_result.velocities.items():
                deformation_results.append({
                    '监测点编号': point_id,
                    '变形速度(mm/期)': round(velocity * 1000, 3),
                    '状态': "异常" if velocity * 1000 > self.velocity_threshold.value() else "正常"
                })
            
            # 应变数据
            for point_id, strain in self.deformation_result.strains.items():
                strain_results.append({
                    '监测点编号': point_id,
                    '相对应变': round(strain, 6),
                    '状态': "异常" if abs(strain) > self.strain_threshold.value() else "正常"
                })
            
            # 导出结果
            exporter = Exporter(export_dir)
            results = exporter.export_landslide(deformation_results, strain_results, export_dir)
            
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
        """获取滑坡监测结果用于导出"""
        if self.deformation_result is None:
            return None
        
        export_data = []
        
        # 获取所有监测点
        all_points = set(self.deformation_result.velocities.keys()) | set(self.deformation_result.strains.keys())
        
        velocity_threshold = self.velocity_threshold.value()
        strain_threshold = self.strain_threshold.value()
        
        for point_id in sorted(all_points):
            velocity = self.deformation_result.velocities.get(point_id, 0) * 1000  # 转为mm
            strain = self.deformation_result.strains.get(point_id, 0)
            
            export_data.append({
                '监测点编号': point_id,
                '变形速度(mm/期)': round(velocity, 3),
                '速度状态': '异常' if velocity > velocity_threshold else '正常',
                '相对应变': round(strain, 6),
                '应变状态': '异常' if abs(strain) > strain_threshold else '正常',
                '是否最大速度点': '是' if point_id == self.deformation_result.max_velocity_point else '否',
                '是否最大应变点': '是' if point_id == self.deformation_result.max_strain_point else '否'
            })
        
        return pd.DataFrame(export_data)

    def plot_result(self):
        """绘制结果图表"""
        self.clear_figure()
        
        if self.deformation_result is None or not self.deformation_result.velocities:
            return
        
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        points = list(self.deformation_result.velocities.keys())
        velocities = [v * 1000 for v in self.deformation_result.velocities.values()]
        strains = [abs(e) for e in self.deformation_result.strains.values()]
        
        # 速度图
        colors = []
        threshold = self.velocity_threshold.value()
        for v in velocities:
            if v > threshold:
                colors.append('#F44336')  # 红色-异常
            else:
                colors.append('#4CAF50')  # 绿色-正常
        
        bars1 = ax1.bar(points, velocities, color=colors)
        ax1.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'阈值 ({threshold} mm/期)')
        ax1.set_ylabel('速度 (mm/期)')
        ax1.set_title('各监测点位移速度 (XY二维)')
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 应变图
        strain_threshold = self.strain_threshold.value()
        colors2 = []
        for s in strains:
            if s > strain_threshold:
                colors2.append('#F44336')
            else:
                colors2.append('#2196F3')
        
        bars2 = ax2.bar(points, strains, color=colors2)
        ax2.axhline(y=strain_threshold, color='red', linestyle='--', linewidth=2, 
                   label=f'阈值 ({strain_threshold})')
        ax2.set_ylabel('相对应变')
        ax2.set_title('各监测点相对应变 (XY二维)')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        self.figure.tight_layout()
        self.canvas.draw()

    def _display_data(self):
        if self._raw_data is None:
            return
        
        self.data_table.setRowCount(len(self._raw_data))
        self.data_table.setColumnCount(4)
        self.data_table.setHorizontalHeaderLabels(['ID', 'Epoch', 'X', 'Y'])
        
        for i, (_, row) in enumerate(self._raw_data.iterrows()):
            self.data_table.setItem(i, 0, QTableWidgetItem(str(row['ID'])))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(row['Epoch'])))
            self.data_table.setItem(i, 2, QTableWidgetItem(f"{row['X']:.4f}"))
            self.data_table.setItem(i, 3, QTableWidgetItem(f"{row['Y']:.4f}"))
        
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def clear_data(self):
        """清空数据"""
        super().clear_data()
        self.deformation_result = None
        self.data_table.setRowCount(0)
        self.result_text.clear()
        self.info_label.setText("请导入监测数据或手动输入，每个监测点需要至少2期数据")
