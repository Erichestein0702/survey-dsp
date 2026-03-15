"""
IDW插值模块UI
支持n=4,5,6对比分析
"""

import os
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QDialogButtonBox, QMessageBox, QFileDialog, QPushButton,
    QGroupBox, QComboBox, QRadioButton, QButtonGroup, QSpinBox,
    QDoubleSpinBox, QTabWidget, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_module_widget import BaseModuleWidget
from module1_IDW.idw_interpolator import IDWInterpolator
from module1_IDW.models import KnownPoint, TargetPoint, IDWResult
from common.exporter import Exporter


class IDWInputDialog(QDialog):
    """IDW数据输入对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入IDW插值数据")
        self.setMinimumSize(800, 600)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        known_group = QGroupBox("已知采样点")
        known_layout = QVBoxLayout(known_group)
        known_layout.addWidget(QLabel("格式: 点号 X Y 高程Z"))
        self.known_text = QTextEdit()
        self.known_text.setPlaceholderText("P01 100.0 200.0 50.5\nP02 150.0 250.0 52.3\nP03 200.0 300.0 55.1")
        known_layout.addWidget(self.known_text)
        layout.addWidget(known_group)

        target_group = QGroupBox("待插值点")
        target_layout = QVBoxLayout(target_group)
        target_layout.addWidget(QLabel("格式: 点号 X Y"))
        self.target_text = QTextEdit()
        self.target_text.setPlaceholderText("Q01 120.0 220.0\nQ02 180.0 280.0")
        target_layout.addWidget(self.target_text)
        layout.addWidget(target_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        known_data = self.known_text.toPlainText().strip()
        target_data = self.target_text.toPlainText().strip()
        if not known_data or not target_data:
            QMessageBox.warning(self, "数据不足", "请输入已知点和待插值点数据！")
            return None, None
        return known_data, target_data


class IDWWidget(BaseModuleWidget):
    """IDW插值模块 - 支持n=4,5,6对比分析"""

    def __init__(self, parent=None):
        self.interpolator: Optional[IDWInterpolator] = None
        self.known_points = []
        self.target_points = []
        self.comparison_results: Dict[int, List[IDWResult]] = {}
        super().__init__("IDW插值", parent)

    def init_ui(self):
        # 参数设置
        params_group = QGroupBox("插值参数")
        params_layout = QHBoxLayout(params_group)
        
        params_layout.addWidget(QLabel("权指数 p:"))
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setRange(1.0, 5.0)
        self.power_spin.setValue(2.0)
        self.power_spin.setSingleStep(0.5)
        params_layout.addWidget(self.power_spin)
        
        params_layout.addSpacing(20)
        
        # n值对比选项
        self.compare_check = QCheckBox("对比n=4,5,6")
        self.compare_check.setChecked(True)
        self.compare_check.stateChanged.connect(self._on_compare_changed)
        params_layout.addWidget(self.compare_check)
        
        params_layout.addWidget(QLabel("n值:"))
        self.n_combo = QComboBox()
        self.n_combo.addItems(["4", "5", "6", "4,5,6(对比)"])
        self.n_combo.setCurrentIndex(3)  # 默认对比模式
        params_layout.addWidget(self.n_combo)
        
        params_layout.addStretch()
        self.input_layout.insertWidget(1, params_group)

    def _on_compare_changed(self, state):
        """对比选项改变"""
        if state == Qt.CheckState.Checked.value:
            self.n_combo.setCurrentIndex(3)
        else:
            self.n_combo.setCurrentIndex(0)

    def import_file(self):
        """导入文本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入IDW数据文件", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            self._load_file_data(file_path)

    def _load_file_data(self, file_path: str):
        known_points = []
        target_points = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) >= 4:
                    known_points.append(KnownPoint(
                        id=parts[0],
                        x=float(parts[1]),
                        y=float(parts[2]),
                        z=float(parts[3])
                    ))
                elif len(parts) >= 3:
                    target_points.append(TargetPoint(
                        id=parts[0],
                        x=float(parts[1]),
                        y=float(parts[2])
                    ))
        
        self.known_points = known_points
        self.target_points = target_points
        
        df = pd.DataFrame([{'ID': p.id, 'X': p.x, 'Y': p.y, 'Z': p.z} for p in known_points])
        self.update_data_preview(df)
        self.show_info(f"已加载 {len(known_points)} 个已知点, {len(target_points)} 个待插值点")

    def import_excel(self):
        self.show_info("IDW模块推荐使用文本文件导入")

    def manual_input(self):
        dialog = IDWInputDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            known_data, target_data = dialog.get_data()
            if known_data and target_data:
                try:
                    known_points = []
                    for line in known_data.strip().split('\n'):
                        parts = line.split()
                        if len(parts) >= 4:
                            known_points.append(KnownPoint(
                                id=parts[0],
                                x=float(parts[1]),
                                y=float(parts[2]),
                                z=float(parts[3])
                            ))
                    
                    target_points = []
                    for line in target_data.strip().split('\n'):
                        parts = line.split()
                        if len(parts) >= 3:
                            target_points.append(TargetPoint(
                                id=parts[0],
                                x=float(parts[1]),
                                y=float(parts[2])
                            ))
                    
                    self.known_points = known_points
                    self.target_points = target_points
                    
                    df = pd.DataFrame([{'ID': p.id, 'X': p.x, 'Y': p.y, 'Z': p.z} for p in known_points])
                    self.update_data_preview(df)
                    self.show_info(f"已加载 {len(known_points)} 个已知点, {len(target_points)} 个待插值点")
                except Exception as e:
                    self.show_error(f"数据解析失败: {str(e)}")

    def calculate(self):
        if not self.known_points or not self.target_points:
            self.show_error("请先导入数据！")
            return
        
        try:
            power = self.power_spin.value()
            
            # 判断是否进行n值对比
            do_compare = self.compare_check.isChecked() or self.n_combo.currentIndex() == 3
            
            if do_compare:
                # 对比n=4,5,6
                n_values = [4, 5, 6]
                self.comparison_results = {}
                
                for n in n_values:
                    interpolator = IDWInterpolator(
                        self.known_points, 
                        power=power, 
                        n_neighbors=n
                    )
                    
                    results = []
                    for target in self.target_points:
                        r = interpolator.interpolate(target)
                        results.append(r)
                    
                    self.comparison_results[n] = results
                
                self._result_data = self.comparison_results
                self._display_comparison_results()
                self.show_info(f"n=4,5,6对比分析完成！")
            else:
                # 单一n值
                n = int(self.n_combo.currentText())
                
                self.interpolator = IDWInterpolator(
                    self.known_points, 
                    power=power, 
                    n_neighbors=n
                )
                
                results = []
                for target in self.target_points:
                    r = self.interpolator.interpolate(target)
                    results.append(r)
                
                self._result_data = results
                self._display_single_results(results, n)
                self.show_info(f"插值完成！n={n}")
            
            # 绘制图形
            self.plot_result()
            
            # 启用导出按钮
            self.btn_export_md.setEnabled(True)
            self.btn_export_csv.setEnabled(True)
            self.btn_export_image.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"计算失败: {str(e)}")

    def _display_single_results(self, results: List[IDWResult], n: int):
        """显示单一n值结果"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"IDW插值计算报告 (n={n})")
        lines.append("=" * 70)
        lines.append(f"已知点数: {len(self.known_points)}")
        lines.append(f"待插值点数: {len(self.target_points)}")
        lines.append(f"权指数p: {self.power_spin.value()}")
        lines.append("")
        lines.append("插值结果:")
        lines.append("-" * 70)
        lines.append(f"{'点号':<10} {'X':>12} {'Y':>12} {'高程Z':>15} {'使用点数':>10}")
        lines.append("-" * 70)
        
        for r in results:
            lines.append(f"{r.target_point.id:<10} {r.target_point.x:>12.3f} {r.target_point.y:>12.3f} {r.interpolated_z:>15.6f} {len(r.used_points):>10}")
        
        lines.append("=" * 70)
        self.result_text.setText("\n".join(lines))

    def _display_comparison_results(self):
        """显示n=4,5,6对比结果"""
        lines = []
        lines.append("=" * 90)
        lines.append("IDW插值对比分析报告 (n=4,5,6)")
        lines.append("=" * 90)
        lines.append(f"已知点数: {len(self.known_points)}")
        lines.append(f"待插值点数: {len(self.target_points)}")
        lines.append(f"权指数p: {self.power_spin.value()}")
        lines.append("")
        lines.append("对比结果:")
        lines.append("-" * 90)
        
        # 表头
        header = f"{'点号':<10} {'X':>10} {'Y':>10}"
        for n in [4, 5, 6]:
            header += f" {'Z(n='+str(n)+')':>15}"
        header += f" {'极差':>12} {'均值':>12}"
        lines.append(header)
        lines.append("-" * 90)
        
        # 数据行
        for i, target in enumerate(self.target_points):
            row = f"{target.id:<10} {target.x:>10.3f} {target.y:>10.3f}"
            
            z_values = []
            for n in [4, 5, 6]:
                z = self.comparison_results[n][i].interpolated_z
                z_values.append(z)
                row += f" {z:>15.6f}"
            
            # 计算极差和均值
            z_range = max(z_values) - min(z_values)
            z_mean = sum(z_values) / len(z_values)
            
            row += f" {z_range:>12.6f} {z_mean:>12.6f}"
            lines.append(row)
        
        lines.append("-" * 90)
        
        # 结论分析
        lines.append("")
        lines.append("结论分析:")
        lines.append("-" * 90)
        
        # 计算每个n值的平均高程
        avg_z = {}
        for n in [4, 5, 6]:
            avg = sum(r.interpolated_z for r in self.comparison_results[n]) / len(self.target_points)
            avg_z[n] = avg
            lines.append(f"  n={n}: 平均高程 = {avg:.6f}")
        
        # 找出差异最大的点
        max_diff = 0
        max_diff_point = ""
        for i, target in enumerate(self.target_points):
            z_values = [self.comparison_results[n][i].interpolated_z for n in [4, 5, 6]]
            diff = max(z_values) - min(z_values)
            if diff > max_diff:
                max_diff = diff
                max_diff_point = target.id
        
        lines.append(f"  最大差异: {max_diff:.6f}m (点 {max_diff_point})")
        lines.append("")
        lines.append("建议:")
        lines.append("  - n值较小时，插值结果受最近邻点影响更大")
        lines.append("  - n值较大时，插值结果更平滑但可能丢失局部特征")
        lines.append("  - 根据数据分布选择合适的n值")
        
        lines.append("=" * 90)
        self.result_text.setText("\n".join(lines))

    def export(self):
        """导出IDW插值结果"""
        if not self._result_data:
            self.show_error("暂无结果可导出！")
            return
        
        try:
            export_dir = QFileDialog.getExistingDirectory(
                self, "选择导出目录", str(Path("reports"))
            )
            
            if not export_dir:
                return
            
            # 准备导出数据
            export_data = []
            
            if isinstance(self._result_data, dict):
                # 对比模式
                for n, results in self._result_data.items():
                    for r in results:
                        export_data.append({
                            'n_value': n,
                            'point_id': r.target_point.id,
                            'x': r.target_point.x,
                            'y': r.target_point.y,
                            'interpolated_z': r.interpolated_z
                        })
            else:
                # 单一模式
                for r in self._result_data:
                    export_data.append({
                        'point_id': r.target_point.id,
                        'x': r.target_point.x,
                        'y': r.target_point.y,
                        'interpolated_z': r.interpolated_z
                    })
            
            # 导出结果
            exporter = Exporter(export_dir)
            result = exporter.export_idw(export_data, export_dir)
            
            if result.success:
                self.show_info(f"导出成功: {result.file_path}")
            else:
                self.show_error(f"导出失败: {result.message}")
                
        except Exception as e:
            self.show_error(f"导出失败: {str(e)}")

    def get_result_text(self) -> str:
        return self.result_text.toPlainText()
    
    def _get_export_data(self) -> pd.DataFrame:
        """获取IDW插值结果用于导出"""
        if self._result_data is None:
            return None
        
        export_data = []
        
        if isinstance(self._result_data, dict):
            # 对比模式 n=4,5,6
            for n, results in self._result_data.items():
                for r in results:
                    export_data.append({
                        'n值': n,
                        '点号': r.target_point.id,
                        'X坐标': r.target_point.x,
                        'Y坐标': r.target_point.y,
                        '插值高程Z': r.interpolated_z,
                        '使用点数': len(r.used_points)
                    })
        else:
            # 单一模式
            for r in self._result_data:
                export_data.append({
                    '点号': r.target_point.id,
                    'X坐标': r.target_point.x,
                    'Y坐标': r.target_point.y,
                    '插值高程Z': r.interpolated_z,
                    '使用点数': len(r.used_points)
                })
        
        return pd.DataFrame(export_data)

    def plot_result(self):
        """绘制结果图表"""
        self.figure.clear()
        
        if isinstance(self._result_data, dict):
            # 对比模式 - 绘制对比图
            ax = self.figure.add_subplot(111)
            
            x_pos = np.arange(len(self.target_points))
            width = 0.25
            
            for i, n in enumerate([4, 5, 6]):
                zs = [r.interpolated_z for r in self._result_data[n]]
                ax.bar(x_pos + i * width, zs, width, label=f'n={n}')
            
            ax.set_xlabel('待插值点')
            ax.set_ylabel('高程Z')
            ax.set_title('IDW插值对比 (n=4,5,6)')
            ax.set_xticks(x_pos + width)
            ax.set_xticklabels([t.id for t in self.target_points], rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
        else:
            # 单一模式
            ax = self.figure.add_subplot(111)
            
            xs = [r.target_point.x for r in self._result_data]
            ys = [r.target_point.y for r in self._result_data]
            zs = [r.interpolated_z for r in self._result_data]
            
            scatter = ax.scatter(xs, ys, c=zs, cmap='terrain', s=100, edgecolors='black')
            self.figure.colorbar(scatter, ax=ax, label='高程')
            
            for r in self._result_data:
                ax.annotate(r.target_point.id, (r.target_point.x, r.target_point.y), 
                           textcoords="offset points", xytext=(5,5), fontsize=8)
            
            if self.known_points:
                kx = [p.x for p in self.known_points]
                ky = [p.y for p in self.known_points]
                ax.scatter(kx, ky, c='red', marker='^', s=50, label='已知点', edgecolors='black')
            
            ax.set_xlabel('X坐标')
            ax.set_ylabel('Y坐标')
            ax.set_title('IDW插值结果')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
