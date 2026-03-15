"""
GPS高程拟合模块UI
支持三种方法对比分析：二次曲面拟合、多项式平面拟合、四参数曲面拟合
"""

import os
import numpy as np
import pandas as pd
from typing import Optional, List, Tuple

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QDialogButtonBox, QMessageBox, QCheckBox, QFileDialog, QPushButton,
    QGroupBox, QComboBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_module_widget import BaseModuleWidget
from module2_GPS_Elevation.elevation_fitter import ElevationFitter, FittingResult
from module2_GPS_Elevation.models import ModelResult
from common.exporter import Exporter


class ElevationInputDialog(QDialog):
    """高程数据输入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入高程拟合数据")
        self.setMinimumSize(600, 450)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel("请输入已知点数据：点号 X坐标 Y坐标 高程异常值(Zeta)")
        layout.addWidget(info_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["点号", "X坐标(m)", "Y坐标(m)", "高程异常Zeta(m)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(12)
        
        # 预设点号
        for i in range(12):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
        
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
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
    
    def _remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
    
    def get_data(self) -> Optional[pd.DataFrame]:
        data = []
        for row in range(self.table.rowCount()):
            try:
                id_item = self.table.item(row, 0)
                x_item = self.table.item(row, 1)
                y_item = self.table.item(row, 2)
                zeta_item = self.table.item(row, 3)
                
                if all([x_item, y_item, zeta_item]):
                    data.append({
                        'ID': id_item.text() if id_item else str(row + 1),
                        'X': float(x_item.text()),
                        'Y': float(y_item.text()),
                        'Zeta': float(zeta_item.text())
                    })
            except (ValueError, AttributeError):
                continue
        
        if len(data) < 12:
            QMessageBox.warning(self, "数据不足", "高程拟合至少需要12个已知点！")
            return None
        
        return pd.DataFrame(data)


class ElevationFittingWidget(BaseModuleWidget):
    """GPS高程拟合模块 - 三种方法对比分析"""
    
    def __init__(self, parent=None):
        self.fitter: Optional[ElevationFitter] = None
        self.fitting_result: Optional[FittingResult] = None
        self.X: Optional[np.ndarray] = None
        self.Y: Optional[np.ndarray] = None
        self.Zeta: Optional[np.ndarray] = None
        super().__init__("GPS高程拟合", parent)
    
    def init_ui(self):
        # 参数设置
        params_group = QGroupBox("拟合参数")
        params_layout = QHBoxLayout(params_group)
        
        params_layout.addWidget(QLabel("坐标中心化:"))
        self.center_check = QCheckBox("启用(推荐)")
        self.center_check.setChecked(True)
        params_layout.addWidget(self.center_check)
        
        params_layout.addSpacing(20)
        
        # 对比分析选项
        self.compare_check = QCheckBox("三种方法对比分析")
        self.compare_check.setChecked(True)
        params_layout.addWidget(self.compare_check)
        
        params_layout.addStretch()
        self.input_layout.insertWidget(1, params_group)
        
        # 数据表
        self.data_table = QTableWidget()
        self.data_table.setMinimumHeight(200)
        self.input_layout.addWidget(self.data_table)
        
        self.info_label = QLabel("请导入数据或手动输入已知点坐标和高程异常值(至少12个点)")
        self.info_label.setStyleSheet("color: #666666; padding: 5px;")
        self.input_layout.addWidget(self.info_label)

    def import_file(self):
        """导入文本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入高程数据文件", "", 
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
                                'Zeta': float(parts[3])
                            })
                        except:
                            pass
            
            if len(data) < 12:
                self.show_error(f"数据点不足: {len(data)} < 12")
                return
            
            self._raw_data = pd.DataFrame(data)
            self.X = self._raw_data['X'].values
            self.Y = self._raw_data['Y'].values
            self.Zeta = self._raw_data['Zeta'].values
            self._display_data()
            self.info_label.setText(f"已加载 {len(data)} 个已知点")
            
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
            required_cols = ['X', 'Y', 'Zeta']
            if not all(col in df.columns for col in required_cols):
                self.show_error("Excel文件必须包含X、Y、Zeta列！")
                return
            
            self.X = df['X'].values
            self.Y = df['Y'].values
            self.Zeta = df['Zeta'].values
            self._raw_data = df[required_cols].copy()
            self._display_data()
            self.info_label.setText(f"已加载 {len(self.X)} 个已知点")
        except Exception as e:
            self.show_error(f"导入失败: {str(e)}")

    def manual_input(self):
        dialog = ElevationInputDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data is not None:
                self.X = data['X'].values
                self.Y = data['Y'].values
                self.Zeta = data['Zeta'].values
                self._raw_data = data
                self._display_data()
                self.info_label.setText(f"已输入 {len(data)} 个已知点")

    def calculate(self):
        if self.X is None or len(self.X) < 12:
            self.show_error("数据不足！高程拟合至少需要12个已知点。")
            return
        
        try:
            self.fitter = ElevationFitter()
            self.fitting_result = self.fitter.fit(
                self.X, self.Y, self.Zeta,
                center_coordinates=self.center_check.isChecked()
            )
            self._result_data = self.fitting_result
            
            # 显示对比结果
            self._display_comparison_results()
            
            self.show_info("三种方法对比分析完成")
            
            # 绘制图形
            self.plot_result()
            
            # 启用导出按钮
            self.btn_export_md.setEnabled(True)
            self.btn_export_csv.setEnabled(True)
            self.btn_export_image.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"拟合失败: {str(e)}")

    def _display_comparison_results(self):
        """显示三种方法对比结果"""
        if not self.fitting_result:
            return
        
        result = self.fitting_result
        lines = []
        
        lines.append("=" * 80)
        lines.append("GPS高程拟合 - 三种方法对比分析报告")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"已知点数: {len(self.X)}")
        lines.append("")
        
        # 三种方法对比表
        lines.append("一、三种拟合方法对比")
        lines.append("-" * 80)
        lines.append(f"{'方法':<15} {'RMS(mm)':>12} {'最大残差(mm)':>15} {'平均残差(mm)':>15} {'参数个数':>10}")
        lines.append("-" * 80)
        
        for name, model_result in result.all_results.items():
            rms_mm = model_result.rms * 1000
            max_res_mm = np.max(np.abs(model_result.residuals)) * 1000
            avg_res_mm = np.mean(np.abs(model_result.residuals)) * 1000
            n_params = len(model_result.coefficients)
            
            marker = " ★" if name == result.best_model_name else ""
            lines.append(f"{name:<15} {rms_mm:>12.3f} {max_res_mm:>15.3f} {avg_res_mm:>15.3f} {n_params:>10}{marker}")
        
        lines.append("-" * 80)
        lines.append("注: ★ 表示最优模型")
        lines.append("")
        
        # 最优模型详情
        lines.append("二、最优模型详情")
        lines.append("-" * 80)
        best = result.best_model_result
        lines.append(f"最优方法: {result.best_model_name}")
        lines.append(f"RMS: {best.rms*1000:.3f} mm")
        lines.append("")
        lines.append("模型系数:")
        for i, coef in enumerate(best.coefficients):
            lines.append(f"  a{i} = {coef:.6e}")
        lines.append("")
        
        # 残差分析
        lines.append("三、残差分析")
        lines.append("-" * 80)
        residuals_mm = best.residuals * 1000
        lines.append(f"最大残差: {np.max(np.abs(residuals_mm)):.3f} mm")
        lines.append(f"最小残差: {np.min(np.abs(residuals_mm)):.3f} mm")
        lines.append(f"平均残差: {np.mean(np.abs(residuals_mm)):.3f} mm")
        lines.append(f"残差标准差: {np.std(residuals_mm):.3f} mm")
        lines.append("")
        
        # 结论
        lines.append("四、结论与建议")
        lines.append("-" * 80)
        lines.append(result.recommendation)
        lines.append("")
        
        # 三种方法差异分析
        if len(result.all_results) >= 3:
            lines.append("五、三种方法差异分析")
            lines.append("-" * 80)
            rms_values = {name: mr.rms * 1000 for name, mr in result.all_results.items()}
            max_rms = max(rms_values.values())
            min_rms = min(rms_values.values())
            diff = max_rms - min_rms
            lines.append(f"RMS最大值: {max_rms:.3f} mm")
            lines.append(f"RMS最小值: {min_rms:.3f} mm")
            lines.append(f"RMS差异: {diff:.3f} mm ({diff/min_rms*100:.1f}%)")
            lines.append("")
            
            if diff < 5:
                lines.append("结论: 三种方法精度相近，建议使用简单的平面拟合模型。")
            elif diff < 15:
                lines.append("结论: 三种方法存在一定差异，建议使用推荐的模型。")
            else:
                lines.append("结论: 三种方法差异较大，需根据数据特点选择合适的模型。")
        
        lines.append("")
        lines.append("=" * 80)
        
        self.result_text.setText("\n".join(lines))

    def export(self):
        """导出高程拟合结果"""
        if not self.fitting_result:
            self.show_error("暂无结果可导出！")
            return
        
        try:
            export_dir = QFileDialog.getExistingDirectory(
                self, "选择导出目录", "reports"
            )
            
            if not export_dir:
                return
            
            # 准备导出数据
            export_data = {}
            for name, model_result in self.fitting_result.all_results.items():
                export_data[name] = {
                    'rms_mm': model_result.rms * 1000,
                    'max_residual_mm': np.max(np.abs(model_result.residuals)) * 1000,
                    'coefficients': model_result.coefficients.tolist()
                }
            
            # 导出结果
            exporter = Exporter(export_dir)
            results = exporter.export_elevation(export_data, export_dir)
            
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
        """获取高程拟合结果用于导出"""
        if self.fitting_result is None:
            return None
        
        export_data = []
        
        # 导出三种方法的对比结果
        for name, model_result in self.fitting_result.all_results.items():
            export_data.append({
                '拟合方法': name,
                'RMS(mm)': round(model_result.rms * 1000, 3),
                '最大残差(mm)': round(np.max(np.abs(model_result.residuals)) * 1000, 3),
                '平均残差(mm)': round(np.mean(np.abs(model_result.residuals)) * 1000, 3),
                '参数个数': len(model_result.coefficients),
                '是否最优': '是' if name == self.fitting_result.best_model_name else '否'
            })
        
        return pd.DataFrame(export_data)

    def plot_result(self):
        """绘制结果图表"""
        self.clear_figure()
        
        if self.fitting_result is None:
            return
        
        # 创建3个子图
        ax1 = self.figure.add_subplot(131)
        ax2 = self.figure.add_subplot(132)
        ax3 = self.figure.add_subplot(133)
        
        # 图1: 三种方法RMS对比
        models = list(self.fitting_result.all_results.keys())
        rms_values = [self.fitting_result.all_results[m].rms * 1000 for m in models]
        colors = ['#4CAF50' if m == self.fitting_result.best_model_name else '#2196F3' for m in models]
        
        bars = ax1.bar(range(len(models)), rms_values, color=colors, alpha=0.7)
        ax1.set_xticks(range(len(models)))
        ax1.set_xticklabels(models, rotation=15, ha='right')
        ax1.set_ylabel('RMS (mm)')
        ax1.set_title('三种方法RMS对比')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 在柱状图上标注数值
        for bar, val in zip(bars, rms_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 图2: 最优模型残差分布
        best = self.fitting_result.best_model_result
        residuals_mm = best.residuals * 1000
        ax2.bar(range(len(residuals_mm)), residuals_mm, color='#4CAF50', alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.axhline(y=best.rms*1000, color='red', linestyle='--', 
                   linewidth=1.5, label=f'RMS={best.rms*1000:.2f}mm')
        ax2.axhline(y=-best.rms*1000, color='red', linestyle='--', linewidth=1.5)
        ax2.set_xlabel('点号')
        ax2.set_ylabel('残差 (mm)')
        ax2.set_title(f'残差分布 ({self.fitting_result.best_model_name})')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 图3: 高程异常分布
        ax3.scatter(self.X, self.Y, c=self.Zeta, cmap='viridis', s=50, alpha=0.7)
        ax3.set_xlabel('X坐标 (m)')
        ax3.set_ylabel('Y坐标 (m)')
        ax3.set_title('高程异常空间分布')
        cbar = self.figure.colorbar(ax3.collections[0], ax=ax3)
        cbar.set_label('Zeta (m)')
        ax3.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def _display_data(self):
        if self._raw_data is None:
            return
        
        self.data_table.setRowCount(len(self._raw_data))
        cols = list(self._raw_data.columns)
        self.data_table.setColumnCount(len(cols))
        self.data_table.setHorizontalHeaderLabels(cols)
        
        for i, row in self._raw_data.iterrows():
            for j, col in enumerate(cols):
                value = row[col]
                if isinstance(value, float):
                    self.data_table.setItem(i, j, QTableWidgetItem(f"{value:.4f}"))
                else:
                    self.data_table.setItem(i, j, QTableWidgetItem(str(value)))
        
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def clear_data(self):
        """清空数据"""
        super().clear_data()
        self.X = None
        self.Y = None
        self.Zeta = None
        self.fitting_result = None
        self.data_table.setRowCount(0)
        self.result_text.clear()
        self.info_label.setText("请导入数据或手动输入已知点坐标和高程异常值(至少12个点)")
