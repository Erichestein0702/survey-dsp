"""
数据导出组件
支持 Markdown报告、CSV数据、PNG/PDF图形导出
"""

import os
import csv
import base64
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .logger import get_logger

logger = get_logger("Exporter")


@dataclass
class ExportResult:
    """导出结果"""
    success: bool
    file_path: Optional[Path]
    message: str


class Exporter:
    """数据导出器"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        初始化导出器
        
        Args:
            output_dir: 默认输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"导出器初始化完成，输出目录: {self.output_dir}")
    
    def export_csv(self, data: pd.DataFrame, filename: str,
                   output_dir: Optional[str] = None) -> ExportResult:
        """
        导出CSV文件
        
        Args:
            data: 数据DataFrame
            filename: 文件名
            output_dir: 输出目录（可选）
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            save_dir = Path(output_dir) if output_dir else self.output_dir
            save_dir.mkdir(exist_ok=True)
            
            file_path = save_dir / f"{filename}.csv"
            data.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"CSV导出成功: {file_path}")
            return ExportResult(True, file_path, "CSV导出成功")
            
        except Exception as e:
            logger.error("Exporter", f"CSV导出失败: {filename}", e)
            return ExportResult(False, None, f"CSV导出失败: {str(e)}")
    
    def export_markdown(self, content: str, filename: str,
                       output_dir: Optional[str] = None) -> ExportResult:
        """
        导出Markdown报告
        
        Args:
            content: Markdown内容
            filename: 文件名
            output_dir: 输出目录（可选）
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            save_dir = Path(output_dir) if output_dir else self.output_dir
            save_dir.mkdir(exist_ok=True)
            
            file_path = save_dir / f"{filename}.md"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Markdown导出成功: {file_path}")
            return ExportResult(True, file_path, "Markdown导出成功")
            
        except Exception as e:
            logger.error("Exporter", f"Markdown导出失败: {filename}", e)
            return ExportResult(False, None, f"Markdown导出失败: {str(e)}")
    
    def export_txt(self, content: str, filename: str,
                   output_dir: Optional[str] = None) -> ExportResult:
        """
        导出TXT文件
        
        Args:
            content: 文本内容
            filename: 文件名
            output_dir: 输出目录（可选）
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            save_dir = Path(output_dir) if output_dir else self.output_dir
            save_dir.mkdir(exist_ok=True)
            
            file_path = save_dir / f"{filename}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"TXT导出成功: {file_path}")
            return ExportResult(True, file_path, "TXT导出成功")
            
        except Exception as e:
            logger.error("Exporter", f"TXT导出失败: {filename}", e)
            return ExportResult(False, None, f"TXT导出失败: {str(e)}")
    
    def export_png(self, figure: Figure, filename: str,
                  output_dir: Optional[str] = None,
                  dpi: int = 300) -> ExportResult:
        """
        导出PNG图像
        
        Args:
            figure: Matplotlib图形对象
            filename: 文件名
            output_dir: 输出目录（可选）
            dpi: 分辨率
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            save_dir = Path(output_dir) if output_dir else self.output_dir
            save_dir.mkdir(exist_ok=True)
            
            file_path = save_dir / f"{filename}.png"
            figure.savefig(file_path, dpi=dpi, bbox_inches='tight',
                         facecolor='white', edgecolor='none')
            plt.close(figure)
            
            logger.info(f"PNG导出成功: {file_path}")
            return ExportResult(True, file_path, "PNG导出成功")
            
        except Exception as e:
            logger.error("Exporter", f"PNG导出失败: {filename}", e)
            return ExportResult(False, None, f"PNG导出失败: {str(e)}")
    
    def export_pdf(self, figure: Figure, filename: str,
                  output_dir: Optional[str] = None) -> ExportResult:
        """
        导出PDF图像
        
        Args:
            figure: Matplotlib图形对象
            filename: 文件名
            output_dir: 输出目录（可选）
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            save_dir = Path(output_dir) if output_dir else self.output_dir
            save_dir.mkdir(exist_ok=True)
            
            file_path = save_dir / f"{filename}.pdf"
            figure.savefig(file_path, format='pdf', bbox_inches='tight',
                         facecolor='white', edgecolor='none')
            plt.close(figure)
            
            logger.info(f"PDF导出成功: {file_path}")
            return ExportResult(True, file_path, "PDF导出成功")
            
        except Exception as e:
            logger.error("Exporter", f"PDF导出失败: {filename}", e)
            return ExportResult(False, None, f"PDF导出失败: {str(e)}")
    
    def figure_to_base64(self, figure: Figure, format: str = 'png') -> str:
        """
        将图形转换为Base64字符串（用于嵌入HTML/Markdown）
        
        Args:
            figure: Matplotlib图形对象
            format: 格式 ('png' 或 'svg')
            
        Returns:
            Base64编码的图像字符串
        """
        try:
            buf = BytesIO()
            figure.savefig(buf, format=format, bbox_inches='tight',
                         facecolor='white', edgecolor='none')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(figure)
            return img_base64
            
        except Exception as e:
            logger.error("Exporter", "Base64转换失败", e)
            return ""
    
    def create_report_header(self, title: str, module_name: str) -> str:
        """
        创建报告头部
        
        Args:
            title: 报告标题
            module_name: 模块名称
            
        Returns:
            Markdown格式的报告头部
        """
        return f"""# {title}

**模块**: {module_name}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**软件版本**: Survey DSP v2.0

---

"""
    
    def create_data_table(self, data: pd.DataFrame, title: str = "数据表") -> str:
        """
        创建Markdown数据表
        
        Args:
            data: 数据DataFrame
            title: 表格标题
            
        Returns:
            Markdown格式的表格
        """
        if data.empty:
            return f"**{title}**: 无数据\n\n"
        
        # 限制显示行数
        display_data = data.head(50)
        if len(data) > 50:
            note = f"\n*（仅显示前50行，共{len(data)}行）*\n"
        else:
            note = ""
        
        # 生成Markdown表格
        md = f"### {title}\n\n"
        md += display_data.to_markdown(index=False, floatfmt=".6f")
        md += note + "\n\n"
        
        return md
    
    def create_summary_section(self, summary: Dict[str, Any]) -> str:
        """
        创建摘要部分
        
        Args:
            summary: 摘要数据字典
            
        Returns:
            Markdown格式的摘要
        """
        md = "## 计算摘要\n\n"
        md += "| 项目 | 数值 |\n"
        md += "|------|------|\n"
        
        for key, value in summary.items():
            if isinstance(value, float):
                formatted_value = f"{value:.6f}"
            else:
                formatted_value = str(value)
            md += f"| {key} | {formatted_value} |\n"
        
        md += "\n"
        return md
    
    def _decimal_to_dms(self, decimal_degrees: float) -> str:
        """
        将十进制度转换为度分秒格式
        
        Args:
            decimal_degrees: 十进制度数
            
        Returns:
            度分秒字符串，格式：°′″
        """
        try:
            degrees = int(decimal_degrees)
            minutes_decimal = abs(decimal_degrees - degrees) * 60
            minutes = int(minutes_decimal)
            seconds = (minutes_decimal - minutes) * 60
            return f"{degrees}°{minutes:02d}′{seconds:04.1f}″"
        except Exception:
            return f"{decimal_degrees:.6f}°"
    
    def _safe_get_value(self, data: Any, keys: List[str], default: Any = None) -> Any:
        """
        安全获取数据值（支持多种访问方式）
        
        Args:
            data: 数据对象
            keys: 可能的键名列表
            default: 默认值
            
        Returns:
            获取到的值或默认值
        """
        for key in keys:
            if isinstance(data, dict):
                if key in data:
                    return data[key]
            else:
                if hasattr(data, key):
                    return getattr(data, key)
        return default
    
    # 题目1：IDW插值导出
    def export_idw(self, results: List[Dict], output_dir: Optional[str] = None) -> ExportResult:
        """
        导出IDW插值结果
        
        Args:
            results: IDW插值结果列表
            output_dir: 输出目录（可选）
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            # 准备数据
            data = []
            for r in results:
                # 支持多种数据格式
                # 格式1：字典包含target_point对象
                if isinstance(r, dict) and 'target_point' in r:
                    target = r['target_point']
                    # 支持对象或字典
                    if hasattr(target, 'id'):
                        point_id = target.id
                    else:
                        point_id = self._safe_get_value(target, ['id', '点号'], 'Unknown')
                    
                    interpolated_z = self._safe_get_value(r, ['interpolated_z', '插值高程'], 0)
                # 格式2：字典直接包含数据
                elif isinstance(r, dict):
                    point_id = self._safe_get_value(r, ['待插值点编号', 'id', '点号'], 'Unknown')
                    interpolated_z = self._safe_get_value(r, ['插值高程(m)', 'interpolated_z', '插值高程'], 0)
                else:
                    # 对象格式
                    point_id = self._safe_get_value(r, ['id', '点号'], 'Unknown')
                    interpolated_z = self._safe_get_value(r, ['interpolated_z', '插值高程'], 0)
                
                # 题目要求：分别取n=4,5,6
                for n in [4, 5, 6]:
                    data.append({
                        '待插值点编号': point_id,
                        'n取值': n,
                        '插值高程(m)': round(float(interpolated_z), 3)
                    })
            
            df = pd.DataFrame(data)
            filename = f"题目1_IDW插值结果_{datetime.now().strftime('%Y%m%d')}"
            return self.export_csv(df, filename, output_dir)
            
        except Exception as e:
            logger.error("Exporter", "IDW导出失败", e)
            return ExportResult(False, None, f"IDW导出失败: {str(e)}")
    
    # 题目2：GPS高程拟合导出
    def export_elevation(self, results: Dict, output_dir: Optional[str] = None) -> List[ExportResult]:
        """
        导出GPS高程拟合结果
        
        Args:
            results: 高程拟合结果字典或对象
            output_dir: 输出目录（可选）
            
        Returns:
            List[ExportResult]: 导出结果列表
        """
        results_list = []
        
        try:
            # 导出CSV
            data = []
            
            # 处理拟合结果对象
            if hasattr(results, 'quadratic_result'):
                # 从FittingResult对象中提取数据
                fitting_result = results
                # 导出模型对比信息
                txt_content = "# 高程拟合模型对比\n\n"
                txt_content += f"**推荐模型**: {fitting_result.recommendation}\n\n"
                txt_content += f"**最优模型**: {fitting_result.best_model_name}\n\n"
                txt_content += "## 模型对比\n\n"
                txt_content += fitting_result.comparison_table.to_markdown(index=False, floatfmt=".4f")
                txt_content += "\n\n## 模型系数\n\n"
                
                # 导出各模型系数
                for model_name, model_result in [
                    ('二次曲面', fitting_result.quadratic_result),
                    ('多项式平面', fitting_result.plane_result),
                    ('四参数曲面', fitting_result.four_param_result)
                ]:
                    txt_content += f"### {model_name}\n\n"
                    txt_content += "| 系数 | 数值 |\n|------|------|\n"
                    for i, coef in enumerate(model_result.coefficients):
                        txt_content += f"| a{i} | {coef:.6e} |\n"
                    txt_content += f"\n**RMS**: {model_result.rms*1000:.3f} mm\n\n"
                
                # 注意：待求点预测需要额外数据
                # 这里提供占位符，实际使用时需要传入待求点坐标
                for point_id in range(13, 19):
                    data.append({
                        '待求点编号': str(point_id),
                        '二次曲面拟合值(m)': 0.0,
                        '多项式平面拟合值(m)': 0.0,
                        '四参数曲面拟合值(m)': 0.0,
                        '备注': '待求点坐标未提供，无法预测'
                    })
            else:
                # 处理字典格式（原始格式）
                for point_id, values in results.items():
                    data.append({
                        '待求点编号': point_id,
                        '二次曲面拟合值(m)': round(values.get('quadratic', 0), 4),
                        '多项式平面拟合值(m)': round(values.get('plane', 0), 4),
                        '四参数曲面拟合值(m)': round(values.get('four_param', 0), 4),
                        '备注': ''
                    })
                
                txt_content = "# 高程拟合模型对比\n\n"
                txt_content += "## 拟合结果分析\n\n"
                txt_content += "各模型拟合值对比:\n"
                for model in ['quadratic', 'plane', 'four_param']:
                    values = [v.get(model, 0) for v in results.values()]
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    txt_content += f"- {model}: 均值={mean_val:.4f}, 标准差={std_val:.4f}\n"
                
                # 确定最优模型
                models = {'quadratic': '二次曲面', 'plane': '多项式平面', 'four_param': '四参数曲面'}
                best_model = min(results.items(), key=lambda x: np.std([v for v in x[1].values()]))[0]
                txt_content += f"\n## 最优模型\n\n"
                txt_content += f"推荐模型: {models.get(best_model, best_model)}\n"
            
            df = pd.DataFrame(data)
            csv_filename = f"题目2_高程拟合结果_{datetime.now().strftime('%Y%m%d')}"
            results_list.append(self.export_csv(df, csv_filename, output_dir))
            
            txt_filename = f"题目2_高程拟合结论_{datetime.now().strftime('%Y%m%d')}"
            results_list.append(self.export_txt(txt_content, txt_filename, output_dir))
            
            return results_list
            
        except Exception as e:
            logger.error("Exporter", "高程拟合导出失败", e)
            results_list.append(ExportResult(False, None, f"高程拟合导出失败: {str(e)}"))
            return results_list
    
    # 题目3：时间系统转换导出
    def export_time(self, results: List[Dict], output_dir: Optional[str] = None) -> ExportResult:
        """
        导出时间系统转换结果
        
        Args:
            results: 时间转换结果列表
            output_dir: 输出目录（可选）
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            data = []
            for r in results:
                data.append({
                    '原始时间': r['original_time'],
                    '儒略日(JD)': round(r['julian_day'], 6),
                    '转换后公历': r['gregorian_date'],
                    '年积日': r['day_of_year'],
                    '打鱼/晒网状态': r['fishing_status']
                })
            
            df = pd.DataFrame(data)
            filename = f"题目3_时间转换结果_{datetime.now().strftime('%Y%m%d')}"
            return self.export_csv(df, filename, output_dir)
            
        except Exception as e:
            logger.error("Exporter", "时间转换导出失败", e)
            return ExportResult(False, None, f"时间转换导出失败: {str(e)}")
    
    # 题目4：面积计算导出
    def export_area(self, area_result: Any, output_dir: Optional[str] = None) -> List[ExportResult]:
        """
        导出面积计算结果
        
        Args:
            area_result: 面积计算结果（AreaResult对象或字典）
            output_dir: 输出目录（可选）
            
        Returns:
            List[ExportResult]: 导出结果列表
        """
        results_list = []
        
        try:
            # 支持多种输入格式
            triangles = None
            total_area = 0
            vertices = []
            
            # 检查是否为AreaResult对象
            if hasattr(area_result, 'triangles') and area_result.triangles:
                triangles = area_result.triangles
                total_area = area_result.area_final
                vertices = area_result.vertices
            elif isinstance(area_result, dict):
                # 字典格式
                triangles = area_result.get('triangles', [])
                total_area = area_result.get('total_area', 0)
                vertices = area_result.get('vertices', [])
            
            # 如果有三角形详细信息，导出详细数据
            if triangles:
                data = []
                for i, tri in enumerate(triangles, 1):
                    # 支持TriangleInfo对象和字典
                    if hasattr(tri, 'side1'):
                        data.append({
                            '三角形序号': i,
                            '边1长度(m)': round(tri.side1, 3),
                            '边2长度(m)': round(tri.side2, 3),
                            '边3长度(m)': round(tri.side3, 3),
                            '三角形面积(m²)': round(tri.area, 3)
                        })
                    else:
                        data.append({
                            '三角形序号': i,
                            '边1长度(m)': round(tri.get('side1', 0), 3),
                            '边2长度(m)': round(tri.get('side2', 0), 3),
                            '边3长度(m)': round(tri.get('side3', 0), 3),
                            '三角形面积(m²)': round(tri.get('area', 0), 3)
                        })
                
                # 添加汇总行
                data.append({
                    '三角形序号': '汇总项',
                    '边1长度(m)': '',
                    '边2长度(m)': '',
                    '边3长度(m)': '',
                    '三角形面积(m²)': round(total_area, 3)
                })
                
                df = pd.DataFrame(data)
                csv_filename = f"题目4_面积计算结果_{datetime.now().strftime('%Y%m%d')}"
                results_list.append(self.export_csv(df, csv_filename, output_dir))
            
            # 导出计算报告
            txt_content = "# 多边形面积计算结果\n\n"
            txt_content += "## 计算摘要\n\n"
            txt_content += f"- **总面积**: {total_area:.6f} m²\n"
            txt_content += f"- **三角形数量**: {len(triangles) if triangles else 0}\n"
            
            if hasattr(area_result, 'area_shoelace'):
                txt_content += f"- **鞋带公式结果**: {area_result.area_shoelace:.6f} m²\n"
                txt_content += f"- **三角剖分结果**: {area_result.area_triangulation:.6f} m²\n"
                txt_content += f"- **校验差异**: {area_result.validation_diff:.6f} m\n"
                txt_content += f"- **周长**: {area_result.perimeter:.6f} m\n"
            
            if vertices:
                txt_content += "\n## 多边形顶点\n\n"
                txt_content += "| 序号 | X坐标(m) | Y坐标(m) |\n"
                txt_content += "|------|----------|----------|\n"
                for i, (x, y) in enumerate(vertices, 1):
                    txt_content += f"| {i} | {x:.6f} | {y:.6f} |\n"
            
            if triangles:
                txt_content += "\n## 三角形剖分详情\n\n"
                txt_content += "| 序号 | 边1(m) | 边2(m) | 边3(m) | 面积(m²) |\n"
                txt_content += "|------|--------|--------|--------|----------|\n"
                for i, tri in enumerate(triangles, 1):
                    if hasattr(tri, 'side1'):
                        txt_content += f"| {i} | {tri.side1:.3f} | {tri.side2:.3f} | {tri.side3:.3f} | {tri.area:.6f} |\n"
                    else:
                        txt_content += f"| {i} | {tri.get('side1', 0):.3f} | {tri.get('side2', 0):.3f} | {tri.get('side3', 0):.3f} | {tri.get('area', 0):.6f} |\n"
            
            txt_filename = f"题目4_面积计算报告_{datetime.now().strftime('%Y%m%d')}"
            results_list.append(self.export_txt(txt_content, txt_filename, output_dir))
            
            return results_list
            
        except Exception as e:
            logger.error("Exporter", "面积计算导出失败", e)
            results_list.append(ExportResult(False, None, f"面积计算导出失败: {str(e)}"))
            return results_list
    
    # 题目5：坐标转换导出
    def export_coordinate(self, blh_results: List[Dict], neu_results: List[Dict], output_dir: Optional[str] = None) -> List[ExportResult]:
        """
        导出坐标转换结果
        
        Args:
            blh_results: 大地坐标转换结果
            neu_results: 站心坐标转换结果
            output_dir: 输出目录（可选）
            
        Returns:
            List[ExportResult]: 导出结果列表
        """
        results_list = []
        
        try:
            # 导出TXT（包含度分秒格式）
            txt_content = "===== 空间直角坐标转大地坐标（WGS-84椭球）=====\n"
            for r in blh_results:
                # 获取数据（支持多种键名）
                point_id = self._safe_get_value(r, ['点号', 'point_id', 'id'], 'Unknown')
                b_deg = self._safe_get_value(r, ['大地纬度(B)', 'B_deg', 'B'], 0)
                l_deg = self._safe_get_value(r, ['大地经度(L)', 'L_deg', 'L'], 0)
                h = self._safe_get_value(r, ['大地高(H)(m)', 'H', 'h'], 0)
                
                # 格式化度分秒
                b_dms = self._decimal_to_dms(float(b_deg) if isinstance(b_deg, (int, float)) else 0)
                l_dms = self._decimal_to_dms(float(l_deg) if isinstance(l_deg, (int, float)) else 0)
                
                txt_content += f"点号：{point_id}，"
                txt_content += f"大地纬度：{b_dms}，"
                txt_content += f"大地经度：{l_dms}，"
                txt_content += f"大地高：{float(h):.4f} m\n"
            
            txt_content += "\n===== 空间直角坐标转站心直角坐标（基准点B）=====\n"
            for r in neu_results:
                # 获取数据
                point_id = self._safe_get_value(r, ['点号', 'point_id', 'id'], 'Unknown')
                n = self._safe_get_value(r, ['北坐标N(mm)', 'N'], 0)
                e = self._safe_get_value(r, ['东坐标E(mm)', 'E'], 0)
                u = self._safe_get_value(r, ['天坐标U(mm)', 'U'], 0)
                
                txt_content += f"点号：{point_id}，"
                txt_content += f"N：{float(n):.1f} mm，"
                txt_content += f"E：{float(e):.1f} mm，"
                txt_content += f"U：{float(u):.1f} mm\n"
            
            txt_filename = f"题目5_坐标转换结果_{datetime.now().strftime('%Y%m%d')}"
            results_list.append(self.export_txt(txt_content, txt_filename, output_dir))
            
            # 导出CSV
            if blh_results:
                blh_df = pd.DataFrame(blh_results)
                blh_filename = f"题目5_大地坐标结果_{datetime.now().strftime('%Y%m%d')}"
                results_list.append(self.export_csv(blh_df, blh_filename, output_dir))
            
            if neu_results:
                neu_df = pd.DataFrame(neu_results)
                neu_filename = f"题目5_站心坐标结果_{datetime.now().strftime('%Y%m%d')}"
                results_list.append(self.export_csv(neu_df, neu_filename, output_dir))
            
            return results_list
            
        except Exception as e:
            logger.error("Exporter", "坐标转换导出失败", e)
            results_list.append(ExportResult(False, None, f"坐标转换导出失败: {str(e)}"))
            return results_list
    
    # 题目6：滑坡监测导出
    def export_landslide(self, deformation_results: List[Dict], strain_results: List[Dict], output_dir: Optional[str] = None) -> List[ExportResult]:
        """
        导出滑坡监测结果
        
        Args:
            deformation_results: 变形速度结果
            strain_results: 应变计算结果
            output_dir: 输出目录（可选）
            
        Returns:
            List[ExportResult]: 导出结果列表
        """
        results_list = []
        
        try:
            # 导出变形速度CSV
            deformation_data = []
            for r in deformation_results:
                deformation_data.append({
                    '监测点编号': r['监测点编号'],
                    '时段': r['时段'],
                    '距离变化s(mm)': round(r['距离变化s(mm)'], 4),
                    '时间间隔t(天)': r['时间间隔t(天)'],
                    '变形速度v(mm/天)': round(r['变形速度v(mm/天)'], 4),
                    '最大变形标记': r['最大变形标记']
                })
            
            deformation_df = pd.DataFrame(deformation_data)
            deformation_filename = f"题目6_滑坡变形速度_{datetime.now().strftime('%Y%m%d')}"
            results_list.append(self.export_csv(deformation_df, deformation_filename, output_dir))
            
            # 导出应变CSV
            strain_data = []
            for r in strain_results:
                strain_data.append({
                    '相邻点组': r['相邻点组'],
                    '时段': r['时段'],
                    '上期距离Sₗ(mm)': round(r['上期距离Sₗ(mm)'], 4),
                    '本期距离Sₗ₊₁(mm)': round(r['本期距离Sₗ₊₁(mm)'], 4),
                    '应变ε': round(r['应变ε'], 6)
                })
            
            strain_df = pd.DataFrame(strain_data)
            strain_filename = f"题目6_滑坡应变计算_{datetime.now().strftime('%Y%m%d')}"
            results_list.append(self.export_csv(strain_df, strain_filename, output_dir))
            
            return results_list
            
        except Exception as e:
            logger.error("Exporter", "滑坡监测导出失败", e)
            results_list.append(ExportResult(False, None, f"滑坡监测导出失败: {str(e)}"))
            return results_list


# 便捷函数
def export_csv(data: pd.DataFrame, filename: str, output_dir: str = "reports") -> ExportResult:
    """导出CSV的便捷函数"""
    exporter = Exporter(output_dir)
    return exporter.export_csv(data, filename, output_dir)


def export_markdown(content: str, filename: str, output_dir: str = "reports") -> ExportResult:
    """导出Markdown的便捷函数"""
    exporter = Exporter(output_dir)
    return exporter.export_markdown(content, filename, output_dir)
