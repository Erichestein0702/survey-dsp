"""
时间系统转换模块UI
支持文件批量导入和手动输入
"""

import os
import pandas as pd
from typing import Optional, List

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QDialogButtonBox, QMessageBox, QFileDialog, QPushButton,
    QGroupBox, QComboBox, QRadioButton, QButtonGroup, QSpinBox,
    QDoubleSpinBox, QLineEdit, QWidget, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.base_module_widget import BaseModuleWidget
from module3_TimeSystem.time_converter import TimeConverter
from module3_TimeSystem.julian_day import JulianDay
from module3_TimeSystem.gps_time import GPSTimeCalculator
from module3_TimeSystem.file_processor import TimeFileProcessor, BatchConversionResult
from common.exporter import Exporter


class TimeSystemWidget(BaseModuleWidget):
    """时间系统转换模块"""

    def __init__(self, parent=None):
        self._batch_results: List[BatchConversionResult] = []
        super().__init__("时间系统转换", parent)

    def init_ui(self):
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 文件批量处理页
        self.file_tab = QWidget()
        self._init_file_tab()
        self.tab_widget.addTab(self.file_tab, "文件批量处理")
        
        # 手动输入页
        self.manual_tab = QWidget()
        self._init_manual_tab()
        self.tab_widget.addTab(self.manual_tab, "手动输入")
        
        self.input_layout.insertWidget(1, self.tab_widget)

    def _init_file_tab(self):
        """初始化文件批量处理页"""
        layout = QVBoxLayout(self.file_tab)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        
        btn_layout = QHBoxLayout()
        self.btn_select_file = QPushButton("选择时间数据文件")
        self.btn_select_file.clicked.connect(self._select_file)
        btn_layout.addWidget(self.btn_select_file)
        
        self.lbl_file_path = QLabel("未选择文件")
        self.lbl_file_path.setWordWrap(True)
        btn_layout.addWidget(self.lbl_file_path)
        btn_layout.addStretch()
        
        file_layout.addLayout(btn_layout)
        
        # 文件格式说明
        format_label = QLabel("文件格式：每行6个数值（年 月 日 时 分 秒），空格分隔")
        format_label.setStyleSheet("color: gray;")
        file_layout.addWidget(format_label)
        
        layout.addWidget(file_group)
        
        # 文件内容预览
        preview_group = QGroupBox("文件内容预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.file_preview = QTextEdit()
        self.file_preview.setReadOnly(True)
        self.file_preview.setMaximumHeight(150)
        preview_layout.addWidget(self.file_preview)
        
        layout.addWidget(preview_group)
        
        # 批量计算按钮
        self.btn_batch_calc = QPushButton("批量转换")
        self.btn_batch_calc.clicked.connect(self._batch_calculate)
        self.btn_batch_calc.setEnabled(False)
        layout.addWidget(self.btn_batch_calc)
        
        layout.addStretch()

    def _init_manual_tab(self):
        """初始化手动输入页"""
        layout = QVBoxLayout(self.manual_tab)
        
        input_group = QGroupBox("时间输入")
        input_layout = QVBoxLayout(input_group)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("输入类型:"))
        self.input_type_combo = QComboBox()
        self.input_type_combo.addItems(["公历时间", "儒略日", "GPS时间"])
        self.input_type_combo.currentIndexChanged.connect(self._on_input_type_changed)
        type_layout.addWidget(self.input_type_combo)
        type_layout.addStretch()
        input_layout.addLayout(type_layout)
        
        self.gregorian_widget = QWidget()
        gregorian_layout = QFormLayout(self.gregorian_widget)
        
        datetime_layout = QHBoxLayout()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1, 9999)
        self.year_spin.setValue(2026)
        datetime_layout.addWidget(QLabel("年"))
        datetime_layout.addWidget(self.year_spin)
        
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(3)
        datetime_layout.addWidget(QLabel("月"))
        datetime_layout.addWidget(self.month_spin)
        
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(11)
        datetime_layout.addWidget(QLabel("日"))
        datetime_layout.addWidget(self.day_spin)
        
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(0)
        datetime_layout.addWidget(QLabel("时"))
        datetime_layout.addWidget(self.hour_spin)
        
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(0)
        datetime_layout.addWidget(QLabel("分"))
        datetime_layout.addWidget(self.minute_spin)
        
        self.second_spin = QDoubleSpinBox()
        self.second_spin.setRange(0, 60)
        self.second_spin.setValue(0)
        datetime_layout.addWidget(QLabel("秒"))
        datetime_layout.addWidget(self.second_spin)
        
        gregorian_layout.addRow("公历时间:", datetime_layout)
        input_layout.addWidget(self.gregorian_widget)
        
        self.jd_widget = QWidget()
        jd_layout = QHBoxLayout(self.jd_widget)
        jd_layout.addWidget(QLabel("儒略日:"))
        self.jd_spin = QDoubleSpinBox()
        self.jd_spin.setRange(0, 9999999)
        self.jd_spin.setDecimals(6)
        self.jd_spin.setValue(2461111.0)
        self.jd_spin.setMinimumWidth(150)
        jd_layout.addWidget(self.jd_spin)
        jd_layout.addStretch()
        self.jd_widget.hide()
        input_layout.addWidget(self.jd_widget)
        
        self.gps_widget = QWidget()
        gps_layout = QHBoxLayout(self.gps_widget)
        gps_layout.addWidget(QLabel("GPS周:"))
        self.gps_week_spin = QSpinBox()
        self.gps_week_spin.setRange(0, 9999)
        self.gps_week_spin.setValue(2300)
        gps_layout.addWidget(self.gps_week_spin)
        gps_layout.addWidget(QLabel("周内秒:"))
        self.gps_seconds_spin = QDoubleSpinBox()
        self.gps_seconds_spin.setRange(0, 604800)
        self.gps_seconds_spin.setDecimals(3)
        self.gps_seconds_spin.setValue(0)
        self.gps_seconds_spin.setMinimumWidth(120)
        gps_layout.addWidget(self.gps_seconds_spin)
        gps_layout.addStretch()
        self.gps_widget.hide()
        input_layout.addWidget(self.gps_widget)
        
        layout.addWidget(input_group)
        
        # 手动计算按钮
        self.btn_manual_calc = QPushButton("转换")
        self.btn_manual_calc.clicked.connect(self._manual_calculate)
        layout.addWidget(self.btn_manual_calc)
        
        layout.addStretch()
        
        self._on_input_type_changed(0)

    def _on_input_type_changed(self, index):
        self.gregorian_widget.hide()
        self.jd_widget.hide()
        self.gps_widget.hide()
        
        if index == 0:
            self.gregorian_widget.show()
        elif index == 1:
            self.jd_widget.show()
        elif index == 2:
            self.gps_widget.show()

    def _select_file(self):
        """选择时间数据文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择时间数据文件", "", "文本文件 (*.txt *.csv *.dat);;所有文件 (*.*)"
        )
        
        if file_path:
            self._current_file = file_path
            self.lbl_file_path.setText(file_path)
            
            # 预览文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    preview_lines = []
                    for i, line in enumerate(lines[:20]):  # 只显示前20行
                        line = line.strip()
                        if line and not line.startswith('#'):
                            preview_lines.append(line)
                    self.file_preview.setText('\n'.join(preview_lines))
                    self.btn_batch_calc.setEnabled(True)
            except Exception as e:
                self.show_error(f"无法读取文件: {str(e)}")
                self.btn_batch_calc.setEnabled(False)

    def _batch_calculate(self):
        """批量计算"""
        if not hasattr(self, '_current_file'):
            self.show_error("请先选择文件")
            return
        
        try:
            results, output = TimeFileProcessor.process_file(self._current_file)
            self._batch_results = results
            
            # 显示格式化输出
            self.result_text.setText(output)
            
            # 保存结果用于导出
            self._result_data = {
                'type': 'batch',
                'results': results,
                'output': output
            }
            
            self.show_info(f"成功转换 {len(results)} 条时间记录")
            
            # 绘制图形
            self.plot_result()
            
            # 启用导出按钮
            self.btn_export_md.setEnabled(True)
            self.btn_export_csv.setEnabled(True)
            self.btn_export_image.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"批量转换失败: {str(e)}")

    def _manual_calculate(self):
        """手动计算单个时间"""
        try:
            input_type = self.input_type_combo.currentIndex()
            
            if input_type == 0:
                year = self.year_spin.value()
                month = self.month_spin.value()
                day = self.day_spin.value()
                hour = self.hour_spin.value()
                minute = self.minute_spin.value()
                second = self.second_spin.value()
                
                result = TimeConverter.full_workflow(
                    year=year, month=month, day=day,
                    hour=hour, minute=minute, second=second
                )
            elif input_type == 1:
                jd = self.jd_spin.value()
                result = TimeConverter.full_workflow(jd=jd)
            elif input_type == 2:
                week = self.gps_week_spin.value()
                seconds = self.gps_seconds_spin.value()
                result = TimeConverter.full_workflow(week=week, seconds=seconds)
            
            # 格式化为指导书要求的格式
            output = self._format_manual_output(result)
            self.result_text.setText(output)
            
            self._result_data = {
                'type': 'manual',
                'result': result
            }
            
            self.show_info("时间转换完成！")
            
            # 绘制图形
            self.plot_result()
            
            # 启用导出按钮
            self.btn_export_md.setEnabled(True)
            self.btn_export_csv.setEnabled(True)
            self.btn_export_image.setEnabled(True)
            
        except Exception as e:
            self.show_error(f"计算失败: {str(e)}")

    def _format_manual_output(self, result: dict) -> str:
        """格式化手动输入的输出"""
        lines = []
        
        lines.append("-------JD-----------")
        lines.append(f"{result['julian_day']:.6f}")
        
        lines.append("")
        lines.append("-------公历（年 月 日 时：分：秒）----------")
        g = result['gregorian']
        lines.append(f"{g.year} {g.month} {g.day} {g.hour} {g.minute} {int(g.second)}")
        
        lines.append("")
        lines.append("-------年积日----------")
        lines.append(f"第{result['day_of_year']}日")
        
        lines.append("")
        lines.append("-------三天打鱼两天晒网----------")
        lines.append(result['fishing_status'])
        
        lines.append("")
        lines.append("-------GPS时间（周 周内秒）----------")
        gps = result['gps_time']
        lines.append(f"{gps.week} {gps.seconds:.3f}")
        
        return "\n".join(lines)

    def import_file(self):
        """导入文件 - 切换到文件批量处理页"""
        self.tab_widget.setCurrentIndex(0)
        self._select_file()

    def import_excel(self):
        """时间系统转换模块不支持Excel导入"""
        self.show_info("时间系统转换模块支持文件导入，请使用\"文件批量处理\"页")

    def _load_file_data(self, file_path: str):
        """加载文件数据"""
        self.tab_widget.setCurrentIndex(0)
        self._current_file = file_path
        self.lbl_file_path.setText(file_path)
        self._batch_calculate()

    def _load_excel_data(self, file_path: str):
        """不支持Excel加载"""
        self.show_info("时间系统转换模块不支持Excel导入")

    def manual_input(self):
        """切换到手动输入页"""
        self.tab_widget.setCurrentIndex(1)

    def calculate(self):
        """根据当前标签页执行计算"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:
            self._batch_calculate()
        else:
            self._manual_calculate()

    def export(self):
        """
        导出时间系统转换结果
        """
        if not self._result_data:
            self.show_error("暂无结果可导出！")
            return
        
        try:
            # 选择导出目录
            export_dir = QFileDialog.getExistingDirectory(
                self, "选择导出目录", "reports"
            )
            
            if not export_dir:
                return
            
            # 准备导出数据
            export_data = []
            
            if self._result_data.get('type') == 'batch':
                # 批量结果
                for r in self._result_data['results']:
                    rec = r.input_record
                    export_data.append({
                        'year': rec.year,
                        'month': rec.month,
                        'day': rec.day,
                        'hour': rec.hour,
                        'minute': rec.minute,
                        'second': rec.second,
                        'julian_day': r.julian_day,
                        'gps_week': r.gps_week,
                        'gps_seconds': r.gps_seconds,
                        'day_of_year': r.day_of_year,
                        'fishing_status': r.fishing_status
                    })
            else:
                # 单个结果
                result = self._result_data['result']
                g = result['gregorian']
                gps = result['gps_time']
                export_data.append({
                    'year': g.year,
                    'month': g.month,
                    'day': g.day,
                    'hour': g.hour,
                    'minute': g.minute,
                    'second': g.second,
                    'julian_day': result['julian_day'],
                    'gps_week': gps.week,
                    'gps_seconds': gps.seconds,
                    'day_of_year': result['day_of_year'],
                    'fishing_status': result['fishing_status']
                })
            
            # 导出结果
            exporter = Exporter(export_dir)
            export_result = exporter.export_time(export_data, export_dir)
            
            if export_result.success:
                self.show_info(f"导出成功: {export_result.file_path}")
            else:
                self.show_error(f"导出失败: {export_result.message}")
                
        except Exception as e:
            self.show_error(f"导出失败: {str(e)}")

    def get_result_text(self) -> str:
        if self._result_data is None:
            return "暂无结果"
        return self.result_text.toPlainText()
    
    def _get_export_data(self) -> pd.DataFrame:
        """获取时间系统转换结果用于导出"""
        if self._result_data is None:
            return None
        
        export_data = []
        
        if self._result_data.get('type') == 'batch':
            # 批量结果
            for r in self._batch_results:
                rec = r.input_record
                export_data.append({
                    '年': rec.year,
                    '月': rec.month,
                    '日': rec.day,
                    '时': rec.hour,
                    '分': rec.minute,
                    '秒': rec.second,
                    '儒略日': r.julian_day,
                    'GPS周': r.gps_week,
                    'GPS周内秒': r.gps_seconds,
                    '年积日': r.day_of_year,
                    '打鱼晒网': r.fishing_status
                })
        else:
            # 单个结果
            result = self._result_data.get('result', {})
            if result:
                g = result.get('gregorian')
                gps = result.get('gps_time')
                export_data.append({
                    '年': g.year if g else '',
                    '月': g.month if g else '',
                    '日': g.day if g else '',
                    '时': g.hour if g else '',
                    '分': g.minute if g else '',
                    '秒': g.second if g else '',
                    '儒略日': result.get('julian_day', ''),
                    'GPS周': gps.week if gps else '',
                    'GPS周内秒': gps.seconds if gps else '',
                    '年积日': result.get('day_of_year', ''),
                    '打鱼晒网': result.get('fishing_status', '')
                })
        
        return pd.DataFrame(export_data)

    def plot_result(self):
        """绘制结果图表"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if self._result_data:
            if self._result_data.get('type') == 'batch' and self._batch_results:
                # 批量结果显示年积日分布
                days = [r.day_of_year for r in self._batch_results]
                jds = [r.julian_day for r in self._batch_results]
                
                ax.scatter(days, jds, c='#2196F3', s=50, alpha=0.6)
                ax.set_xlabel('年积日')
                ax.set_ylabel('儒略日 (JD)')
                ax.set_title('时间数据分布')
                ax.grid(True, alpha=0.3)
            else:
                # 单个结果显示时间系统对比
                labels = ['公历\n(年月日)', '儒略日\n(JD)', 'GPS时间\n(周+秒)']
                x_pos = [0, 1, 2]
                
                ax.bar(x_pos, [1, 1, 1], color=['#2196F3', '#4CAF50', '#FF9800'])
                ax.set_xticks(x_pos)
                ax.set_xticklabels(labels)
                ax.set_ylabel('时间系统')
                ax.set_title('时间系统转换结果')
                
                result = self._result_data.get('result', {})
                if result.get('gregorian'):
                    g = result['gregorian']
                    ax.text(0, 0.5, f"{g.year}-{g.month:02d}-{g.day:02d}\n"
                            f"{g.hour:02d}:{g.minute:02d}:{g.second:02.0f}",
                            ha='center', va='center', fontsize=10, color='white', fontweight='bold')
                
                if result.get('julian_day') is not None:
                    ax.text(1, 0.5, f"{result['julian_day']:.2f}",
                            ha='center', va='center', fontsize=10, color='white', fontweight='bold')
                
                if result.get('gps_time'):
                    gps = result['gps_time']
                    ax.text(2, 0.5, f"W{gps.week}\n{gps.seconds:.0f}s",
                            ha='center', va='center', fontsize=10, color='white', fontweight='bold')
                
                ax.set_ylim(0, 1.2)
                ax.set_yticks([])
            
        self.canvas.draw()
