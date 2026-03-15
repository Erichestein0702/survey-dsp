"""
多边形面积计算核心模块
提供鞋带公式、三角剖分等算法，支持双重校验
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from common.logger import get_logger
from common.parser import DataParser, ParseResult
from common.exporter import Exporter
from .graham_scan import GrahamScan

logger = get_logger("AreaCalculator")


@dataclass
class TriangleInfo:
    """三角形详细信息"""
    vertex1: Tuple[float, float]  # 顶点1坐标
    vertex2: Tuple[float, float]  # 顶点2坐标
    vertex3: Tuple[float, float]  # 顶点3坐标
    side1: float  # 边1长度（顶点1到顶点2）
    side2: float  # 边2长度（顶点2到顶点3）
    side3: float  # 边3长度（顶点3到顶点1）
    area: float   # 三角形面积


@dataclass
class AreaResult:
    """
    面积计算结果
    
    Attributes:
        area_shoelace: 鞋带公式计算的面积
        area_triangulation: 三角剖分计算的面积
        area_final: 最终采用的面积值
        vertices: 多边形顶点列表
        perimeter: 周长
        is_valid: 计算是否有效
        validation_passed: 双重校验是否通过
        validation_diff: 两种方法差异
        warning_message: 警告信息
        triangles: 三角形详细信息列表（用于导出）
    """
    area_shoelace: float
    area_triangulation: float
    area_final: float
    vertices: List[Tuple[float, float]]
    perimeter: float
    is_valid: bool
    validation_passed: bool
    validation_diff: float
    warning_message: Optional[str] = None
    triangles: Optional[List[TriangleInfo]] = None


class AreaCalculator:
    """
    多边形面积计算器
    支持鞋带公式和三角剖分双重校验
    """
    
    # 校验阈值
    VALIDATION_THRESHOLD = 1e-6
    
    def __init__(self):
        """初始化面积计算器"""
        self.graham_scan = GrahamScan()
        self.parser = DataParser()
        self.exporter = Exporter()
        logger.info("面积计算器初始化完成")
    
    def calculate(self, points: List[Tuple[float, float]], 
                 sort_points: bool = True) -> AreaResult:
        """
        计算多边形面积
        
        Args:
            points: 多边形顶点列表 [(x1, y1), (x2, y2), ...]
            sort_points: 是否对点进行排序（默认True）
            
        Returns:
            AreaResult: 面积计算结果
        """
        logger.log_algorithm_start("多边形面积计算", {
            '顶点数': len(points),
            '排序': sort_points
        })
        
        # 数据校验
        if len(points) < 3:
            raise ValueError(f"多边形顶点数不足: {len(points)} < 3")
        
        # 点排序（如果需要）
        if sort_points:
            sorted_points = self.graham_scan.sort_points(points)
            logger.debug(f"点集已排序")
        else:
            sorted_points = points
        
        # 检查是否为简单多边形
        if not self.graham_scan.is_simple_polygon(sorted_points):
            logger.warning("AreaCalculator 多边形边存在交叉，可能不是简单多边形")
        
        # 方法1：鞋带公式
        area_shoelace = self._shoelace_formula(sorted_points)
        logger.debug(f"鞋带公式面积: {area_shoelace:.6f}")
        
        # 方法2：三角剖分（同时获取三角形详细信息）
        area_triangulation, triangles = self._triangulation(sorted_points, return_triangles=True)
        logger.debug(f"三角剖分面积: {area_triangulation:.6f}")
        
        # 双重校验
        validation_passed, validation_diff, warning = self._validate_results(
            area_shoelace, area_triangulation
        )
        
        # 计算周长
        perimeter = self._calculate_perimeter(sorted_points)
        
        # 确定最终面积
        if validation_passed:
            area_final = area_shoelace  # 使用鞋带公式的结果
            is_valid = True
        else:
            area_final = 0.0
            is_valid = False
        
        logger.log_algorithm_end(
            "多边形面积计算",
            f"面积={area_final:.6f}, 校验={'通过' if validation_passed else '失败'}"
        )
        
        return AreaResult(
            area_shoelace=area_shoelace,
            area_triangulation=area_triangulation,
            area_final=area_final,
            vertices=sorted_points,
            perimeter=perimeter,
            is_valid=is_valid,
            validation_passed=validation_passed,
            validation_diff=validation_diff,
            warning_message=warning,
            triangles=triangles
        )
    
    def _shoelace_formula(self, points: List[Tuple[float, float]]) -> float:
        """
        鞋带公式计算多边形面积
        
        公式：Area = 0.5 * |sum(x_i * y_{i+1} - x_{i+1} * y_i)|
        
        Args:
            points: 多边形顶点列表（逆时针或顺时针顺序）
            
        Returns:
            多边形面积
        """
        n = len(points)
        area = 0.0
        
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        
        return abs(area) / 2.0
    
    def _triangulation(self, points: List[Tuple[float, float]], 
                       return_triangles: bool = False) -> Union[float, Tuple[float, List[TriangleInfo]]]:
        """
        三角剖分法计算多边形面积
        
        以第一个点为公共顶点，将多边形剖分为三角形
        
        Args:
            points: 多边形顶点列表
            return_triangles: 是否返回三角形详细信息
            
        Returns:
            多边形面积，如果return_triangles=True则返回(面积, 三角形列表)
        """
        n = len(points)
        if n < 3:
            if return_triangles:
                return 0.0, []
            return 0.0
        
        # 使用重心作为公共顶点更稳定
        centroid_x = sum(p[0] for p in points) / n
        centroid_y = sum(p[1] for p in points) / n
        centroid = (centroid_x, centroid_y)
        
        total_area = 0.0
        triangles = []
        
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            
            p1 = centroid
            p2 = (x1, y1)
            p3 = (x2, y2)
            
            # 计算三角形面积
            triangle_area = self._triangle_area(p1, p2, p3)
            total_area += triangle_area
            
            # 如果需要返回三角形详细信息
            if return_triangles:
                # 计算三边长度
                side1 = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                side2 = np.sqrt((p3[0] - p2[0])**2 + (p3[1] - p2[1])**2)
                side3 = np.sqrt((p1[0] - p3[0])**2 + (p1[1] - p3[1])**2)
                
                triangles.append(TriangleInfo(
                    vertex1=p1,
                    vertex2=p2,
                    vertex3=p3,
                    side1=side1,
                    side2=side2,
                    side3=side3,
                    area=triangle_area
                ))
        
        if return_triangles:
            return total_area, triangles
        return total_area
    
    def _triangle_area(self, p1: Tuple[float, float], 
                      p2: Tuple[float, float], 
                      p3: Tuple[float, float]) -> float:
        """
        计算三角形面积（使用叉积公式）
        
        Args:
            p1, p2, p3: 三角形三个顶点
            
        Returns:
            三角形面积
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2.0
    
    def _validate_results(self, area1: float, area2: float) -> Tuple[bool, float, Optional[str]]:
        """
        校验两种方法的计算结果
        
        Args:
            area1: 鞋带公式计算的面积
            area2: 三角剖分计算的面积
            
        Returns:
            (是否通过校验, 差异值, 警告信息)
        """
        if area1 == 0 and area2 == 0:
            return True, 0.0, None
        
        # 计算相对差异
        max_area = max(area1, area2)
        diff = abs(area1 - area2)
        relative_diff = diff / max_area if max_area > 0 else 0.0
        
        if relative_diff > self.VALIDATION_THRESHOLD:
            warning = (
                f"图形拓扑异常：两种算法结果差异过大 "
                f"(鞋带公式={area1:.6f}, 三角剖分={area2:.6f}, "
                f"相对差异={relative_diff:.2e})"
            )
            logger.log_warning("AreaCalculator", warning)
            return False, relative_diff, warning
        
        return True, relative_diff, None
    
    def _calculate_perimeter(self, points: List[Tuple[float, float]]) -> float:
        """
        计算多边形周长
        
        Args:
            points: 多边形顶点列表
            
        Returns:
            周长
        """
        n = len(points)
        perimeter = 0.0
        
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            perimeter += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        return perimeter
    
    def load_data(self, file_path: str) -> List[Tuple[float, float]]:
        """
        从文件加载多边形顶点数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            顶点坐标列表
        """
        parse_result = self.parser.parse_file(file_path)
        
        if 'X' not in parse_result.data.columns:
            raise ValueError("数据缺少X坐标列")
        if 'Y' not in parse_result.data.columns:
            raise ValueError("数据缺少Y坐标列")
        
        X = parse_result.data['X'].values
        Y = parse_result.data['Y'].values
        
        points = list(zip(X, Y))
        logger.info(f"从文件加载了 {len(points)} 个顶点")
        return points
    
    def generate_report(self, result: AreaResult) -> str:
        """
        生成Markdown格式报告
        
        Args:
            result: 面积计算结果
            
        Returns:
            Markdown格式报告
        """
        report = self.exporter.create_report_header(
            "多边形面积计算报告", "模块4 - 多边形面积计算"
        )
        
        # 计算摘要
        report += "## 计算摘要\n\n"
        report += f"| 项目 | 数值 |\n"
        report += f"|------|------|\n"
        report += f"| 顶点数 | {len(result.vertices)} |\n"
        report += f"| 周长 | {result.perimeter:.6f} m |\n"
        report += f"| 鞋带公式面积 | {result.area_shoelace:.6f} m² |\n"
        report += f"| 三角剖分面积 | {result.area_triangulation:.6f} m² |\n"
        report += f"| 最终面积 | {result.area_final:.6f} m² |\n"
        report += f"| 双重校验 | {'通过' if result.validation_passed else '失败'} |\n"
        report += f"| 差异 | {result.validation_diff:.2e} |\n"
        report += "\n"
        
        # 警告信息
        if result.warning_message:
            report += "## 警告\n\n"
            report += f"> ⚠️ {result.warning_message}\n\n"
        
        # 顶点坐标表
        report += "## 顶点坐标\n\n"
        report += "| 序号 | X (m) | Y (m) |\n"
        report += "|------|-------|-------|\n"
        for i, (x, y) in enumerate(result.vertices):
            report += f"| {i+1} | {x:.6f} | {y:.6f} |\n"
        report += "\n"
        
        return report
