"""
海伦公式面积计算模块
根据指导书要求，使用海伦公式计算6个固定三角形的面积
"""

import math
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class HeronTriangle:
    """海伦公式三角形信息"""
    index: int              # 三角形序号
    vertex_a: str           # 顶点A名称
    vertex_b: str           # 顶点B名称  
    vertex_c: str           # 顶点C名称
    side_a: float           # 边a长度（对A）
    side_b: float           # 边b长度（对B）
    side_c: float           # 边c长度（对C）
    area: float             # 三角形面积


@dataclass
class HeronAreaResult:
    """海伦公式面积计算结果"""
    triangles: List[HeronTriangle]  # 6个三角形信息
    total_area: float               # 总面积
    vertex_count: int               # 顶点数


class HeronCalculator:
    """
    海伦公式面积计算器
    
    根据指导书要求，将多边形分割为6个固定三角形，
    使用海伦公式计算每个三角形的面积。
    
    三角形划分规则（以8个顶点的多边形为例）：
    - 三角形1: A-B-C
    - 三角形2: A-C-D
    - 三角形3: A-D-E
    - 三角形4: A-E-F
    - 三角形5: A-F-G
    - 三角形6: A-G-H
    
    即以第一个顶点A为公共顶点，依次与其他连续顶点组成三角形。
    """
    
    @staticmethod
    def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        计算两点之间的距离
        
        Args:
            p1: 点1坐标 (x1, y1)
            p2: 点2坐标 (x2, y2)
            
        Returns:
            两点间距离
        """
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    @staticmethod
    def heron_formula(a: float, b: float, c: float) -> float:
        """
        海伦公式计算三角形面积
        
        公式：
        s = (a + b + c) / 2  (半周长)
        Area = sqrt(s * (s-a) * (s-b) * (s-c))
        
        Args:
            a: 边a长度
            b: 边b长度
            c: 边c长度
            
        Returns:
            三角形面积
        """
        # 检查是否能构成三角形
        if a + b <= c or a + c <= b or b + c <= a:
            return 0.0
        
        s = (a + b + c) / 2.0
        area_squared = s * (s - a) * (s - b) * (s - c)
        
        if area_squared <= 0:
            return 0.0
        
        return math.sqrt(area_squared)
    
    @staticmethod
    def calculate_from_vertices(
        vertices: List[Tuple[float, float]],
        vertex_names: List[str] = None
    ) -> HeronAreaResult:
        """
        从顶点坐标计算6个三角形的面积
        
        Args:
            vertices: 多边形顶点坐标列表 [(x1,y1), (x2,y2), ...]
            vertex_names: 顶点名称列表，默认为 [A, B, C, D, E, F, G, H]
            
        Returns:
            HeronAreaResult: 计算结果
        """
        n = len(vertices)
        
        if n < 3:
            raise ValueError(f"顶点数不足: {n} < 3")
        
        # 默认顶点名称
        if vertex_names is None:
            vertex_names = [chr(ord('A') + i) for i in range(n)]
        
        triangles = []
        total_area = 0.0
        
        # 以第一个顶点为公共顶点，划分三角形
        # 三角形1: V0-V1-V2
        # 三角形2: V0-V2-V3
        # 三角形3: V0-V3-V4
        # ...以此类推
        
        triangle_count = 0
        for i in range(1, n - 1):
            triangle_count += 1
            if triangle_count > 6:
                break  # 最多6个三角形
            
            # 当前三角形的三个顶点
            v0 = vertices[0]
            v1 = vertices[i]
            v2 = vertices[i + 1]
            
            name0 = vertex_names[0]
            name1 = vertex_names[i]
            name2 = vertex_names[i + 1]
            
            # 计算三边长度
            # side_a 对顶点A (v0)
            # side_b 对顶点B (v1)
            # side_c 对顶点C (v2)
            side_a = HeronCalculator.calculate_distance(v1, v2)  # 对v0的边
            side_b = HeronCalculator.calculate_distance(v0, v2)  # 对v1的边
            side_c = HeronCalculator.calculate_distance(v0, v1)  # 对v2的边
            
            # 使用海伦公式计算面积
            area = HeronCalculator.heron_formula(side_a, side_b, side_c)
            
            triangle = HeronTriangle(
                index=triangle_count,
                vertex_a=name0,
                vertex_b=name1,
                vertex_c=name2,
                side_a=side_a,
                side_b=side_b,
                side_c=side_c,
                area=area
            )
            
            triangles.append(triangle)
            total_area += area
        
        return HeronAreaResult(
            triangles=triangles,
            total_area=total_area,
            vertex_count=n
        )
    
    @staticmethod
    def format_output(result: HeronAreaResult) -> str:
        """
        按指导书要求格式化输出
        
        输出格式：
        三角形1: 边1=xx 边2=xx 边3=xx 面积=xx
        三角形2: ...
        ...
        总面积: xx
        
        Args:
            result: 计算结果
            
        Returns:
            格式化字符串
        """
        lines = []
        lines.append("=" * 60)
        lines.append("海伦公式面积计算结果")
        lines.append("=" * 60)
        lines.append("")
        
        for tri in result.triangles:
            lines.append(
                f"三角形{tri.index}: "
                f"边1={tri.side_a:.4f}m "
                f"边2={tri.side_b:.4f}m "
                f"边3={tri.side_c:.4f}m "
                f"面积={tri.area:.4f}m²"
            )
        
        lines.append("")
        lines.append(f"总面积: {result.total_area:.4f} m²")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    @staticmethod
    def calculate_from_file(file_path: str) -> Tuple[HeronAreaResult, List[str]]:
        """
        从文件读取顶点并计算面积
        
        文件格式：点号 X Y
        
        Args:
            file_path: 文件路径
            
        Returns:
            (计算结果, 错误信息列表)
        """
        vertices = []
        vertex_names = []
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    lines = f.readlines()
            except Exception as e:
                errors.append(f"无法读取文件: {str(e)}")
                return None, errors
        
        line_num = 0
        for line in lines:
            line_num += 1
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            
            parts = line.split()
            if len(parts) < 3:
                errors.append(f"第{line_num}行格式错误，需要: 点号 X Y")
                continue
            
            try:
                name = parts[0]
                x = float(parts[1])
                y = float(parts[2])
                
                vertex_names.append(name)
                vertices.append((x, y))
            except ValueError as e:
                errors.append(f"第{line_num}行数值解析错误: {str(e)}")
                continue
        
        if len(vertices) < 3:
            errors.append(f"顶点数不足: {len(vertices)} < 3")
            return None, errors
        
        result = HeronCalculator.calculate_from_vertices(vertices, vertex_names)
        return result, errors


# 便捷函数
def calculate_heron_area(
    vertices: List[Tuple[float, float]],
    vertex_names: List[str] = None
) -> HeronAreaResult:
    """便捷函数：计算海伦公式面积"""
    return HeronCalculator.calculate_from_vertices(vertices, vertex_names)
